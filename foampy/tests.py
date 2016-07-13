"""Tests for foamPy."""

from .core import *
from .dictionaries import *
from .types import *
from .foil import *


def test_load_all_torque_drag():
    """Test the `load_all_torque_drag` function."""
    t, torque, drag = load_all_torque_drag(casedir="test")
    assert t.max() == 4.0
