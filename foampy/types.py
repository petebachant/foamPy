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
        self.foam_version = foampy.foam_version
        self.header = ""
        if os.path.isfile(self.fpath):
            self.read()
        else:
            self.header = foampy.dictionaries.build_header(name,
                    self.foam_version, fileclass="dictionary")
            
    def read(self):
        """Parse dictionary."""
        # Read header first
        with open(self.fpath) as f:
            in_header = False
            for line in f:
                if line[:2] == "/*":
                    in_header = True
                elif line[:2] == r"\*":
                    self.header += line
                    in_header = False
                if in_header:
                    self.header += line           
        # Parse header for OpenFOAM version
        splitheader = self.header.split()
        if "Version:" in splitheader:
            index = splitheader.index("Version:") + 1
            self.foam_version = splitheader[index]
    
    def __str__(self):
        """Create text from dictionary in OpenFOAM format."""
        return self.header
    
    
class BlockMeshDict(FoamDict):
    """Object to represent a `blockMeshDict`."""
    
    def __init__(self, name="blockMeshDict", casedir="./", 
                 subdir="constant/polyMesh"):
        FoamDict.__init__(self)


class FoamList(list):
    """Class that represents an OpenFOAM list."""
    
    def __init__(self, py_list=[], dtype=float):
        py_list = [dtype(i) for i in py_list]
        list.__init__(self, py_list)
    
    def __str__(self):
        txt = "("
        for i in self:
            txt += str(i) + " "
        txt = txt[:-1]
        txt += ")"
        return txt


def test_foamdict():
    """Test `FoamDict` class."""
    d = FoamDict(name="controlDict", casedir="test")
    print(d)
    print(d.foam_version)
    

def test_foamlist():
    """Test `FoamList` class."""
    flist = FoamList([1, 2, 3, 4])
    print(flist)
    
    for i in flist:
        print(i)
        
    flist2 = FoamList([flist, flist], dtype=FoamList)
    print(flist2)