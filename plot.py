#!/usr/bin/python3

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from math import log
import sys

region = 'The Forge'
try:
    if len(sys.argv) > 1:
        region = ' '.join(sys.argv[1:])
        print(region)
except:
    pass


app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)
view = pg.GraphicsLayoutWidget()
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle(region)

plt = view.addPlot()

with open('systems.txt','r') as f:
    sys = eval(f.read())

with open('regions.txt','r') as f:
    regions = eval(f.read())

for k,v in regions.items():
    if v['name'].lower() == region.lower():
        const_ids = v['constellations']
        break

s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))

systems = []
for k,v in sys.items():
    if v['constellation_id'] in const_ids:
        #p.append(np.array([v['position']['x']/div, v['position']['y']/div, v['position']['z']/div ], np.int64))
        d = {}
        x = v['position']['x']
        y = v['position']['y']
        if x <= 0:
            posx = 0-log(0-x)
        else:
            posx = log(x)
        if y <= 0:
            posy = 0-log(0-y)
        else:
            posy = log(y)

        d['pos'] = np.array([posx, posy])
        d['data'] = 1
        systems.append(d)
print(len(systems))

s1.addPoints(systems)

plt.addItem(s1)

lastClicked = []
def clicked(plot, points):
    global lastClicked
    for p in lastClicked:
        p.resetPen()
    print("clicked points", points)
    for p in points:
        p.setPen('b', width=2)

        print(p)
        print(dir(p))
        print(p.data)
        print(p.size)
        print(p.symbol)

    lastClicked = points
s1.sigClicked.connect(clicked)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

