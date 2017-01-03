"""Functions for reading and writing dictionaries."""

from __future__ import division, print_function
import os


system_dicts = ["controlDict", "snappyHexMeshDict", "fvSchemes", "fvSolution",
                "fvOptions", "decomposeParDict", "topoSetDict", "blockMeshDict"]
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


def read_single_line_value(dictname=None, dictpath=None, keyword="",
                           dtype=float, casedir="./"):
    """Read value from a dictionary that appears on a single line."""
    if dictpath is None and dictname is not None:
        if dictname in system_dicts:
            dictpath = os.path.join(casedir, "system", dictname)
        elif dictname in constant_dicts:
            dictpath = os.path.join(casedir, "constant", dictname)
    elif dictpath is None and dictname is None:
        raise ValueError("Neither dictionary name nor dictionary path supplied")
    with open(dictpath) as f:
        for line in f.readlines():
            line = line.strip()
            if ";" in line:
                ls = line.replace(";", " ").split()
                if ls[0] == keyword:
                    return dtype(ls[1])
