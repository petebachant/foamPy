"""Tests for foamPy."""

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
