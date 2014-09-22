import os
from paraview.simple import OpenDataFile, RenameSource, Show

surfdir = "postProcessing/surfaces"

times = sorted(os.listdir(surfdir))

files = os.listdir(os.path.join(surfdir, times[0]))

for f in files:
    file_list = [os.path.join(surfdir, t, f) for t in times]
    OpenDataFile(file_list)
    RenameSource(f.replace(".vtk", ""))

