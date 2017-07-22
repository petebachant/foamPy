"""Tests for templates module"""

import foampy.templates
import os

cwd = os.getcwd()


def test_gen_from_template_dir():
    os.chdir("test")
    foampy.templates.make_template("system/controlDict",
                                   delete=False, git=False,
                                   keywords=["deltaT"])
    assert os.path.isfile("templates/system/controlDict")
    with open("templates/system/controlDict") as f:
        txt = f.read()
        assert "{delta_t}" in txt
    os.remove("templates/system/controlDict")
    os.chdir(cwd)
