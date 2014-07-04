#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script creates the dynamic mesh dictionary with periodic omega

omega fluctuates with 3 periods per rotation, and a phase shift to put
the first peak at 80 degrees, to match experiments

@author: pete
"""

import foampy

U = 1.0
R = 0.5
meantsr = 1.9

foampy.gen_dynmeshdict(U, R, meantsr, cellzone="AMIsurface_z", npoints=500)
