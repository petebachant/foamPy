
"""
by Pete Bachant (c) 2014

This module contains some useful classes and scripts for working with
OpenFOAM. I'm not sure how it compares with PyFoam.

"""
from __future__ import division, print_function
import numpy as np
import os
import re
from PyQt4 import QtCore, QtGui
import datetime
import sys
import time
from .dictionaries import system_dicts, constant_dicts


def load_torque_drag_old(casedir="", folder="0", filename=None):
    """Loads time, z-axis torque, and streamwise force from specified forces
    folder. Case name can be left empty if running within a case folder."""
    regex = r"([0-9.eE\-+]+)\s+\(+([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
    regex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
    regex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)+"
    regex += r"\s+\(+([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
    regex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)"
    regex += r"\,\(([0-9.eE\-+]+)\s([0-9.eE\-+]+)\s([0-9.eE\-+]+)\)+"
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
            match = re.search(regex,line)
            if match:
                t.append(float(match.group(1)))
                fpx.append(float(match.group(2)))
                fpy.append(float(match.group(3)))
                fpz.append(float(match.group(4)))
                fvx.append(float(match.group(5)))
                fvy.append(float(match.group(6)))
                fvz.append(float(match.group(7)))
                fpox.append(float(match.group(8)))
                fpoy.append(float(match.group(9)))
                fpoz.append(float(match.group(10)))
                mpx.append(float(match.group(11)))
                mpy.append(float(match.group(12)))
                mpz.append(float(match.group(13)))
                mvx.append(float(match.group(14)))
                mvy.append(float(match.group(15)))
                mvz.append(float(match.group(16)))
                mpox.append(float(match.group(17)))
                mpoy.append(float(match.group(18)))
                mpoz.append(float(match.group(19)))
    #Convert to numpy arrays
    t = np.asarray(t)
    torque = np.asarray(np.asarray(mpz) + np.asarray(mvz))
    drag = np.asarray(np.asarray(fpx) + np.asarray(fvx))
    return t, torque, drag
    
def load_forces_moments(casedir="", folder="0", filename=None):
    """Loads time, forces, and moments into a dictionary of Numpy arrays."""
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
    data = {"time" : np.asarray(t),
            "force" : {"pressure" : {"x" : np.asarray(fpx),
                                     "y" : np.asarray(fpy),
                                     "z" : np.asarray(fpz)},
                       "viscous" : {"x" : np.asarray(fvx),
                                    "y" : np.asarray(fvy),
                                    "z" : np.asarray(fvz)},
                       "porous" : {"x" : np.asarray(fpox),
                                   "y" : np.asarray(fpoy),
                                   "z" : np.asarray(fpoz)}},
            "moment" : {"pressure" : {"x" : np.asarray(mpx),
                                      "y" : np.asarray(mpy),
                                      "z" : np.asarray(mpz)},
                        "viscous" : {"x" : np.asarray(mvx),
                                     "y" : np.asarray(mvy),
                                    "z" : np.asarray(mvz)},
                        "porous" : {"x" : np.asarray(mpox),
                                    "y" : np.asarray(mpoy),
                                    "z" : np.asarray(mpoz)}}}        
    return data

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


def load_theta_omega(casedir="", t_interp=None, theta_units="degrees"):
    """Imports omega from dynamicMeshDict table. Returns t, theta, 
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
    if t_interp != None:
        omega = np.interp(t_interp, t, omega)
        theta = np.interp(t_interp, t, theta)
    if theta_units == "degrees":
        theta = theta/np.pi*180
    return t, theta, omega
    
def load_set(casedir="", name="profile", quantity="U", fmt="xy", axis="xyz"):
    """Imports text data created with the OpenFOAM sample utility"""
    if casedir != "":
        folder = casedir + "/postProcessing/sets"
    else:
        folder = "postProcessing/sets"
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
    
def load_sample_xy(casedir="", profile="U"):
    """Imports text data created with the OpenFOAM sample utility"""
    if casedir != "":
        folder = casedir + "/postProcessing/sets"
    else:
        folder = "postProcessing/sets"
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
    """Get run endTime"""
    with open("system/controlDict", "r") as f:
        for line in f.readlines():
            line = line.replace(";", "").split()
            if "endTime" in line and line[0] == "endTime":
                endtime = float(line[1])
    return endtime
    
def get_deltat():
    """Get run deltaT"""
    with open("system/controlDict", "r") as f:
        for line in f.readlines():
            line = line.replace(";", "").split()
            if "deltaT" in line and line[0] == "deltaT":
                deltat = float(line[1])
    return deltat
    
def get_ncells(logname="log.checkMesh", keyword="cells"):
    if keyword == "cells":
        keyword = "cells:"
    with open(logname) as f:
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
    
def read_dict(dictname, casedir=""):
    """Read an OpenFOAM dict into a Python dict. Right now this is quite
    crude, but gets the job done decently for 1 word parameters."""
    foamdict = {}
    if dictname in system_dicts:
        p = "system/" + dictname
    elif dictname in constant_dicts:
        p = "constant/" + dictname
    elif dictname == "blockMeshDict":
        p = "constant/polyMesh/" + dictname
    with open(p) as f:
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

def get_solver_times(solver="pimpleDyMFoam", window=400):
    """Read last N lines from file solver log and return t (current Time),
    deltaT, and clockTime"""
    with open("log."+solver, "rb") as f:
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
    return t, deltat, exectime
    

class ProgressThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(bool)
    part_done = QtCore.pyqtSignal(int)
    timeleft_solverate = QtCore.pyqtSignal(list)
    def run(self):
        controldict = read_dict("controlDict")
        solver = controldict["application"]
        endtime = float(controldict["endTime"])
        done = False
        while not done:
            for d in os.listdir("./"):
                try:
                    if float(d) == endtime:
                        done = True
                except:
                    pass
            t, deltat, exectime = get_solver_times(solver)
            try:
                t_per_step = exectime[-1] - exectime[-2]
                tps2 = exectime[-2] - exectime[-3]
                t_per_step = (t_per_step + tps2)/2
            except IndexError:
                t, deltat, exectime = get_solver_times(solver, window=2000)
                t_per_step = exectime[-1] - exectime[-2]
            try:
                deltat = deltat[-1]
            except IndexError:
                deltat = get_deltat()
            self.part_done.emit(int(t[-1]/endtime*100))
            self.timeleft_solverate.emit([(endtime - t[-1]), t_per_step/deltat/3600])
            time.sleep(1)
        self.finished.emit(True)   


class ProgressBar(QtGui.QWidget):
    """Sets up a progress bar for an OpenFOAM run."""
    def __init__(self, parent=None):
        super(ProgressBar, self).__init__(parent)
        self.thread = ProgressThread()
        self.nameLine = QtGui.QLineEdit()    
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(1)
        self.progressbar.setMaximum(100)
        self.progressbar.setFixedWidth(400)    
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.progressbar, 0, 0)    
        self.setLayout(mainLayout)
        self.setWindowTitle("Solving")
        self.thread.part_done.connect(self.update_progress)
        self.thread.timeleft_solverate.connect(self.update_title)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_title(self, tlsr):
        solve_rate = np.round(tlsr[1], decimals=2)
        slt = tlsr[1]*tlsr[0]
        solve_time_left = str(datetime.timedelta(hours=slt))[:-7]
        self.setWindowTitle("Solving at " + str(solve_rate) + " h/s - " \
                + solve_time_left + " remaining")
                
    def update_progress(self, val):
        self.progressbar.setValue(val)
        
    def on_finished(self):
        sys.exit()

def make_progress_bar(gui=True):
    if gui:
        app = QtGui.QApplication(sys.path)
        pbarwin = ProgressBar()
        pbarwin.show()
        app.exec_()
    else:
        controldict = read_dict("controlDict")
        solver = controldict["application"]
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
                t, deltat, exectime = get_solver_times(solver)
                try:
                    t_per_step = exectime[-1] - exectime[-2]
                    tps2 = exectime[-2] - exectime[-3]
                    t_per_step = (t_per_step + tps2)/2
                except IndexError:
                    t, deltat, exectime = get_solver_times(solver, window=2000)
                    t_per_step = exectime[-1] - exectime[-2]
                try:
                    deltat = deltat[-1]
                except IndexError:
                    deltat = get_deltat()
                percent_done = int(t[-1]/endtime*100)
                time_left, solve_rate = endtime - t[-1], t_per_step/deltat/3600
                slt = time_left*solve_rate
                solve_time_left = str(datetime.timedelta(hours=slt))[:-7]
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

def main():
    """Testing things."""
    gen_dynmeshdict(1, 1, 1, npoints=10)
    t, theta, omega = load_theta_omega()
    print(t)
    print(omega)

if __name__ == "__main__":
    main()
