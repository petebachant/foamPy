
"""
by Pete Bachant (c) 2014

This module contains some useful classes and scripts for working with
OpenFOAM. I'm not sure how it compares with PyFoam.

"""
from __future__ import division, print_function


system_dicts = ["controlDict", "snappyHexMeshDict", "fvSchemes", "fvSolution",
                "fvOptions", "decomposeParDict", "topoSetDict"]
constant_dicts = ["dynamicMeshDict", "RASProperties", "transportProperties",
                  "turbulenceProperties"]

upper_rule = ("// * * * * * * * * * * * * * * * * * * * * * * * * * "
             "* * * * * * * * * * * * //")
lower_rule = ("// **********************************************"
             "*************************** //")


def build_header(dictobject="", version="2.3.x", fileclass="dictionary",
                 incl_foamfile=True):
    """Creates the header for an OpenFOAM dictionary. Inputs are the
    object and version."""
    txt = \
    r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  {}                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/""".format(version)
    if incl_foamfile:
        txt += \
        r"""
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {};
    object      {};
}}""".format(fileclass, dictobject)
    return txt


def replace_value(dictpath, keyword, newvalue):
    """Replace a value in a dictionary."""
    newvalue = str(newvalue)
    with open(dictpath) as f:
        in_block = False
        lines = f.readlines()
        single_line = True
        for n in range(len(lines)):
            sl = lines[n].split()
            if len(sl) > 0 and sl[0] == keyword:
                nstart = n
                if not ";" in lines[n]:
                    in_block = True
                    single_line = False
            if ";" in lines[n] and in_block:
                in_block = False
                nend = n
    if single_line:
        oldvalue = lines[nstart].replace(";", "").split()[1]
        newvalue = lines[nstart].replace(oldvalue, newvalue)
        new_text = lines[:nstart] + [newvalue] + lines[nstart+1:]
    else:
        new_text = lines[:nstart] + [newvalue] + lines[nend+1:]
    with open(dictpath, "w") as f:
        for line in new_text:
            f.write(line)


def read_text(dictpath, keyword):
    with open(dictpath) as f:
        in_block = False
        lines = f.readlines()
        single_line = True
        for n in range(len(lines)):
            sl = lines[n].split()
            if len(sl) > 0 and sl[0] == keyword:
                nstart = n
                if not ";" in lines[n]:
                    in_block = True
                    single_line = False
            if ";" in lines[n] and in_block:
                in_block = False
                nend = n
    return lines[nstart:nend+1]


def read_single_line_value(dictname, objname, dtype=float, casedir=""):
    """Read value from a dictionary that appears on a single line."""
    # Backwards compatibility
    valtype = dtype
    if casedir:
        p = casedir + "/"
    else:
        p = ""
    if dictname in constant_dicts:
        p += "constant/" + dictname
    elif dictname in system_dicts:
        p += "system/" + dictname
    elif dictname == "blockMeshDict":
        p += "constant/polyMesh/blockMeshDict"
    with open(p) as f:
        for line in f.readlines():
            if ";" in line:
                ls = line.replace(";", " ").split()
                if ls[0] == objname:
                    return valtype(ls[1])


def test_replace_value():
    """Test the `replace_value` function."""
    print("\nTesting dictionaries.replace_value")
    orig = read_single_line_value("blockMeshDict", "convertToMeters",
                                  casedir="./test", dtype=int)
    replace_value("test/constant/polyMesh/blockMeshDict", "convertToMeters",
                  555)
    assert read_single_line_value("blockMeshDict", "convertToMeters",
                                  casedir="./test") == 555
    replace_value("test/constant/polyMesh/blockMeshDict", "convertToMeters",
                  orig)
    assert read_single_line_value("blockMeshDict", "convertToMeters",
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
