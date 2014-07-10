
"""
by Pete Bachant (c) 2014

This module contains some useful classes and scripts for working with
OpenFOAM. I'm not sure how it compares with PyFoam.

"""
from __future__ import division, print_function

    
def build_header(dictobject, version="2.3.x", fileclass="dictionary"):
    """Creates the header for an OpenFOAM dictionary. Inputs are the 
    object and version."""
    return \
    r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  {}                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {};
    object      {};
}}
""".format(version, fileclass, dictobject)


def replace_value(dictpath, keyword, newvalue):
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


if __name__ == "__main__":
    new_text = """blocks
(
    hex (0 1 2 3 4 5 6 7)
    (66 66 44)
    simpleGrading (1 1 1)
);\n"""
    replace_value("../test/constant/polyMesh/blockMeshDict", "blocks", new_text)
    replace_value("../test/constant/polyMesh/blockMeshDict", "convertToMeters", "1.1")
    

