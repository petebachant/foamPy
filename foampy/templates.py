"""Code related to templating."""

from __future__ import division, print_function, absolute_import
import re
import subprocess
import os
import foampy


def to_snake_case(keyword):
    """Convert a keyword to snake case.

    From https://stackoverflow.com/questions/1175208
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', keyword)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def make_template(fpath, template_dir="templates", keywords=[], git=True,
                  delete=True):
    """Convert an OpenFOAM dictionary to a template for use with Python's
    string formatting.

    Parameters
    ----------
    fpath : str
        Path to file to be converted to a template.
    template_dir : str
        Path to directory in which to store templates.
    keywords : list
        List of strings to setup as formatted keywords in template.
    git : bool
        If ``True``, attempt to remove file from Git repo and add to
        ``.gitignore`` file.
    """
    fpath_template = os.path.join(template_dir, fpath)
    template_subdir = os.path.join(template_dir, os.path.dirname(fpath))
    if not os.path.isdir(template_subdir):
        os.makedirs(template_subdir)
    with open(fpath) as f:
        txt = f.read()
    txt = txt.replace("{", "{{")
    txt = txt.replace("}", "}}")
    new_txt = ""
    for line in txt.split("\n"):
        for kw in keywords:
            if line.strip().startswith(kw):
                val = line.replace(";", " ").strip().split()[1]
                line = line.replace(val, "{" + to_snake_case(kw) + "}")
        new_txt += line + "\n"
    with open(fpath_template, "w") as f:
        f.write(new_txt)
    # Now delete old file
    if git and delete:
        try:
            subprocess.call("git rm -f " + fpath, shell=True)
        except subprocess.CalledProcessError as e:
            print("Could not remove file from Git repo")
            print(e)
            os.remove(fpath)
    elif delete:
        os.remove(fpath)
    if git:
        # Add to gitignore if applicable
        if os.path.isfile(".gitignore"):
            with open(".gitignore") as f:
                txt = f.read()
            if not fpath in txt.split("\n"):
                print("Adding", fpath, "to .gitignore")
                if not txt.endswith("\n"):
                    txt += "\n"
                txt += fpath + "\n"
                with open(".gitignore", "w") as f:
                    f.write(txt)


def gen_from_template_dir(fpath_out, template_dir="templates", fname_out=None,
                          **params):
    """Generate a file from a template with the same relative path inside
    ``template_dir``.
    """
    fpath_template = os.path.join(template_dir, fpath_out)
    if fname_out is not None:
        fpath_out = os.path.join(os.path.dirname(fpath_out), fname_out)
    with open(fpath_template) as f:
        txt = f.read()
    with open(fpath_out, "w") as f:
        f.write(txt.format(**params))


def fill_template(src, dest=None, **params):
    """Fill a template file based on given parameters using new style Python
    string formatting.
    """
    if dest is None:
        dest = src.replace(".template", "")
    with open(src) as f:
        txt = f.read()
    with open(dest, "w") as f:
        f.write(txt.format(**params))
