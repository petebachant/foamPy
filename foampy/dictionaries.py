
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


if __name__ == "__main__":
    print(build_header("controlDict", fileclass="volVectorField"))
