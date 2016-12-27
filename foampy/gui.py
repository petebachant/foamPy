"""GUI-based tools."""

from __future__ import division, print_function, absolute_import
try:
    from PyQt4 import QtCore, QtGui
except:
    from PyQt5 import QtCore, QtGui


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


def make_progress_bar():
    app = QtGui.QApplication(sys.path)
    pbarwin = ProgressBar()
    pbarwin.show()
    app.exec_()
