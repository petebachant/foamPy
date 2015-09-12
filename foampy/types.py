# -*- coding: utf-8 -*-
"""
This module contains classes to work with custom OpenFOAM classes, e.g., lists
and dictionaries.
"""

from __future__ import division, print_function
import os
import foampy

class FoamDict(dict):
    """Object that represents an OpenFOAM dictionary."""
    
    def __init__(self, name="", casedir="./", subdir="system"):
        self.name = name
        self.subdir = subdir
        self.casedir = casedir
        self.fpath = os.path.join(casedir, subdir, name)
        if os.path.isfile(self.fpath):
            self.read()
        else:
            self.header = foampy.dictionaries.build_header(name,
                    foampy.foam_version, fileclass="dictionary")
            
    def read(self):
        """Parse dictionary."""
        pass
    
    def __str__(self):
        """Create text from dictionary in OpenFOAM format."""
        return "test"
    
    
def BlockMeshDict(FoamDict):
    """Object to represent a `blockMeshDict`."""
    
    def __init__(self, name="blockMeshDict", casedir="./", 
                 subdir="constant/polyMesh"):
        FoamDict.__init__(self)


def test_foamdict():
    """Test `FoamDict` class."""
    d = FoamDict(name="controlDict", casedir="test")
    print(d)