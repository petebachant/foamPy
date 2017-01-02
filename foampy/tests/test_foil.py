"""Tests for the `foil` module."""

from __future__ import division, print_function, absolute_import
from foampy.foil import *


def test_reformat_foildata():
    ifp = "test/NACA_0021.dat"
    ofp = "test/NACA_0021.txt"
    ofp2 = "test/NACA_0021_2.txt"
    ofp3 = "test/NACA_0021_3.txt"
    if os.path.isfile(ofp):
        os.remove(ofp)
    reformat_foildata(ifp, ofp)
    if os.path.isfile(ofp2):
        os.remove(ofp2)
    reformat_foildata(ifp, ofp2, startline=118)
    if os.path.isfile(ofp3):
        os.remove(ofp3)
    reformat_foildata(ifp, ofp3, startline=118, stopline=119)


def test_foildata_mirror():
    fd = FoilData()
    fd.cl = np.linspace(1, 20, 10)
    fd.alpha = np.linspace(-5, 10, 10)
    fd.cd = np.linspace(0.001, 0.01, 10)
    fd.cm = np.linspace(0.5, 50, 10)
    fd.mirror()
    print(fd.alpha)
    assert fd.alpha[0] == -10.0
    assert fd.cl[0] == -fd.cl[-1]
    assert fd.cd[0] == fd.cd[-1]
    assert fd.cm[0] == -fd.cm[-1]


def test_mirror_foildata():
    reformat_foildata("test/NACA_0021.dat", "test/NACA_0021_4.txt",
                      startline=57)
    mirror_foildata("test/NACA_0021_4.txt", "test/NACA_0021_4_m.txt")
