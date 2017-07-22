__version__ = "0.0.5"

import os

# Attempt to detect OpenFOAM version
try:
    foam_version = os.environ["WM_PROJECT_VERSION"]
except KeyError:
    foam_version = "x.x.x"

from . import core
from .core import *
from . import dictionaries
from . import foil
from . import types
from . import templates
