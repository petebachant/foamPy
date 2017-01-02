"""
Module for working with foil data.
"""
from __future__ import division, print_function
import os
import numpy as np


class FoilData(object):
    """
    Object that represents a foil characteristic database.
    """
    def __init__(self):
        self.alpha = []
        self.cl = []
        self.cd = []
        self.cm = []
        self.comments = ["// Reformatted with foamPy\n",
                         "// (alpha_deg cl cd cm)\n"]

    def read(self, fpath, startline=None, stopline=None, comments=False):
        """
        Reads foil data from file. Format is detected automatically, but
        column order is not.
        """
        self.alpha = []
        self.cl = []
        self.cd = []
        self.cm = []
        if comments:
            self.comments = []
        in_block = False
        with open(fpath, "r") as f:
            for n, line in enumerate(f.readlines()):
                if startline is not None and n+1 < startline:
                    pass
                elif stopline is not None and n+1 > stopline:
                    pass
                else:
                    try:
                        line = line.replace("(", "")
                        line = line.replace(")", "")
                        a = [float(n) for n in line.replace(",", " ").split()]
                        self.alpha.append(a[0])
                        self.cl.append(a[1])
                        self.cd.append(a[2])
                        if len(a) > 3:
                            self.cm.append(a[3])
                        else:
                            self.cm.append(0.0)
                        in_block = True
                    except (ValueError, IndexError):
                        if in_block:
                            break
                        else:
                            if comments:
                                self.comments.append(line)
        self.alpha = np.asarray(self.alpha)
        self.cl = np.asarray(self.cl)
        self.cd = np.asarray(self.cd)
        self.cm = np.asarray(self.cm)

    def mirror(self):
        """Mirror positive coefficients about zero degrees angle of attack."""
        self.cl = self.cl[self.alpha >= 0]
        self.cd = self.cd[self.alpha >= 0]
        self.cm = self.cm[self.alpha >= 0]
        self.alpha = self.alpha[self.alpha >= 0]
        self.alpha = np.append(-self.alpha[-1:0:-1], self.alpha)
        self.cl = np.append(-self.cl[-1:0:-1], self.cl)
        self.cd = np.append(self.cd[-1:0:-1], self.cd)
        self.cm = np.append(-self.cm[-1:0:-1], self.cm)

    def write(self, fpath):
        """
        Write foil data to file in OpenFOAM format.
        """
        with open(fpath, "w") as f:
            for comment in self.comments:
                if comment.strip()[:2] != "//":
                    comment = "// " + comment
                f.write(comment)
            for a, cl, cd, cm in zip(self.alpha, self.cl, self.cd, self.cm):
                f.write("({} {} {} {})\n".format(a, cl, cd, cm))


def reformat_foildata(input_path, output_path, startline=None, stopline=None):
    """
    Reformat foil data file into a list of 4-element OpenFOAM lists.
    """
    fd = FoilData()
    fd.read(input_path, startline, stopline)
    fd.write(output_path)


def mirror_foildata(inpath, outpath):
    """Mirror positive data in file about zero angle of attack."""
    fd = FoilData()
    fd.read(inpath, comments=True)
    fd.mirror()
    fd.write(outpath)
