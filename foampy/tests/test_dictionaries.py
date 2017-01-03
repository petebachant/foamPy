"""Tests for the `dictionaries` module."""

from __future__ import division, print_function, absolute_import
import foampy
from foampy.dictionaries import *


def test_replace_value():
    """Test the `replace_value` function."""
    print("\nTesting dictionaries.replace_value")
    orig = read_single_line_value(dictname="blockMeshDict",
                                  keyword="convertToMeters",
                                  casedir="./test", dtype=int)
    replace_value("test/system/blockMeshDict", "convertToMeters", 555)
    assert read_single_line_value(dictname="blockMeshDict",
                                  keyword="convertToMeters",
                                  casedir="./test") == 555
    replace_value("test/system/blockMeshDict", "convertToMeters", orig)
    assert read_single_line_value(dictname="blockMeshDict",
                                  keyword="convertToMeters",
                                  casedir="./test") == orig


def test_build_header():
    """Test the `dictionaries.build_header` function."""
    print("\nTesting dictionaries.build_header")
    h = build_header("blockMeshDict", incl_foamfile=True)
    print(h)
    assert h == r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}"""
    h = build_header("blockMeshDict", incl_foamfile=False)
    print(h)
    assert h == r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/"""
