__version__ = "0.0.2"

import os

# Attempt to detect OpenFOAM version
try:
    wm_project_dir = os.environ["WM_PROJECT_DIR"]
    foam_version = os.path.split(wm_project_dir)[-1].replace("OpenFOAM-", "")
except KeyError:
    foam_version = "x.x.x"

from . import core
from .core import *
from . import dictionaries
from . import foil
from . import types
