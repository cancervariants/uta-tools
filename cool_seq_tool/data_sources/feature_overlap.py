"""Module for getting feature (gene/exon) overlap"""
import re
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from cool_seq_tool.data_sources import SeqRepoAccess
from cool_seq_tool.paths import MANE_REFSEQ_GFF_PATH
from cool_seq_tool.schemas import ResidueMode


class FeatureOverlapError(Exception):
    """Custom exception for the Feature Overlap class"""


class FeatureOverlap:
    """The class for getting feature overlap"""

    def __init__(
        self,
        seqrepo_access: SeqRepoAccess,
        mane_refseq_gff_path: Path = MANE_REFSEQ_GFF_PATH,
    ) -> None:
        """Initialize the FeatureOverlap class. Will load RefSeq data and store as df.

        :param seqrepo_access: Client for accessing SeqRepo data
        :param mane_refseq_gff_path: Path to the MANE RefSeq GFF file
        """
        self.seqrepo_access = seqrepo_access
        self.mane_refseq_gff_path = mane_refseq_gff_path
        self.df = self._load_mane_refseq_gff_data()

    def _load_mane_refseq_gff_data(self) -> pd.core.frame.DataFrame:
        """Load MANE RefSeq GFF data file into DataFrame.

        :return: DataFrame containing MANE RefSeq GFF data for CDS. Columsn include
            `type`, `chromosome` (chromosome without 'chr' prefix), `cds_start`,
            `cds_stop`, `info_name` (name of record), and `gene`
        """
        df = pd.read_csv(
            self.mane_refseq_gff_path,
            sep="\t",
            header=None,
            skiprows=9,
            usecols=[0, 2, 3, 4, 8],
        )
        df.columns = ["chromosome", "type", "cds_start", "cds_stop", "info"]

        # Restrict to only feature of interest: CDS (which has gene info)
        df = df[df["type"] == "CDS"].copy()

        # Get name from the info field
        df["info_name"] = df["info"].apply(
            lambda info: re.findall("Name=([^;]+)", info)[0]
        )

        # Get gene from the info field
        df["gene"] = df["info"].apply(lambda info: re.findall("gene=([^;]+)", info)[0])

        # Get chromosome names without prefix and without suffix for alternate
        # transcripts
        df["chromosome"] = df["chromosome"].apply(
            lambda chromosome: chromosome.strip("chr").split("_")[0]
        )
        df["chromosome"] = df["chromosome"].astype(str)

        # Convert start and stop to ints
        df["cds_start"] = df["cds_start"].astype(int)
        df["cds_stop"] = df["cds_stop"].astype(int)

        # Only retain certain columns
        df = df[
            ["type", "chromosome", "cds_start", "cds_stop", "info_name", "gene"]
        ]

        return df

    def _get_chr_from_alt_ac(self, identifier: str) -> str:
        """Get chromosome given genomic identifier

        :param identifier: Genomic identifier on GRCh38 assembly
        :raises FeatureOverlapError: If unable to find associated GRCh38 chromosome
        :return: Chromosome. 1..22, X, Y. No 'chr' prefix.
        """
        aliases, error_msg = self.seqrepo_access.translate_identifier(
            identifier, "GRCh38"
        )

        if error_msg:
            raise FeatureOverlapError(str(error_msg))

        if not aliases:
            raise FeatureOverlapError(
                f"Unable to find GRCh38 aliases for: {identifier}"
            )

        chr_pattern = r"^GRCh38:(?P<chromosome>X|Y|([1-9]|1[0-9]|2[0-2]))$"
        for a in aliases:
            chr_match = re.match(chr_pattern, a)
            if chr_match:
                break

        if not chr_match:
            raise FeatureOverlapError(
                f"Unable to find GRCh38 chromosome for: {identifier}"
            )

        chr_groupdict = chr_match.groupdict()
        return chr_groupdict["chromosome"]

    def get_grch38_cds_overlap(
        self,
        start: int,
        end: int,
        chromosome: Optional[str] = None,
        identifier: Optional[str] = None,
        residue_mode: ResidueMode = ResidueMode.RESIDUE,
    ) -> Optional[Dict]:
        """Get feature overlap for GRCh38 genomic data

        :param start: GRCh38 start position
        :param end: GRCh38 end position
        :param chromosome: Chromosome. 1..22, X, or Y. If not provided, must provide
            `identifier`. If both `chromosome` and `identifier` are provided,
            `chromosome` will be used.
        :param identifier: Genomic identifier on GRCh38 assembly. If not provided,
            must identifier `chromosome`. If both `chromosome` and `identifier` are
            provided, `chromosome` will be used.
        :param residue_mode: Residue mode for `start` and `end`
        :raise FeatureOverlapError: If missing required fields
        :return: Feature overlap dictionary where the key is the gene name and the value
            is the list of CDS overlap (cds_start, cds_stop, overlap_start,
            overlap_stop). Will return residue coordinates.
        """
        if chromosome:
            if not re.match(r"^X|Y|([1-9]|1[0-9]|2[0-2])$", chromosome):
                raise FeatureOverlapError("`chromosome` must be 1, ..., 22, X, or Y")
        else:
            if identifier:
                chromosome = self._get_chr_from_alt_ac(identifier)
            else:
                raise FeatureOverlapError(
                    "Must provide either `chromosome` or `identifier`"
                )

        # GFF is 1-based, so we need to convert inter-residue to residue
        # RESIDUE           |   | 1 |   | 2 |   | 3 |   |
        # INTER_RESIDUE     | 0 |   | 1 |   | 2 |   | 3 |
        if residue_mode == ResidueMode.INTER_RESIDUE:
            if start != end:
                start += 1
            else:
                end += 1

        # Get feature dataframe
        feature_df = self.df[
            (self.df["chromosome"] == chromosome)
            & (self.df["cds_start"] <= end)  # noqa: W503
            & (self.df["cds_stop"] >= start)  # noqa: W503
        ].copy()

        if feature_df.empty:
            return None

        # Add overlap columns
        feature_df["overlap_start"] = feature_df["cds_start"].apply(
            lambda x: x if start <= x else start
        )
        feature_df["overlap_stop"] = feature_df["cds_stop"].apply(
            lambda x: end if end <= x else x
        )

        return (
            feature_df.groupby(["gene"])[
                ["info_name", "cds_start", "cds_stop", "overlap_start", "overlap_stop"]
            ]
            .apply(lambda x: x.set_index("info_name").to_dict(orient="records"))
            .to_dict()
        )
