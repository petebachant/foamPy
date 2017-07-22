"""Core functionality for foamPy."""

from __future__ import division, print_function
import numpy as np
import os
import re
import datetime
import sys
import time
import subprocess
import pandas
import glob
from .dictionaries import *
from .templates import *


def gen_stripped_lines(fpath):
    with open(fpath) as f:
        for line in f.readlines():
            yield line.replace("(", " ").replace(")", " ")


def load_forces(casedir="./", object_name="forces", start_time=0):
    """Load forces and moments as a pandas DataFrame."""
    glob_string = os.path.join(
        casedir,
        "postProcessing/{}/{}/forces*.dat".format(object_name, start_time)
    )
    fpath = sorted(glob.glob(glob_string))[-1]
    data = np.loadtxt(gen_stripped_lines(fpath))
    df = pandas.DataFrame()
    df["time"] = data[:, 0]
    df["fx_pressure"] = data[:, 1]
    df["fx_viscous"] = data[:, 4]
    df["fx_porous"] = data[:, 7]
    df["fy_pressure"] = data[:, 2]
    df["fy_viscous"] = data[:, 5]
    df["fy_porous"] = data[:, 8]
    df["fz_pressure"] = data[:, 3]
    df["fz_viscous"] = data[:, 6]
    df["fz_porous"] = data[:, 9]
    df["mx_pressure"] = data[:, 10]
    df["mx_viscous"] = data[:, 13]
    df["mx_porous"] = data[:, 16]
    df["my_pressure"] = data[:, 11]
    df["my_viscous"] = data[:, 14]
    df["my_porous"] = data[:, 17]
    df["mz_pressure"] = data[:, 12]
    df["mz_viscous"] = data[:, 15]
    df["mz_porous"] = data[:, 18]
    for fm in ["f", "m"]:
        for component in ["x", "y", "z"]:
            df[fm + component] = df[fm + component + "_pressure"] \
                               + df[fm + component + "_viscous"] \
                               + df[fm + component + "_porous"]
    return df


def load_probes_data(casedir="./", object_name="probes", start_time=0,
                     field_name="U"):
    """Load probes data as pandas ``DataFrame``."""
    fpath = os.path.join(casedir, "postProcessing", object_name,
                         str(start_time), field_name)
    # First get probe locations to use as column names
    with open(fpath) as f:
        txt = f.read()
    probe_lines = re.findall(r"# Probe \d.*\n", txt)
    probe_locs = []
    for line in probe_lines:
        probe_locs.append(line.split("(")[-1].split(")")[0].split())
    data = np.loadtxt(gen_stripped_lines(fpath))
    df = pandas.DataFrame()
    df["time"] = data[:, 0]
    # Determine the rank of the data
    nprobes = len(probe_locs)
    nsamps = data.shape[0]
    dims = (data.shape[1] - 1) // nprobes
    for n, probe_loc in enumerate(probe_locs):
        probe_loc = [float(pl) for pl in probe_loc]
        d = data[:, n + 1:n + dims + 1]
        if dims > 1:
            d = [tuple(p) for p in d]
        df[tuple(probe_loc)] = d
    return df


def load_torque_drag(casedir="", folder="0", filename=None,
                     torque_axis="z", drag_axis="x"):
    """Loads time, z-axis torque, and streamwise force from specified forces
    folder. Case name can be left empty if running within a case folder."""
    # Create empty lists
    t = []
    fpx = []; fpy = []; fpz = []
    fpox = []; fpoy = []; fpoz = []
    fvx = []; fvy = []; fvz = []
    mpx = []; mpy = []; mpz = []
    mpox = []; mpoy = []; mpoz = []
    mvx = []; mvy = []; mvz = []
    # Cycle through file
    if casedir: casedir += "/"
    if not filename: filename = "forces.dat"
    with open(casedir+"postProcessing/forces/"+str(folder)+"/"+filename, "r") as f:
        for line in f.readlines():
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", " ")
            line = line.split()
            if line[0] != "#":
                t.append(float(line[0]))
                fpx.append(float(line[1]))
                fpy.append(float(line[2]))
                fpz.append(float(line[3]))
                fvx.append(float(line[4]))
                fvy.append(float(line[5]))
                fvz.append(float(line[6]))
                fpox.append(float(line[7]))
                fpoy.append(float(line[8]))
                fpoz.append(float(line[9]))
                mpx.append(float(line[10]))
                mpy.append(float(line[11]))
                mpz.append(float(line[12]))
                mvx.append(float(line[13]))
                mvy.append(float(line[14]))
                mvz.append(float(line[15]))
                mpox.append(float(line[16]))
                mpoy.append(float(line[17]))
                mpoz.append(float(line[18]))
    #Convert to numpy arrays
    t = np.asarray(t)
    if torque_axis == "z":
        torque = np.asarray(np.asarray(mpz) + np.asarray(mvz))
    elif torque_axis == "x":
        torque = np.asarray(np.asarray(mpx) + np.asarray(mvx))
    if drag_axis == "x":
        drag = np.asarray(np.asarray(fpx) + np.asarray(fvx))
    return t, torque, drag


def load_all_torque_drag(casedir="", torque_axis="z", drag_axis="x"):
    t, torque, drag = np.array([]), np.array([]), np.array([])
    if casedir: casedir += "/"
    folders = sorted(os.listdir(casedir+"postProcessing/forces"))
    for folder in folders:
        files = sorted(os.listdir(casedir+"postProcessing/forces/"+folder))
        for f in files:
            t1, torque1, drag1 = load_torque_drag(casedir=casedir,
                                                  folder=folder,
                                                  filename=f,
                                                  torque_axis=torque_axis,
                                                  drag_axis=drag_axis)
            t = np.append(t, t1)
            torque = np.append(torque, torque1)
            drag = np.append(drag, drag1)
    return t, torque, drag


def load_theta_omega(casedir="", t_interp=[], theta_units="degrees"):
    """Import omega from ``dynamicMeshDict`` table. Returns t, theta,
    omega (rad/s) where theta is calculated using the trapezoidal rule.

    `t_interp` is a keyword argument for an array over which omega and theta
    will be interpolated.
    """
    t = []
    omega = []
    if casedir != "":
        casedir += "/"
    with open(casedir+"constant/dynamicMeshDict", "r") as f:
        regex = r"\d+.\d+"
        for line in f.readlines():
            match = re.findall(regex, line)
            if len(match)==2:
                t.append(float(match[0]))
                omega.append(float(match[1]))
    omega = np.asarray(omega)
    t = np.asarray(t)
    # Integrate omega to obtain theta
    theta = np.zeros(len(t))
    for n in range(len(t)):
        theta[n] = np.trapz(omega[:n], t[:n])
    # If provided, interpolate omega to match t vector
    if len(t_interp) > 0:
        omega = np.interp(t_interp, t, omega)
        theta = np.interp(t_interp, t, theta)
    if theta_units == "degrees":
        theta = theta/np.pi*180
    return t, theta, omega


def load_set(casedir="./", name="profile", quantity="U", fmt="xy", axis="xyz"):
    """Import text data created with the OpenFOAM sample utility."""
    folder = os.path.join(casedir, "postProcessing", "sets")
    t = []
    times = os.listdir(folder)
    for time1 in times:
        try:
            float(time1)
        except ValueError:
            times.remove(time1)
        try:
            t.append(int(time1))
        except ValueError:
            t.append(float(time1))
    t.sort()
    data = {"time" : t}
    for ts in t:
        filename = "{folder}/{time}/{name}_{q}.{fmt}".format(folder=folder,
            time=ts, name=name, q=quantity, fmt=fmt)
        with open(filename) as f:
            d = np.loadtxt(f)
            if quantity == "U":
                data[ts] = {"u" : d[:, len(axis)],
                            "v" : d[:, len(axis)+1],
                            "w" : d[:, len(axis)+2]}
                if len(axis) == 1:
                    data[ts][axis] = d[:,0]
                else:
                    data[ts]["x"] = d[:,0]
                    data[ts]["y"] = d[:,1]
                    data[ts]["z"] = d[:,2]
    return data


def load_sample_xy(casedir="./", profile="U"):
    """Import text data created with the OpenFOAM sample utility."""
    folder = os.path.join(casedir, "postProcessing", "sets")
    t = []
    times = os.listdir(folder)
    for time1 in times:
        try:
            float(time1)
        except ValueError:
            times.remove(time1)
        try:
            t.append(int(time1))
        except ValueError:
            t.append(float(time1))
    t.sort()
    # Load a y vector from a single file since they are identical
    with open(folder+"/0/profile_"+profile+".xy") as f:
        y = np.loadtxt(f)[:,0]
    if profile == "U":
        u = np.zeros((len(y), len(times)))
        v = np.zeros((len(y), len(times)))
    elif profile == "R":
        uu = np.zeros((len(y), len(times)))
        uv = np.zeros((len(y), len(times)))
        uw = np.zeros((len(y), len(times)))
        vv = np.zeros((len(y), len(times)))
        vw = np.zeros((len(y), len(times)))
        ww = np.zeros((len(y), len(times)))
    for n in range(len(times)):
        with open(folder+"/"+str(t[n])+"/profile_"+profile+".xy") as f:
            data = np.loadtxt(f)
            if profile == "U":
                u[:,n] = data[:,1]
                v[:,n] = data[:,2]
            elif profile == "R":
                uu[:,n] = data[:,1]
                uv[:,n] = data[:,2]
                uw[:,n] = data[:,3]
                vv[:,n] = data[:,4]
                vw[:,n] = data[:,5]
                ww[:,n] = data[:,6]
    t = np.asarray(t, dtype=float)
    if profile == "U":
        data = {"t" : t, "u" : u, "v": v, "y" : y}
    elif profile == "R":
        data = {"t" : t, "uu" : uu, "vv": vv, "ww" : ww,
                "uv" : uv, "y" : y}
    return data


def get_endtime():
    """Get run ``endTime``."""
    with open("system/controlDict", "r") as f:
        for line in f.readlines():
            line = line.replace(";", "").split()
            if "endTime" in line and line[0] == "endTime":
                endtime = float(line[1])
    return endtime


def get_deltat(casedir="./"):
    """Get run ``deltaT``."""
    fpath = os.path.join(casedir, "system", "controlDict")
    with open(fpath) as f:
        for line in f.readlines():
            line = line.replace(";", "").split()
            if "deltaT" in line and line[0] == "deltaT":
                deltat = float(line[1])
    return deltat


def get_ncells(casedir="./", logname="log.checkMesh", keyword="cells",
               autogen=True):
    fpath = os.path.join(casedir, logname)
    if not os.path.isfile(fpath) and autogen:
        start_dir = os.getcwd()
        os.chdir(casedir)
        run("checkMesh", args="-time 0")
        os.chdir(start_dir)
    if keyword == "cells":
        keyword = "cells:"
    with open(fpath) as f:
        for line in f.readlines():
            ls = line.split()
            if ls and ls[0] == keyword:
                value = ls[1]
                return int(value)


def get_max_courant_no():
    with open("system/controlDict") as f:
        for line in f.readlines():
            if ";" in line:
                ls = line.replace(";", " ").split()
                if ls[0] == "maxCo":
                    return float(ls[1])


def read_dict(dictname=None, dictpath=None, casedir="./"):
    """Read an OpenFOAM dict into a Python dict. Right now this is quite
    crude, but gets the job done decently for 1 word parameters."""
    foamdict = {}
    if dictpath is None and dictname is not None:
        if dictname in system_dicts:
            p = "system/" + dictname
        elif dictname in constant_dicts:
            p = "constant/" + dictname
        dictpath = os.path.join(casedir, p)
    with open(dictpath) as f:
        for line in f.readlines():
            if ";" in line:
                line = line.replace(";", "")
                line = line.split()
                if len(line) > 1:
                    foamdict[line[0]] = line[1]
    return foamdict


def read_case():
    """Will eventually read all case dicts and put in a hierarchy of dicts."""
    pass


def gen_dynmeshdict(U, R, meantsr, cellzone="AMIsurface", rpm_fluc=3.7,
                    npoints=400, axis="(0 0 1)", direction=1):
    """Generates a dynamicMeshDict for a given U, R, meantsr, and an optional
    rpm fluctuation amplitude. Phase is fixed."""
    meanomega = meantsr*U/R
    if npoints > 0:
        amp_omega = rpm_fluc*2*np.pi/60.0
        endtime = get_endtime()
        t = np.linspace(0, endtime, npoints)
        omega = meanomega + amp_omega*np.sin(3*meanomega*t - np.pi/1.2)
    # Write to file
    top = \
    r"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.3.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}


dynamicFvMesh   solidBodyMotionFvMesh;

motionSolverLibs ("libfvMotionSolvers.so");

solidBodyMotionFvMeshCoeffs
{
    cellZone        """ + cellzone +""";
    solidBodyMotionFunction  rotatingMotion;
    rotatingMotionCoeffs
    {
        origin\t\t(0 0 0);
        axis\t\t""" + axis + ";\n"
    if npoints > 0:
        top += """        omega\t\ttable
        (
"""
        """Table should be in form
        		(t0 omega0)
        		(t1 omega1)
        """
        table = ""
        for n in range(len(t)-1):
            table += "            (" + str(t[n]) + " " + str(omega[n]) + ")\n"
        table += "            (" + str(t[-1]) + " " + str(omega[-1]) + ")"
        bottom = """
        );
    }
}"""
        alltxt = top + table + bottom
    else:
        alltxt = top + "\n        omega\t\t" + str(direction*meanomega)\
                + ";\n    }\n}\n"
    with open("constant/dynamicMeshDict", "w") as f:
        f.write(alltxt)


def get_solver_times(casedir="./", solver=None, log_fpath=None, window=400):
    """Read last N lines from file solver log and return t (current Time),
    `deltaT`, and `clockTime`.
    """
    if log_fpath is None and solver is None:
        log_fpath = "log." + read_dict("controlDict",
                                       casedir=casedir)["application"]
        if not os.path.isfile(log_fpath):
            log_fpath = glob.glob(os.path.join(casedir, "log.*Foam"))[0]
    elif log_fpath is None and solver is not None:
        log_fpath = os.path.join(casedir, "log." + solver)
    with open(log_fpath, "rb") as f:
        BUFSIZ = 1024
        # True if open() was overridden and file was opened in text
        # mode. In that case readlines() will return unicode strings
        # instead of bytes.
        encoded = getattr(f, "encoding", False)
        CR = "\n" if encoded else b"\n"
        data = "" if encoded else b""
        f.seek(0, os.SEEK_END)
        fsize = f.tell()
        block = -1
        exit = False
        while not exit:
            step = (block * BUFSIZ)
            if abs(step) >= fsize:
                f.seek(0)
                newdata = f.read(BUFSIZ - (abs(step) - fsize))
                exit = True
            else:
                f.seek(step, os.SEEK_END)
                newdata = f.read(BUFSIZ)
            data = newdata + data
            if data.count(CR) >= window:
                break
            else:
                block -= 1
    log = data.splitlines()[-window:]
    t = []
    clocktime = []
    exectime = []
    deltat = []
    for entry in log:
        try:
            line = entry.split()
            if line[0] == b"Time":
                t.append(float(line[-1]))
            if b"ClockTime" in line:
                clocktime.append(float(line[-2]))
            if b"ExecutionTime" in line:
                exectime.append(float(line[2]))
            if b"deltaT" in line:
                deltat.append(float(line[-1]))
        except:
            pass
    return {"time": t, "delta_t": deltat, "exectime": exectime,
            "clocktime": clocktime}


def monitor_progress():
    """Monitor solver progress."""
    controldict = read_dict("controlDict")
    endtime = float(controldict["endTime"])
    done = False
    try:
        while not done:
            for d in os.listdir("./"):
                try:
                    if float(d) == endtime:
                        done = True
                except:
                    pass
            solver_times = get_solver_times()
            t = solver_times["time"]
            deltat = solver_times["delta_t"]
            exectime = solver_times["exectime"]
            try:
                t_per_step = exectime[-1] - exectime[-2]
                tps2 = exectime[-2] - exectime[-3]
                t_per_step = (t_per_step + tps2)/2
            except IndexError:
                solver_times = get_solver_times(window=2000)
                t = solver_times["time"]
                deltat = solver_times["delta_t"]
                exectime = solver_times["exectime"]
                t_per_step = exectime[-1] - exectime[-2]
            try:
                deltat = deltat[-1]
            except IndexError:
                deltat = get_deltat()
            percent_done = int(t[-1]/endtime*100)
            time_left, solve_rate = endtime - t[-1], t_per_step/deltat/3600
            slt = time_left*solve_rate
            solve_time_left = str(datetime.timedelta(hours=slt))[:-7]
            print("\r" + " "*66, end="")
            print("\r[{}%] - solving at {:0.2f} h/s - {} remaining".format\
                    (percent_done, solve_rate, solve_time_left), end="")
            time.sleep(1)
        print("\nEnd")
    except KeyboardInterrupt:
        print("")


def read_log_end(logname, nlines=20):
    """Read last lines from log and return as a list."""
    window = nlines
    with open("log."+logname, "rb") as f:
        BUFSIZ = 1024
        # True if open() was overridden and file was opened in text
        # mode. In that case readlines() will return unicode strings
        # instead of bytes.
        encoded = getattr(f, 'encoding', False)
        CR = '\n' if encoded else b'\n'
        data = '' if encoded else b''
        f.seek(0, os.SEEK_END)
        fsize = f.tell()
        block = -1
        exit = False
        while not exit:
            step = (block * BUFSIZ)
            if abs(step) >= fsize:
                f.seek(0)
                newdata = f.read(BUFSIZ - (abs(step) - fsize))
                exit = True
            else:
                f.seek(step, os.SEEK_END)
                newdata = f.read(BUFSIZ)
            data = newdata + data
            if data.count(CR) >= window:
                break
            else:
                block -= 1
    log = data.splitlines()[-window:]
    return [line.decode("utf-8") for line in log]


def get_n_processors(casedir="./", dictpath="system/decomposeParDict"):
    """Read number of processors from decomposeParDict."""
    dictpath = os.path.join(casedir, dictpath)
    with open(dictpath) as f:
        for line in f.readlines():
            line = line.strip().replace(";", " ")
            if line:
                line = line.split()
                if line[0] == "numberOfSubdomains":
                    return int(line[1])


def run(appname, tee=False, logname=None, parallel=False, nproc=None, args=[],
        overwrite=False, append=False):
    """Run an application."""
    if logname is None:
        logname = "log." + appname
    if os.path.isfile(logname) and not overwrite and not append:
        raise IOError(logname + " exists; remove or use overwrite=True")
    if nproc is not None:
        if nproc > 1:
            parallel = True
    if parallel and nproc is None:
        nproc = get_n_processors()
    if isinstance(args, list):
        args = " ".join(args)
    if parallel:
        cmd = "mpirun -np {nproc} {app} -parallel {args}"
    else:
        cmd = "{app} {args}"
    if tee:
        cmd += " 2>&1 | tee {logname}"
        if append:
            cmd += " -a"
    else:
        cmd += " > {logname} 2>&1"
        if append:
            cmd = cmd.replace(" > ", " >> ")
    if parallel:
        print("Running {appname} on {n} processors".format(appname=appname,
              n=nproc))
    else:
        print("Running " + appname)
    subprocess.call(cmd.format(nproc=nproc, app=appname, args=args,
                               logname=logname), shell=True)


def run_parallel(appname, **kwargs):
    """Run application in parallel."""
    run(appname, parallel=True, **kwargs)


def summary(casedir="./", **extra_params):
    """Summarize a case and return as a pandas Series.

    Parameters
    ----------
    casedir : str
        Case directory to be summarized.
    extra_params : dict
        Key/value pairs for keywords and the functions that return their
        respective values.
    """
    s = pandas.Series()
    s["delta_t"] = get_deltat(casedir=casedir)
    s["n_cells"] = get_ncells(casedir=casedir)
    td = get_solver_times(casedir=casedir)
    s["simulated_time"] = td["time"][-1]
    s["clocktime"] = td["clocktime"][-1]
    s["exectime"] = td["exectime"][-1]
    for key, val in extra_params.items():
        s[key] = val
    return s


def clean(leave_mesh=False, remove_zero=False, extra=[]):
    """Clean case."""
    if not leave_mesh:
        subprocess.call(". $WM_PROJECT_DIR/bin/tools/CleanFunctions && "
                        "cleanCase", shell=True)
    else:
        subprocess.call(". $WM_PROJECT_DIR/bin/tools/CleanFunctions && "
                        "cleanTimeDirectories && cleanDynamicCode", shell=True)
        subprocess.call("rm -rf postProcessing", shell=True)
    if remove_zero:
        subprocess.call("rm -rf 0", shell=True)
    if extra:
        if not isinstance(extra, list):
            extra = [extra]
        for item in extra:
            print("Removing", item)
            subprocess.call("rm -rf {}".format(item), shell=True)
