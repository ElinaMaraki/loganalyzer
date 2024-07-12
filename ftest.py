import csv
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore
from functools import partial
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QAction

# from pyqtgraph.examples.crosshair import vLine, hLine

lists_dict = {}
checked_vars = {}
count = 0
plotDict = {}
selected_csv_file = None
checkboxes = []

# Set up GUI

app = pg.mkQApp("Loganalyzer")
# Create main window
win = pg.Qt.QtWidgets.QMainWindow()
# Create DockArea to arrange widgets within main window
area = DockArea()
# Set main widget for plots in area
win.setCentralWidget(area)
win.resize(1000, 500)
win.setWindowTitle('Loganalyzer elina')

# Create Widgets
# window/dock for checkboxes

d1 = Dock("Options", size=(120, 1))
d1.hideTitleBar()
# window/dock for plots
d2 = Dock("Graphs", size=(500, 300))
d2.hideTitleBar()
# Add and  position Widgets in DockArea
area.addDock(d1, 'left')
area.addDock(d2, 'right')

# Enable antialiasing for smoother plots
pg.setConfigOptions(antialias=True)

# CREATE CHECKBOX AREA AND SCROLLBAR

# Create widget to add scrollbar in
w1 = QtWidgets.QWidget()
# Create scrollable area for checkboxes
w1Layout = QtWidgets.QVBoxLayout()
w1.setLayout(w1Layout)
# Create scrollbar area
scrollbar = QtWidgets.QScrollArea(widgetResizable=True)
scrollbar.setWidget(w1)
# Add scrollbar to checkboxes
d1.addWidget(scrollbar)

w1Layout.addStretch(1)  # Stretch to align all QVBox checkboxes to the top

# Create graphics layout widget for plots
w2 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
# Add widget to plots dock
d2.addWidget(w2)


# Define a function to handle mouse movement events
label = pg.LabelItem(justify='right')

# Show the window
win.show()


# When CSV imported
def select_csv_file():
    global selected_csv_file
    clear_plots()
    options = QFileDialog.Options()
    # Set the dialog to accept only CSV files
    file_name, _ = QFileDialog.getOpenFileName(None, "Select CSV File", "", "CSV Files (*.csv)", options=options)
    if file_name:
        print("Selected CSV File:", file_name)

        with open(file_name, newline='') as f:
            reader = csv.reader(f)
            first_row = next(reader)

            for item in first_row:
                lists_dict[item] = []

            for row in reader:
                for i in range(len(row)):
                    try:
                        lists_dict[first_row[i]].append(float(row[i]))
                    except:
                        lists_dict[first_row[i]].append(float(0))

        def func1(a, c):
            global count
            if (c == 0):
                w2.removeItem(plotDict[a])
                count = count - 1
                if (count == 0):
                    plotDict["vtime"].show()
            else:
                plotDict[a] = w2.addPlot(title=a)
                y = lists_dict[a]
                x = (lists_dict['vtime'])[0:len(y)]
                plotDict[a].setXLink(plotDict["vtime"])
                plotDict[a].plot(x, y)
                plotDict[a].showGrid(x=True, y=True)
                # plotDict[a].setXRange(min(lists_dict['vtime']), max(lists_dict['vtime']), padding=0)
                w2.nextRow()
                count = count + 1
                plotDict["vtime"].hide()
                vLine = pg.InfiniteLine(angle=90, movable=False)
                plotDict[a].addItem(vLine, ignoreBounds=True)
                vb = plotDict[a].vb
                plotDict[a].addItem(label)
                # def mouseMoved(evt):
                #     pos = evt[0]  # Get the position of the mouse cursor
                #     # Convert mouse cursor position to coordinates in the plot
                #     pos = plotDict[a].getViewBox().mapSceneToView(pos)
                #     # Update the position of the vertical and horizontal lines
                #     vLine.setPos(pos.x())
                #     # Display the current values at the mouse cursor position
                #     # You can customize this according to your data
                #     print("Mouse moved to:", pos.x(), pos.y())
                #
                # # Connect the mouseMoved function to mouse movement events
                # proxy = pg.SignalProxy(plotDict[a].scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
                #
                # # Enable mouse interaction
                # plotDict[a].mouseEnabled(x=True, y=True)
                # Create Label for Mouse

                # def mouseMoved(evt):
                #     pos = evt
                #     if plotDict[a].sceneBoundingRect().contains(pos):
                #         mousePoint = vb.mapSceneToView(pos)
                #         index = int(mousePoint.x())
                #         if index > 0 and index < len(y):
                #             label.setText(
                #                 "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>" % (
                #                     mousePoint.x(), y[index]))
                #         vLine.setPos(mousePoint.x())
                #
                # plotDict[a].scene().sigMouseMoved.connect(mouseMoved)

        # Add checkboxes from csv
        i = 0
        for title in first_row:
            if (title == "vtime"):
                continue
            # When checked plot
            checkboxes.append(QtWidgets.QCheckBox(title))
            checkboxes[-1].stateChanged.connect(partial(func1, title))
            w1Layout.addWidget(checkboxes[-1])
            i = i + 1

        # Initial plot of vtime to use for each plot
        plotDict["vtime"] = w2.addPlot()  # to link axes
        plotDict["vtime"].plot(lists_dict['vtime'], [0] * len(lists_dict['vtime']))
        plotDict["vtime"].showGrid(x=True, y=True)
        w2.nextRow()


def clear_plots():
    global selected_csv_file
    selected_csv_file = None
    lists_dict.clear()

    # Clear all plots from GraphicsLayoutWidget
    w2.clear()
    plotDict.clear()

    for checkbox in checkboxes:
        w1Layout.removeWidget(checkbox)
        checkbox.deleteLater()
    checkboxes.clear()


# Create actions for menu
def create_menu():
    menu = win.menuBar()
    file_menu = menu.addMenu('File')

    open_csv_action = QAction('Open CSV', win)
    open_csv_action.triggered.connect(select_csv_file)
    file_menu.addAction(open_csv_action)

    clear_action = QAction('Clear', win)
    clear_action.triggered.connect(clear_plots)
    file_menu.addAction(clear_action)


if __name__ == "__main__":
    create_menu()
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()


