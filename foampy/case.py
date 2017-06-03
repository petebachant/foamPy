"""Module to contain ``Case`` object."""

from __future__ import division, print_function

class Case(object):
    """Object to represent an entire OpenFOAM case.

    This should contain a list of dictionaries, some mandatory, some optional.
    """
    def __init__(self, casedir="./"):
        self.read()

    def read(self):
        """Read all dictionaries present."""
        pass
