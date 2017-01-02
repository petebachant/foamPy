"""Tests for core foamPy functions."""

from __future__ import division, print_function, absolute_import
import foampy
import os
import numpy as np


def test_load_all_torque_drag():
    t, torque, drag = foampy.load_all_torque_drag(casedir="test")
    assert t.max() == 4.0


def test_gen_dynmeshdict():
    os.chdir("test")
    u = 1
    r = 1
    meantsr = 1
    foampy.gen_dynmeshdict(u, r, meantsr, npoints=10, rpm_fluc=0)
    t, theta, omega = foampy.load_theta_omega()
    assert t.min() == 0
    assert t.max() == 0.5
    assert len(omega) == 10
    assert np.mean(omega*r/u) == meantsr
    os.chdir("../")
    os.system("git checkout test/constant/dynamicMeshDict")


def test_run():
    foampy.run("blockMesh", args=["-help"], tee=True)
    assert os.path.isfile("log.blockMesh")
    foampy.run("blockMesh", args=["-help"], tee=True, append=True)
    try:
        foampy.run("blockMesh", args=["-help"], tee=True, append=False)
    except IOError as e:
        print(e)
    os.remove("log.blockMesh")


def test_run_parallel():
    foampy.run_parallel("blockMesh", nproc=2, args=["-help"], tee=True)
    assert os.path.isfile("log.blockMesh")
    foampy.run_parallel("blockMesh", nproc=2, args=["-help"], tee=False,
                        append=True)
    os.remove("log.blockMesh")


def test_get_n_processors():
    n = foampy.get_n_processors(casedir="test")
    assert n == 6
