"""Module for testing seqrepo access class"""

import pytest

from cool_seq_tool.schemas import ResidueMode


def test_get_reference_sequence(test_seqrepo_access):
    """Test that get_reference_sequence method works correctly"""
    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 600, 600)
    assert resp == ("V", None)

    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 600, 601)
    assert resp == ("VK", None)

    resp = test_seqrepo_access.get_reference_sequence(
        "NP_004324.2", 599, 600, residue_mode=ResidueMode.INTER_RESIDUE
    )
    assert resp == ("V", None)

    # Test getting entire sequence
    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2")
    assert len(resp[0]) == 766

    # Test only setting end
    resp = test_seqrepo_access.get_reference_sequence("NP_001341538.1", end=10)
    assert resp == ("MAALSGGGGG", None)

    # Test only setting start
    resp = test_seqrepo_access.get_reference_sequence("NP_001341538.1", start=758)
    assert resp == ("GGYGEFAAFK", None)

    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 601, 600)
    assert resp == (
        "",
        "start (601) cannot be greater than end (600)",
    )

    resp = test_seqrepo_access.get_reference_sequence("NP_0043241311412", 600)
    assert resp == ("", "Accession, NP_0043241311412, not found in SeqRepo")

    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 600, 800)
    assert resp == (
        "",
        "End inter-residue coordinate (800) is out of index on NP_004324.2",
    )

    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 4654645645654, 1)
    assert resp == (
        "",
        "start (4654645645654) cannot be greater than end (1)",
    )

    resp = test_seqrepo_access.get_reference_sequence("NP_004324.2", 600, 4654645645654)
    assert resp == (
        "",
        "End inter-residue coordinate (4654645645654) is out of index on NP_004324.2",
    )


def test_translate_identifier(test_seqrepo_access):
    """Test that translate_identifier method works correctly"""
    expected = (["ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT"], None)
    resp = test_seqrepo_access.translate_identifier(
        "NM_152263.3", target_namespaces="ga4gh"
    )
    assert resp == expected

    resp = test_seqrepo_access.translate_identifier(
        "refseq:NM_152263.3", target_namespaces="ga4gh"
    )
    assert resp == expected

    resp = test_seqrepo_access.translate_identifier("refseq:NM_152263.3")
    assert len(resp[0]) > 0
    assert resp[1] is None
    assert expected[0][0] in resp[0]

    resp = test_seqrepo_access.translate_identifier("GRCh38:2")
    assert len(resp[0]) > 0
    assert resp[1] is None
    assert "refseq:NC_000002.12" in resp[0]

    resp = test_seqrepo_access.translate_identifier("NC_000002.12")
    assert len(resp[0]) > 0
    assert resp[1] is None
    assert "refseq:NC_000002.12" in resp[0]

    resp = test_seqrepo_access.translate_identifier("refseq_152263.3")
    assert resp == (
        [],
        "SeqRepo unable to get translated identifiers for" " refseq_152263.3",
    )


def test_aliases(test_seqrepo_access):
    """Test that aliases method works correctly"""
    expected = (["ga4gh:SQ.ijXOSP3XSsuLWZhXQ7_TJ5JXu4RJO6VT"], None)
    resp = test_seqrepo_access.translate_alias("NM_152263.3")
    assert len(resp[0]) > 0
    assert resp[1] is None
    assert expected[0][0] in resp[0]

    resp = test_seqrepo_access.translate_alias("NC_000002.12")
    assert len(resp[0]) > 0
    assert resp[1] is None
    assert "GRCh38:2" in resp[0]

    resp = test_seqrepo_access.translate_alias("refseq_152263.3")
    assert resp == ([], "SeqRepo could not translate alias refseq_152263.3")

    resp = test_seqrepo_access.translate_alias("GRCh38:2")
    assert resp == ([], "SeqRepo could not translate alias GRCh38:2")


def test_chromosome_to_acs(test_seqrepo_access):
    """Test that chromosome_to_acs method works correctly"""
    resp = test_seqrepo_access.chromosome_to_acs("7")
    assert resp == (["NC_000007.14", "NC_000007.13"], None)

    resp = test_seqrepo_access.chromosome_to_acs("X")
    assert resp == (["NC_000023.11", "NC_000023.10"], None)

    resp = test_seqrepo_access.chromosome_to_acs("Y")
    assert resp == (["NC_000024.10", "NC_000024.9"], None)

    resp = test_seqrepo_access.chromosome_to_acs("117")
    assert resp == (None, "117 is not a valid chromosome")


def test_ac_to_chromosome(test_seqrepo_access):
    """Test that ac_to_chromosome method works correctly"""
    resp = test_seqrepo_access.ac_to_chromosome("NC_000007.13")
    assert resp == ("7", None)

    resp = test_seqrepo_access.ac_to_chromosome("NC_000007.1323")
    assert resp == (None, "Unable to get chromosome for NC_000007.1323")


def test_get_fasta_file(test_seqrepo_access, tmp_path):
    """Test get_fasta_file method"""
    tpm3 = tmp_path / "NM_002529.3.fasta"
    test_seqrepo_access.get_fasta_file("NM_002529.3", tpm3)
    tpm3_expected = """>refseq:NM_002529.3|ga4gh:SQ.RSkww1aYmsMiWbNdNnOTnVDAM3ZWp1uA
TGCAGCTGGGAGCGCACAGACGGCTGCCCCGCCTGAGCGAGGCGGGCGCCGCCGCGATGC
TGCGAGGCGGACGGCGCGGGCAGCTTGGCTGGCACAGCTGGGCTGCGGGGCCGGGCAGCC
TGCTGGCTTGGCTGATACTGGCATCTGCGGGCGCCGCACCCTGCCCCGATGCCTGCTGCC
CCCACGGCTCCTCGGGACTGCGATGCACCCGGGATGGGGCCCTGGATAGCCTCCACCACC
TGCCCGGCGCAGAGAACCTGACTGAGCTCTACATCGAGAACCAGCAGCATCTGCAGCATC
TGGAGCTCCGTGATCTGAGGGGCCTGGGGGAGCTGAGAAACCTCACCATCGTGAAGAGTG
GTCTCCGTTTCGTGGCGCCAGATGCCTTCCATTTCACTCCTCGGCTCAGTCGCCTGAATC
TCTCCTTCAACGCTCTGGAGTCTCTCTCCTGGAAAACTGTGCAGGGCCTCTCCTTACAGG
AACTGGTCCTGTCGGGGAACCCTCTGCACTGTTCTTGTGCCCTGCGCTGGCTACAGCGCT
GGGAGGAGGAGGGACTGGGCGGAGTGCCTGAACAGAAGCTGCAGTGTCATGGGCAAGGGC
CCCTGGCCCACATGCCCAATGCCAGCTGTGGTGTGCCCACGCTGAAGGTCCAGGTGCCCA
ATGCCTCGGTGGATGTGGGGGACGACGTGCTGCTGCGGTGCCAGGTGGAGGGGCGGGGCC
TGGAGCAGGCCGGCTGGATCCTCACAGAGCTGGAGCAGTCAGCCACGGTGATGAAATCTG
GGGGTCTGCCATCCCTGGGGCTGACCCTGGCCAATGTCACCAGTGACCTCAACAGGAAGA
ACGTGACGTGCTGGGCAGAGAACGATGTGGGCCGGGCAGAGGTCTCTGTTCAGGTCAACG
TCTCCTTCCCGGCCAGTGTGCAGCTGCACACGGCGGTGGAGATGCACCACTGGTGCATCC
CCTTCTCTGTGGATGGGCAGCCGGCACCGTCTCTGCGCTGGCTCTTCAATGGCTCCGTGC
TCAATGAGACCAGCTTCATCTTCACTGAGTTCCTGGAGCCGGCAGCCAATGAGACCGTGC
GGCACGGGTGTCTGCGCCTCAACCAGCCCACCCACGTCAACAACGGCAACTACACGCTGC
TGGCTGCCAACCCCTTCGGCCAGGCCTCCGCCTCCATCATGGCTGCCTTCATGGACAACC
CTTTCGAGTTCAACCCCGAGGACCCCATCCCTGTCTCCTTCTCGCCGGTGGACACTAACA
GCACATCTGGAGACCCGGTGGAGAAGAAGGACGAAACACCTTTTGGGGTCTCGGTGGCTG
TGGGCCTGGCCGTCTTTGCCTGCCTCTTCCTTTCTACGCTGCTCCTTGTGCTCAACAAAT
GTGGACGGAGAAACAAGTTTGGGATCAACCGCCCGGCTGTGCTGGCTCCAGAGGATGGGC
TGGCCATGTCCCTGCATTTCATGACATTGGGTGGCAGCTCCCTGTCCCCCACCGAGGGCA
AAGGCTCTGGGCTCCAAGGCCACATCATCGAGAACCCACAATACTTCAGTGATGCCTGTG
TTCACCACATCAAGCGCCGGGACATCGTGCTCAAGTGGGAGCTGGGGGAGGGCGCCTTTG
GGAAGGTCTTCCTTGCTGAGTGCCACAACCTCCTGCCTGAGCAGGACAAGATGCTGGTGG
CTGTCAAGGCACTGAAGGAGGCGTCCGAGAGTGCTCGGCAGGACTTCCAGCGTGAGGCTG
AGCTGCTCACCATGCTGCAGCACCAGCACATCGTGCGCTTCTTCGGCGTCTGCACCGAGG
GCCGCCCCCTGCTCATGGTCTTTGAGTATATGCGGCACGGGGACCTCAACCGCTTCCTCC
GATCCCATGGACCTGATGCCAAGCTGCTGGCTGGTGGGGAGGATGTGGCTCCAGGCCCCC
TGGGTCTGGGGCAGCTGCTGGCCGTGGCTAGCCAGGTCGCTGCGGGGATGGTGTACCTGG
CGGGTCTGCATTTTGTGCACCGGGACCTGGCCACACGCAACTGTCTAGTGGGCCAGGGAC
TGGTGGTCAAGATTGGTGATTTTGGCATGAGCAGGGATATCTACAGCACCGACTATTACC
GTGTGGGAGGCCGCACCATGCTGCCCATTCGCTGGATGCCGCCCGAGAGCATCCTGTACC
GTAAGTTCACCACCGAGAGCGACGTGTGGAGCTTCGGCGTGGTGCTCTGGGAGATCTTCA
CCTACGGCAAGCAGCCCTGGTACCAGCTCTCCAACACGGAGGCAATCGACTGCATCACGC
AGGGACGTGAGTTGGAGCGGCCACGTGCCTGCCCACCAGAGGTCTACGCCATCATGCGGG
GCTGCTGGCAGCGGGAGCCCCAGCAACGCCACAGCATCAAGGATGTGCACGCCCGGCTGC
AAGCCCTGGCCCAGGCACCTCCTGTCTACCTGGATGTCCTGGGCTAGGGGGCCGGCCCAG
GGGCTGGGAGTGGTTAGCCGGAATACTGGGGCCTGCCCTCAGCATCCCCCATAGCTCCCA
GCAGCCCCAGGGTGATCTCAAAGTATCTAATTCACCCTCAGCATGTGGGAAGGGACAGGT
GGGGGCTGGGAGTAGAGGATGTTCCTGCTTCTCTAGGCAAGGTCCCGTCATAGCAATTAT
ATTTATTATCCCTTGAAAAAAAA"""
    assert tpm3.read_text() == tpm3_expected

    limk2 = tmp_path / "ENST00000331728.9.fasta"
    test_seqrepo_access.get_fasta_file("ENST00000331728.9", limk2)
    limk2_expected = """>ensembl:ENST00000331728.9|refseq:NM_005569.4|ga4gh:SQ.7_mlQyDN-uWH0RlxTQFvFEv6ykd2D-xF
GTCTTCCCGCGCCTGAGGCGGCGGCGGCAGGAGCTGAGGGGAGTTGTAGGGAACTGAGGG
GAGCTGCTGTGTCCCCCGCCTCCTCCTCCCCATTTCCGCGCTCCCGGGACCATGTCCGCG
CTGGCGGGTGAAGATGTCTGGAGGTGTCCAGGCTGTGGGGACCACATTGCTCCAAGCCAG
ATATGGTACAGGACTGTCAACGAAACCTGGCACGGCTCTTGCTTCCGGTGTTCAGAATGC
CAGGATTCCCTCACCAACTGGTACTATGAGAAGGATGGGAAGCTCTACTGCCCCAAGGAC
TACTGGGGGAAGTTTGGGGAGTTCTGTCATGGGTGCTCCCTGCTGATGACAGGGCCTTTT
ATGGTGGCTGGGGAGTTCAAGTACCACCCAGAGTGCTTTGCCTGTATGAGCTGCAAGGTG
ATCATTGAGGATGGGGATGCATATGCACTGGTGCAGCATGCCACCCTCTACTGTGGGAAG
TGCCACAATGAGGTGGTGCTGGCACCCATGTTTGAGAGACTCTCCACAGAGTCTGTTCAG
GAGCAGCTGCCCTACTCTGTCACGCTCATCTCCATGCCGGCCACCACTGAAGGCAGGCGG
GGCTTCTCCGTGTCCGTGGAGAGTGCCTGCTCCAACTACGCCACCACTGTGCAAGTGAAA
GAGGTCAACCGGATGCACATCAGTCCCAACAATCGAAACGCCATCCACCCTGGGGACCGC
ATCCTGGAGATCAATGGGACCCCCGTCCGCACACTTCGAGTGGAGGAGGTGGAGGATGCA
ATTAGCCAGACGAGCCAGACACTTCAGCTGTTGATTGAACATGACCCCGTCTCCCAACGC
CTGGACCAGCTGCGGCTGGAGGCCCGGCTCGCTCCTCACATGCAGAATGCCGGACACCCC
CACGCCCTCAGCACCCTGGACACCAAGGAGAATCTGGAGGGGACACTGAGGAGACGTTCC
CTAAGGCGCAGTAACAGTATCTCCAAGTCCCCTGGCCCCAGCTCCCCAAAGGAGCCCCTG
CTGTTCAGCCGTGACATCAGCCGCTCAGAATCCCTTCGTTGTTCCAGCAGCTATTCACAG
CAGATCTTCCGGCCCTGTGACCTAATCCATGGGGAGGTCCTGGGGAAGGGCTTCTTTGGG
CAGGCTATCAAGGTGACACACAAAGCCACGGGCAAAGTGATGGTCATGAAAGAGTTAATT
CGATGTGATGAGGAGACCCAGAAAACTTTTCTGACTGAGGTGAAAGTGATGCGCAGCCTG
GACCACCCCAATGTGCTCAAGTTCATTGGTGTGCTGTACAAGGATAAGAAGCTGAACCTC
CTGACAGAGTACATTGAGGGGGGCACACTGAAGGACTTTCTGCGCAGTATGGATCCGTTC
CCCTGGCAGCAGAAGGTCAGGTTTGCCAAAGGAATCGCCTCCGGAATGGCCTATTTGCAC
TCTATGTGCATCATCCACCGGGATCTGAACTCGCACAACTGCCTCATCAAGTTGGACAAG
ACTGTGGTGGTGGCAGACTTTGGGCTGTCACGGCTCATAGTGGAAGAGAGGAAAAGGGCC
CCCATGGAGAAGGCCACCACCAAGAAACGCACCTTGCGCAAGAACGACCGCAAGAAGCGC
TACACGGTGGTGGGAAACCCCTACTGGATGGCCCCTGAGATGCTGAACGGAAAGAGCTAT
GATGAGACGGTGGATATCTTCTCCTTTGGGATCGTTCTCTGTGAGATCATTGGGCAGGTG
TATGCAGATCCTGACTGCCTTCCCCGAACACTGGACTTTGGCCTCAACGTGAAGCTTTTC
TGGGAGAAGTTTGTTCCCACAGATTGTCCCCCGGCCTTCTTCCCGCTGGCCGCCATCTGC
TGCAGACTGGAGCCTGAGAGCAGACCAGCATTCTCGAAATTGGAGGACTCCTTTGAGGCC
CTCTCCCTGTACCTGGGGGAGCTGGGCATCCCGCTGCCTGCAGAGCTGGAGGAGTTGGAC
CACACTGTGAGCATGCAGTACGGCCTGACCCGGGACTCACCTCCCTAGCCCTGGCCCAGC
CCCCTGCAGGGGGGTGTTCTACAGCCAGCATTGCCCCTCTGTGCCCCATTCCTGCTGTGA
GCAGGGCCGTCCGGGCTTCCTGTGGATTGGCGGAATGTTTAGAAGCAGAACAAGCCATTC
CTATTACCTCCCCAGGAGGCAAGTGGGCGCAGCACCAGGGAAATGTATCTCCACAGGTTC
TGGGGCCTAGTTACTGTCTGTAAATCCAATACTTGCCTGAAAGCTGTGAAGAAGAAAAAA
ACCCCTGGCCTTTGGGCCAGGAGGAATCTGTTACTCGAATCCACCCAGGAACTCCCTGGC
AGTGGATTGTGGGAGGCTCTTGCTTACACTAATCAGCGTGACCTGGACCTGCTGGGCAGG
ATCCCAGGGTGAACCTGCCTGTGAACTCTGAAGTCACTAGTCCAGCTGGGTGCAGGAGGA
CTTCAAGTGTGTGGACGAAAGAAAGACTGATGGCTCAAAGGGTGTGAAAAAGTCAGTGAT
GCTCCCCCTTTCTACTCCAGATCCTGTCCTTCCTGGAGCAAGGTTGAGGGAGTAGGTTTT
GAAGAGTCCCTTAATATGTGGTGGAACAGGCCAGGAGTTAGAGAAAGGGCTGGCTTCTGT
TTACCTGCTCACTGGCTCTAGCCAGCCCAGGGACCACATCAATGTGAGAGGAAGCCTCCA
CCTCATGTTTTCAAACTTAATACTGGAGACTGGCTGAGAACTTACGGACAACATCCTTTC
TGTCTGAAACAAACAGTCACAAGCAAAGGAAGAGGCTGGGGGACTAGAAAGAGGCCCTGC
CCTCTAGAAAGCTCAGATCTTGGCTTCTGTTACTCATACTCGGGTGGGCTCCTTAGTCAG
ATGCCTAAAACATTTTGCCTAAAGCTCGATGGGTTCTGGAGGACAGTGTGGCTTGTCACA
GGCCTAGAGTCTGAGGGAGGGGAGTGGGAGTCTCAGCAATCTCTTGGTCTTGGCTTCATG
GCAACCACTGCTCACCCTTCAACATGCCTGGTTTAGGCAGCAGCTTGGGCTGGGAAGAGG
TGGTGGCAGAGTCTCAAAGCTGAGATGCTGAGAGAGATAGCTCCCTGAGCTGGGCCATCT
GACTTCTACCTCCCATGTTTGCTCTCCCAACTCATTAGCTCCTGGGCAGCATCCTCCTGA
GCCACATGTGCAGGTACTGGAAAACCTCCATCTTGGCTCCCAGAGCTCTAGGAACTCTTC
ATCACAACTAGATTTGCCTCTTCTAAGTGTCTATGAGCTTGCACCATATTTAATAAATTG
GGAATGGGTTTGGGGTATTAATGCAATGTGTGGTGGTTGTATTGGAGCAGGGGGAATTGA
TAAAGGAGAGTGGTTGCTGTTAATATTATCTTATCTATTGGGTGGTATGTGAAATATTGT
ACATAGACCTGATGAGTTGTGGGACCAGATGTCATCTCTGGTCAGAGTTTACTTGCTATA
TAGACTGTACTTATGTGTGAAGTTTGCAAGCTTGCTTTAGGGCTGAGCCCTGGACTCCCA
GCAGCAGCACAGTTCAGCATTGTGTGGCTGGTTGTTTCCTGGCTGTCCCCAGCAAGTGTA
GGAGTGGTGGGCCTGAACTGGGCCATTGATCAGACTAAATAAATTAAGCAGTTAACATAA
CTGGCAA"""
    assert limk2.read_text() == limk2_expected

    limk2_seguid = tmp_path / "SEGUID_LIMK2.fasta"
    test_seqrepo_access.get_fasta_file("ugqOFdlaed2cnxrGa7zngGMrLlY", limk2_seguid)
    limk2_seguid_expected = """>gnl|ID|ugqOFdlaed2cnxrGa7zngGMrLlY|ensembl:ENST00000331728.9|refseq:NM_005569.4|ga4gh:SQ.7_mlQyDN-uWH0RlxTQFvFEv6ykd2D-xF
GTCTTCCCGCGCCTGAGGCGGCGGCGGCAGGAGCTGAGGGGAGTTGTAGGGAACTGAGGG
GAGCTGCTGTGTCCCCCGCCTCCTCCTCCCCATTTCCGCGCTCCCGGGACCATGTCCGCG
CTGGCGGGTGAAGATGTCTGGAGGTGTCCAGGCTGTGGGGACCACATTGCTCCAAGCCAG
ATATGGTACAGGACTGTCAACGAAACCTGGCACGGCTCTTGCTTCCGGTGTTCAGAATGC
CAGGATTCCCTCACCAACTGGTACTATGAGAAGGATGGGAAGCTCTACTGCCCCAAGGAC
TACTGGGGGAAGTTTGGGGAGTTCTGTCATGGGTGCTCCCTGCTGATGACAGGGCCTTTT
ATGGTGGCTGGGGAGTTCAAGTACCACCCAGAGTGCTTTGCCTGTATGAGCTGCAAGGTG
ATCATTGAGGATGGGGATGCATATGCACTGGTGCAGCATGCCACCCTCTACTGTGGGAAG
TGCCACAATGAGGTGGTGCTGGCACCCATGTTTGAGAGACTCTCCACAGAGTCTGTTCAG
GAGCAGCTGCCCTACTCTGTCACGCTCATCTCCATGCCGGCCACCACTGAAGGCAGGCGG
GGCTTCTCCGTGTCCGTGGAGAGTGCCTGCTCCAACTACGCCACCACTGTGCAAGTGAAA
GAGGTCAACCGGATGCACATCAGTCCCAACAATCGAAACGCCATCCACCCTGGGGACCGC
ATCCTGGAGATCAATGGGACCCCCGTCCGCACACTTCGAGTGGAGGAGGTGGAGGATGCA
ATTAGCCAGACGAGCCAGACACTTCAGCTGTTGATTGAACATGACCCCGTCTCCCAACGC
CTGGACCAGCTGCGGCTGGAGGCCCGGCTCGCTCCTCACATGCAGAATGCCGGACACCCC
CACGCCCTCAGCACCCTGGACACCAAGGAGAATCTGGAGGGGACACTGAGGAGACGTTCC
CTAAGGCGCAGTAACAGTATCTCCAAGTCCCCTGGCCCCAGCTCCCCAAAGGAGCCCCTG
CTGTTCAGCCGTGACATCAGCCGCTCAGAATCCCTTCGTTGTTCCAGCAGCTATTCACAG
CAGATCTTCCGGCCCTGTGACCTAATCCATGGGGAGGTCCTGGGGAAGGGCTTCTTTGGG
CAGGCTATCAAGGTGACACACAAAGCCACGGGCAAAGTGATGGTCATGAAAGAGTTAATT
CGATGTGATGAGGAGACCCAGAAAACTTTTCTGACTGAGGTGAAAGTGATGCGCAGCCTG
GACCACCCCAATGTGCTCAAGTTCATTGGTGTGCTGTACAAGGATAAGAAGCTGAACCTC
CTGACAGAGTACATTGAGGGGGGCACACTGAAGGACTTTCTGCGCAGTATGGATCCGTTC
CCCTGGCAGCAGAAGGTCAGGTTTGCCAAAGGAATCGCCTCCGGAATGGCCTATTTGCAC
TCTATGTGCATCATCCACCGGGATCTGAACTCGCACAACTGCCTCATCAAGTTGGACAAG
ACTGTGGTGGTGGCAGACTTTGGGCTGTCACGGCTCATAGTGGAAGAGAGGAAAAGGGCC
CCCATGGAGAAGGCCACCACCAAGAAACGCACCTTGCGCAAGAACGACCGCAAGAAGCGC
TACACGGTGGTGGGAAACCCCTACTGGATGGCCCCTGAGATGCTGAACGGAAAGAGCTAT
GATGAGACGGTGGATATCTTCTCCTTTGGGATCGTTCTCTGTGAGATCATTGGGCAGGTG
TATGCAGATCCTGACTGCCTTCCCCGAACACTGGACTTTGGCCTCAACGTGAAGCTTTTC
TGGGAGAAGTTTGTTCCCACAGATTGTCCCCCGGCCTTCTTCCCGCTGGCCGCCATCTGC
TGCAGACTGGAGCCTGAGAGCAGACCAGCATTCTCGAAATTGGAGGACTCCTTTGAGGCC
CTCTCCCTGTACCTGGGGGAGCTGGGCATCCCGCTGCCTGCAGAGCTGGAGGAGTTGGAC
CACACTGTGAGCATGCAGTACGGCCTGACCCGGGACTCACCTCCCTAGCCCTGGCCCAGC
CCCCTGCAGGGGGGTGTTCTACAGCCAGCATTGCCCCTCTGTGCCCCATTCCTGCTGTGA
GCAGGGCCGTCCGGGCTTCCTGTGGATTGGCGGAATGTTTAGAAGCAGAACAAGCCATTC
CTATTACCTCCCCAGGAGGCAAGTGGGCGCAGCACCAGGGAAATGTATCTCCACAGGTTC
TGGGGCCTAGTTACTGTCTGTAAATCCAATACTTGCCTGAAAGCTGTGAAGAAGAAAAAA
ACCCCTGGCCTTTGGGCCAGGAGGAATCTGTTACTCGAATCCACCCAGGAACTCCCTGGC
AGTGGATTGTGGGAGGCTCTTGCTTACACTAATCAGCGTGACCTGGACCTGCTGGGCAGG
ATCCCAGGGTGAACCTGCCTGTGAACTCTGAAGTCACTAGTCCAGCTGGGTGCAGGAGGA
CTTCAAGTGTGTGGACGAAAGAAAGACTGATGGCTCAAAGGGTGTGAAAAAGTCAGTGAT
GCTCCCCCTTTCTACTCCAGATCCTGTCCTTCCTGGAGCAAGGTTGAGGGAGTAGGTTTT
GAAGAGTCCCTTAATATGTGGTGGAACAGGCCAGGAGTTAGAGAAAGGGCTGGCTTCTGT
TTACCTGCTCACTGGCTCTAGCCAGCCCAGGGACCACATCAATGTGAGAGGAAGCCTCCA
CCTCATGTTTTCAAACTTAATACTGGAGACTGGCTGAGAACTTACGGACAACATCCTTTC
TGTCTGAAACAAACAGTCACAAGCAAAGGAAGAGGCTGGGGGACTAGAAAGAGGCCCTGC
CCTCTAGAAAGCTCAGATCTTGGCTTCTGTTACTCATACTCGGGTGGGCTCCTTAGTCAG
ATGCCTAAAACATTTTGCCTAAAGCTCGATGGGTTCTGGAGGACAGTGTGGCTTGTCACA
GGCCTAGAGTCTGAGGGAGGGGAGTGGGAGTCTCAGCAATCTCTTGGTCTTGGCTTCATG
GCAACCACTGCTCACCCTTCAACATGCCTGGTTTAGGCAGCAGCTTGGGCTGGGAAGAGG
TGGTGGCAGAGTCTCAAAGCTGAGATGCTGAGAGAGATAGCTCCCTGAGCTGGGCCATCT
GACTTCTACCTCCCATGTTTGCTCTCCCAACTCATTAGCTCCTGGGCAGCATCCTCCTGA
GCCACATGTGCAGGTACTGGAAAACCTCCATCTTGGCTCCCAGAGCTCTAGGAACTCTTC
ATCACAACTAGATTTGCCTCTTCTAAGTGTCTATGAGCTTGCACCATATTTAATAAATTG
GGAATGGGTTTGGGGTATTAATGCAATGTGTGGTGGTTGTATTGGAGCAGGGGGAATTGA
TAAAGGAGAGTGGTTGCTGTTAATATTATCTTATCTATTGGGTGGTATGTGAAATATTGT
ACATAGACCTGATGAGTTGTGGGACCAGATGTCATCTCTGGTCAGAGTTTACTTGCTATA
TAGACTGTACTTATGTGTGAAGTTTGCAAGCTTGCTTTAGGGCTGAGCCCTGGACTCCCA
GCAGCAGCACAGTTCAGCATTGTGTGGCTGGTTGTTTCCTGGCTGTCCCCAGCAAGTGTA
GGAGTGGTGGGCCTGAACTGGGCCATTGATCAGACTAAATAAATTAAGCAGTTAACATAA
CTGGCAA"""
    assert limk2_seguid.read_text() == limk2_seguid_expected

    invalid = tmp_path / "invalid.fasta"
    with pytest.raises(KeyError):
        test_seqrepo_access.get_fasta_file("NM_2529.3", invalid)
