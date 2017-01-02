"""Tests for the `types` module."""

from __future__ import division, print_function, absolute_import
from foampy.types import *


def test_foamdict():
    """Test `FoamDict` class."""
    print("\nTesting FoamDict")
    d = FoamDict(name="controlDict", casedir="test")
    d["someInt"] = 555
    d["someFloat"] = 5.5
    d["someString"] = "aString"
    d["someBool"] = False
    d["someList"] = FoamList(np.arange(5))
    d["subDict"] = FoamSubDict(otherInt=5, otherFloat=5.555)
    d["subDict"]["addedLater"] = 666
    d["subDict"]["subSubDict"] = FoamSubDict(subSubBool=True)
    print(d)


def test_foamsubdict():
    """Test `FoamSubDict` class."""
    print("\nTesting FoamSubDict")
    d = FoamSubDict(name="FoamFile", version="2.0", format="ascii")
    d["class"] = "dictionary"
    d["object"] = "blockMeshDict"
    print(d)


def test_foamlist():
    """Test `FoamList` class."""
    print("\nTesting FoamList")
    flist = FoamList([1, 2, 3, 4])
    print(flist)

    for i in flist:
        print(i)

    flist2 = FoamList([flist, flist], dtype=FoamList)
    print(flist2)

    flist = FoamList("(0 0 0 0)", dtype=int)
    assert flist[:] == [0]*4
