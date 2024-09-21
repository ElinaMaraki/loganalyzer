import colorsys
import csv
import sys
import numpy as np
from functools import partial
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QScrollBar, QLineEdit, QTextEdit, QLabel, QAction, QWidget, QVBoxLayout, QScrollArea,
    QCheckBox, QFileDialog, QDialog, QPushButton, QGraphicsProxyWidget, QHBoxLayout, QSplitter
)
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
from PyQt5.QtCore import Qt
import subprocess
import re
import random


class Decoder(QDialog):
    def __init__(self):
        super().__init__()
        self.entry_threshold = QLineEdit(self)
        self.entry_input_file = QLineEdit(self)
        self.entry_output_file = QLineEdit(self)
        self.text_widget = QTextEdit(self)
        self.decoderUI()

    def decoderUI(self):
        self.setWindowTitle("Log Decoder")
        self.resize(900, 600)
        self.setStyleSheet("background-color: #2E2E2E; color:white;")
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Select File Button
        buttonSelFile = QPushButton("Select File", self)
        buttonSelFile.clicked.connect(self.select_file)
        layout.addWidget(buttonSelFile)
        # File Location Label
        file_label = QLabel("Selected File:", self)
        layout.addWidget(file_label)
        # Selected File Location
        layout.addWidget(self.entry_input_file)
        # Threshold Label
        label_threshold = QLabel("Threshold Value:", self)
        layout.addWidget(label_threshold)
        # Threshold Field
        layout.addWidget(self.entry_threshold)
        # Output File Label
        label_output_file = QLabel("Output File Name:", self)
        layout.addWidget(label_output_file)
        # Output File Field
        layout.addWidget(self.entry_output_file)
        # Run Program Button and Action
        button_run_program = QPushButton("Run Program", self)
        button_run_program.clicked.connect(self.run_cpp_program)
        layout.addWidget(button_run_program)

        # Create a scroll area for the text widget
        scroll_area = QScrollArea()
        layout.addWidget(scroll_area)

        # Create a widget to contain the text widget
        text_widget_container = QWidget()
        text_widget_layout = QVBoxLayout()
        text_widget_container.setLayout(text_widget_layout)
        self.text_widget.setStyleSheet("background-color: black; color: white;")
        self.text_widget.setReadOnly(True)
        text_widget_layout.addWidget(self.text_widget)
        scroll_area.setWidget(text_widget_container)
        # Allow the text widget to resize with the scroll area
        scroll_area.setWidgetResizable(True)

        # Create scrollbar
        scrollbar = QScrollBar()
        scroll_area.setVerticalScrollBar(scrollbar)

    def run_cpp_program(self):
        input_file_path = self.entry_input_file.text()
        threshold_value = self.entry_threshold.text()
        output_file_name = self.entry_output_file.text()

        command = ["Parser.exe", input_file_path, str(threshold_value), output_file_name + ".csv"]
        print(f"Executing command: {command}")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
            while True:
                output_line = process.stdout.readline()
                if not output_line:
                    break
                self.text_widget.append(output_line)
                self.text_widget.ensureCursorVisible()
            process.wait()
            self.text_widget.append("CSV created.\n")
        except Exception as e:
            self.text_widget.append(f"Error running C++ program: {str(e)}\n")

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text files (*.txt)")
        if file:
            self.entry_input_file.setText(file)


class LogAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lists_dict = {}
        self.flags_list = {}
        self.checked_vars = {}
        self.plotDict = {}
        self.checkboxes = []
        self.container = False
        self.count = 0
        self.selected_csv_file = None
        self.Flags = ['System Safe', 'Over Voltage','Under Voltage','Over Temp Cells', 'Under Temp Cells',
                    'Abnormality Error', 'Voltage Abnormality', 'Temp Abnormality', 'Voltage Sampling Abnormality',
                    'Temperature Sampling Abnormality', 'Over Current', 'Under Current', 'IVT Preset',
                    'Shutdown Status', 'BMS Shutdown', 'Is Precharged']
        self.binary_dict = {flag: [] for flag in self.Flags}
        self.mode = 0
        self.file_name = ""
        self.vb_dict = {}   # Store references to the view boxes
        self.vLines = {}
        self.mouseMovedConnections = {}  # Store the signal connections for each plot

        # Initialize w1Layout as a QVBoxLayout
        self.w1Layout = QVBoxLayout()
        # Create DockArea to arrange widgets within main window
        self.area = DockArea()
        self.splitter = QSplitter()
        # Create graphics layout widget for plots
        self.w2 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
        # values label
        self.param_label = QLabel("Parameter Values")
        self.label_text = QtWidgets.QTextEdit()
        self.label_text.setReadOnly(True)
        # same for bms flags
        self.flags_label = QLabel("Flags Values")
        self.flags_text = QtWidgets.QTextEdit()
        self.flags_text.setReadOnly(True)
        # Container
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_widget.setLayout(self.container_layout)

        # Add flags and values to container
        self.container_layout.addWidget(self.param_label)
        self.container_layout.addWidget(self.label_text)
        self.container_layout.addWidget(self.flags_label)
        self.container_layout.addWidget(self.flags_text)

        self.label_text2 = QtWidgets.QTextEdit()
        self.label_text2.setReadOnly(True)

        self.container_widget2 = QWidget()
        self.container2_layout = QVBoxLayout()
        self.container_widget2.setLayout(self.container2_layout)

        # Add flags and values to container
        self.container2_layout.addWidget(self.label_text2)

        self.mouseMovedConnection = None
        self.values = []
        self.flags_values = []
        self.select_all_button = QPushButton('Check All')
        self.unselect_all_button = QPushButton('Uncheck All')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Log Analyzer')
        self.resize(900, 600)
        self.setStyleSheet("background-color: #2E2E2E; color:white;")
        # Set main widget for plots in area
        self.setCentralWidget(self.area)

        # Create docks
        self.create_checkboxes_dock()
        self.create_graphs_dock()

        # Create menu bar
        self.create_menu_bar()

    def create_checkboxes_dock(self):
        # window/dock for checkboxes
        d1 = Dock("Options", size=(120, 1))
        d1.hideTitleBar()
        # Add and position Widget in DockArea
        self.area.addDock(d1, 'left')

        # Create widget to add scrollbar in
        w1 = QWidget()
        # Create scrollable area for checkboxes
        w1Layout = QVBoxLayout()
        w1.setLayout(w1Layout)
        # Create scrollbar area
        scrollbar = QScrollArea(widgetResizable=True)
        scrollbar.setWidget(w1)
        # Add scrollbar to checkboxes
        d1.addWidget(scrollbar)

        self.w1Layout = w1Layout

    def create_graphs_dock(self):
        # window/dock for plots
        d2 = Dock("Graphs", size=(500, 300))
        d2.hideTitleBar()
        # Add and position Widget in DockArea
        self.area.addDock(d2, 'right')
        # Add widget to plots dock

        # Create a main widget to hold both plot and container
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        main_layout.addWidget(self.splitter)

        # Add plot widget and container widget to the main layout
        self.splitter.addWidget(self.w2)
        d2.addWidget(main_widget)

    def select_csv_file(self):
        options = QFileDialog.Options()
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;TXT Files (*.txt)", options=options)

        if self.file_name:
            self.initialization()

    def initialization(self):
        if self.file_name:
            print("Selected CSV File:", self.file_name)

            with open(self.file_name, 'rb') as f:
                content = f.read().replace(b'\x00', b'')
                # reader = csv.reader(f)
                # first_row = next(reader)

            content = content.decode('utf-8')
            reader = csv.reader(content.splitlines())
            first_row = next(reader)

            if self.mode == 0:
                for item in first_row:
                    self.lists_dict[item] = []

                for row in reader:
                    for i in range(len(row)):
                        try:
                            self.lists_dict[first_row[i]].append(float(row[i]))
                        except:
                            self.lists_dict[first_row[i]].append(float(0))

            elif self.mode == 1:
                pattern = re.compile(r'Cell #\d+|vtime')
                flags_pattern = re.compile(r'BMSFlags|vtime')

                for item in first_row:
                    if pattern.match(item):
                        self.lists_dict[item] = []
                    if flags_pattern.match(item):
                        self.flags_list[item] = []

                for item in self.Flags:
                    self.flags_list[item] = []

                for row in reader:
                    for i, item in enumerate(first_row):
                        if pattern.match(item):
                            try:
                                self.lists_dict[item].append(float(row[i]))
                            except:
                                self.lists_dict[item].append(float(0))
                        if flags_pattern.match(item):
                            try:
                                self.flags_list[item].append(float(row[i]))
                            except:
                                self.flags_list[item].append(float(0))

                self.process_BMSFlags()

            elif self.mode == 2:
                pattern = re.compile(r'Therm #\d+|vtime')
                flags_pattern = re.compile(r'BMSFlags|vtime')

                for item in first_row:
                    if pattern.match(item):
                        self.lists_dict[item] = []
                    if flags_pattern.match(item):
                        self.flags_list[item] = []

                for item in self.Flags:
                    self.flags_list[item] = []

                for row in reader:
                    for i, item in enumerate(first_row):
                        if pattern.match(item):
                            try:
                                self.lists_dict[item].append(float(row[i]))
                            except:
                                self.lists_dict[item].append(float(0))
                        if flags_pattern.match(item):
                            try:
                                self.flags_list[item].append(float(row[i]))
                            except:
                                self.flags_list[item].append(float(0))

                self.process_BMSFlags()

            elif self.mode == 3:
                pattern = re.compile(r'LV_AMS_.+|vtime')

                for item in first_row:
                    if pattern.match(item):
                        self.lists_dict[item] = []

                for row in reader:
                    for i, item in enumerate(first_row):
                        if pattern.match(item):
                            try:
                                self.lists_dict[item].append(float(row[i]))
                            except:
                                self.lists_dict[item].append(float(0))

            elif self.mode == 4:
                pattern = re.compile(r'BMSFlags|vtime')

                for item in first_row:
                    if pattern.match(item):
                        self.lists_dict[item] = []
                for item in self.Flags:
                    self.lists_dict[item] = []

                for row in reader:
                    for i, item in enumerate(first_row):
                        if pattern.match(item):
                            try:
                                self.lists_dict[item].append(float(row[i]))
                            except:
                                self.lists_dict[item].append(float(0))

                self.process_BMSFlags()

        def create_graphs(a, c):
            if self.mode == 0 or self.mode == 3 or self.mode == 4:
                if c == 0:
                    self.w2.removeItem(self.plotDict[a])
                    vLine = self.vLines.pop(a, None)
                    if vLine is not None:
                        vLine.setParent(None)
                    del self.plotDict[a]
                    self.values = [row for row in self.values if row[0] != a]
                    self.count = self.count - 1
                    if self.count == 0:
                        self.label_text2.setHtml('')
                        self.container_widget2.setParent(None)
                        self.disconnect_all_cursors()
                        self.container = False
                        self.plotDict["vtime"].show()

                else:
                    self.plotDict[a] = self.w2.addPlot(title=a)
                    y = self.lists_dict[a]
                    x = (self.lists_dict['vtime'])[0:len(y)]
                    self.plotDict[a].setXLink(self.plotDict["vtime"])
                    col = colorsys.hsv_to_rgb(random.uniform(0, 1), random.uniform(0.5, 1), random.uniform(0.7, 1))
                    col = tuple(int(255 * c) for c in col)
                    pen = pg.mkPen(color=tuple(col))
                    self.plotDict[a].plot(x, y, pen=pen)
                    self.plotDict[a].showGrid(x=True, y=True)
                    self.w2.nextRow()
                    self.count = self.count + 1
                    self.plotDict["vtime"].hide()

                    self.add_line(a)

                    if not self.container:
                        self.cursor1()
                        self.splitter.addWidget(self.container_widget2)
                        self.splitter.setStretchFactor(0, 3)
                        self.splitter.setStretchFactor(1, 1)
                        self.container = True

            elif self.mode == 1 or self.mode == 2:
                if c == 0:
                    if a in self.plotDict:
                        self.plotDict['mainPlot'].removeItem(self.plotDict[a])
                        del self.plotDict[a]
                        for row in self.values:
                            if row[0] == a:
                                self.values.remove(row)
                        self.count -= 1
                        if self.count == 0:
                            self.label_text.setHtml('')
                            self.flags_text.setHtml('')
                            self.container_widget.setParent(None)
                            self.disconnectCursor()
                            self.remove_mainPlot()
                            self.plotDict["vtime"].show()
                else:
                    if 'mainPlot' not in self.plotDict:
                        self.plotDict["vtime"].hide()
                        if self.mode == 1:
                            self.plotDict['mainPlot'] = self.w2.addPlot(title='Cells Plot')
                        elif self.mode == 2:
                            self.plotDict['mainPlot'] = self.w2.addPlot(title='Therms Plot')
                        self.plotDict['mainPlot'].showGrid(x=True, y=True)
                        self.plotDict['mainPlot'].setXLink(self.plotDict["vtime"])
                        self.splitter.addWidget(self.container_widget)
                        self.splitter.setStretchFactor(0, 3)
                        self.splitter.setStretchFactor(1, 1)
                        self.cursor()

                    y = self.lists_dict[a]
                    x = (self.lists_dict['vtime'])[0:len(y)]
                    col = colorsys.hsv_to_rgb(random.uniform(0, 1), random.uniform(0.5, 1), random.uniform(0.7, 1))
                    col = tuple(int(255 * c) for c in col)
                    pen = pg.mkPen(color=tuple(col))
                    if a in self.plotDict:
                        # Update existing line
                        self.plotDict[a].setData(x, y, pen=pen)
                    else:
                        # Add new line to plot
                        line = self.plotDict['mainPlot'].plot(x, y, name=a, pen=pen)
                        self.plotDict[a] = line
                    self.count += 1
                    self.plotDict["vtime"].hide()

        if self.mode == 1 or self.mode == 2:
            self.select_all_button.clicked.connect(self.select_all)
            self.w1Layout.addWidget(self.select_all_button)
            self.unselect_all_button.clicked.connect(self.unselect_all)
            self.w1Layout.addWidget(self.unselect_all_button)
        else:
            self.remove_check_all_buttons()

        # Add checkboxes from csv
        i = 0
        for item in self.lists_dict:
            if item == "vtime" or item == "BMSFlags":
                continue
            # When checked plot
            self.checkboxes.append(QCheckBox(item))
            self.checkboxes[-1].stateChanged.connect(partial(create_graphs, item))
            self.w1Layout.addWidget(self.checkboxes[-1])
            i = i + 1

        # Initial plot of vtime to use for each plot
        self.plotDict["vtime"] = self.w2.addPlot()  # link axes
        self.plotDict["vtime"].plot(self.lists_dict['vtime'], [0] * len(self.lists_dict['vtime']))
        self.plotDict["vtime"].showGrid(x=True, y=True)
        self.w2.nextRow()

    def cursor(self):
        plot_item = self.plotDict['mainPlot']
        vLine = pg.InfiniteLine(angle=90, movable=False)
        plot_item.addItem(vLine, ignoreBounds=True)

        vb = plot_item.vb

        def mouseMoved(evt):
            pos = evt
            if plot_item.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                index = int(mousePoint.x())
                new_index = min(self.lists_dict["vtime"], key=lambda x: abs(x - index))
                x = self.lists_dict["vtime"].index(new_index)
                for a in self.plotDict:
                    if a == 'vtime' or a == 'mainPlot':
                        continue
                    a_value = self.lists_dict[a][x]
                    found = False
                    for parameter in self.values:
                        if parameter[0] == a:
                            parameter[1] = a_value
                            found = True
                            break
                    if not found:
                        self.values.append([a, a_value])
                formatted_text = "<span style='font-size: 12pt'>vtime=%0.1f ms" % (mousePoint.x())
                formatted_text += "<br>" + "<br>".join([f"{a}: {value}" for a, value in self.values])

                for flag in self.flags_list:
                    if flag == 'vtime' or flag == 'BMSFlags':
                        continue
                    value = self.flags_list[flag][x]
                    found = False
                    for parameter in self.flags_values:
                        if parameter[0] == flag:
                            parameter[1] = value
                            found = True
                            break
                    if not found:
                        self.flags_values.append([flag, value])
                    flags_form_text = "<span style='font-size: 12pt'>vtime=%0.1f ms" % (mousePoint.x())
                    flags_form_text += "<br>" + "<br>".join([f"{flag}: {value}" for flag, value in self.flags_values])
                    self.flags_text.setHtml(flags_form_text)
                    self.label_text.setHtml(formatted_text)
                else:
                    self.label_text2.setHtml(formatted_text)

                vLine.setPos(mousePoint.x())

        self.mouseMovedConnection = plot_item.scene().sigMouseMoved.connect(mouseMoved)

    def disconnectCursor(self):
        if self.mouseMovedConnection is not None:
            self.plotDict['mainPlot'].scene().sigMouseMoved.disconnect(self.mouseMovedConnection)
            self.mouseMovedConnection = None

    def cursor1(self):
        """
        Initializes and adds a vertical cursor line to each plot.
        """
        self.vLines = {}  # Reinitialize the dictionary to store InfiniteLine instances
        self.vb_dict = {}  # Reinitialize the dictionary to store view boxes

        # Loop through each plot and add a cursor line
        for plot_name, plot_item in self.plotDict.items():
            if plot_name == 'vtime' or plot_name == 'mainPlot':
                continue

            # Create and store a new InfiniteLine for each plot
            vLine = pg.InfiniteLine(angle=90, movable=False)
            self.vLines[plot_name] = vLine

            # Add the line to the plot
            plot_item.addItem(vLine, ignoreBounds=True)

            # Store reference to the view box for this plot
            self.vb_dict[plot_name] = plot_item.vb

            # Connect the mouse-move signal for this plot
            self.mouseMovedConnections[plot_name] = plot_item.scene().sigMouseMoved.connect(
                self.mouseMoved_handler(plot_name))


    def add_line(self, plot_name):

        plot_item = self.plotDict[plot_name]

        vLine = pg.InfiniteLine(angle=90, movable=False)  # Recreate the InfiniteLine
        self.vLines[plot_name] = vLine

        # Add the single vertical line to each plot
        plot_item.addItem(vLine, ignoreBounds=True)

        # Store reference to the view box for each plot
        self.vb_dict[plot_name] = plot_item.vb

        # Connect mouse movement signal to the handler
        self.mouseMovedConnections[plot_name] = plot_item.scene().sigMouseMoved.connect(self.mouseMoved_handler(plot_name))

    def mouseMoved_handler(self, plot_name):
        return lambda evt: self.mouseMoved1(evt, plot_name)

    def mouseMoved1(self, evt, plot_name):
        pos = evt
        for plot_name, plot_item in self.plotDict.items():
            if plot_name == 'vtime' or plot_name == 'mainPlot':
                continue

            if plot_item.sceneBoundingRect().contains(pos):
                mousePoint = self.vb_dict[plot_name].mapSceneToView(pos)
                index = int(mousePoint.x())
                new_index = min(self.lists_dict["vtime"], key=lambda x: abs(x - index))
                x = self.lists_dict["vtime"].index(new_index)

                self.values = []  # Reset values for updated display
                for a in self.plotDict:
                    if a == 'vtime' or a == 'mainPlot':
                        continue

                    a_value = self.lists_dict[a][x]
                    self.values.append([a, a_value])

                formatted_text = "<span style='font-size: 12pt'>vtime=%0.1f ms" % (mousePoint.x())
                formatted_text += "<br>" + "<br>".join([f"{a}: {value}" for a, value in self.values])
                self.label_text2.setHtml(formatted_text)

                # Update vertical line position for each plot
                for i in self.vLines:
                    self.vLines[i].setPos(mousePoint.x())

    def disconnect_all_cursors(self):
        for plot_name, connection in list(self.mouseMovedConnections.items()):
            plot_item = self.plotDict.get(plot_name)
            if plot_item is not None:
                # Disconnect the signal connection for the specific plot
                plot_item.scene().sigMouseMoved.disconnect(connection)

        # Clear the mouseMovedConnections dictionary
        self.mouseMovedConnections.clear()

    def remove_check_all_buttons(self):
        if self.w1Layout.indexOf(self.select_all_button) != -1:
            self.w1Layout.removeWidget(self.select_all_button)
            self.select_all_button.setParent(None)

        if self.w1Layout.indexOf(self.unselect_all_button) != -1:
            self.w1Layout.removeWidget(self.unselect_all_button)
            self.unselect_all_button.setParent(None)

    def process_BMSFlags(self):
        if self.mode == 4:
            flist = self.lists_dict
        else:
            flist = self.flags_list

        if flist:
            for binary_float in flist['BMSFlags']:
                binary_int = int(binary_float)
                binary_str = str(binary_int)
                if len(binary_str) != 16:
                    for i in range(16):
                        flist[self.Flags[i]].append(0)
                else:
                    for i in range(16):
                        flist[self.Flags[i]].append(int(binary_str[i]))

    def remove_mainPlot(self):
        if 'mainPlot' in self.plotDict:
            self.plotDict['mainPlot'].clear()
            self.w2.removeItem(self.plotDict['mainPlot'])
            del self.plotDict['mainPlot']

    def all_plots(self):
        self.mode = 0
        if self.file_name:
            self.clear_all()
            self.initialization()
        else:
            self.select_csv_file()

    def new_csv(self):
        self.close_file()
        self.mode = 0
        self.select_csv_file()

    def plot_BMS(self):
        self.mode = 1
        if self.file_name:
            self.clear_all()
            self.initialization()
        else:
            self.select_csv_file()

    def plot_Temp(self):
        self.mode = 2
        if self.file_name:
            self.clear_all()
            self.initialization()
        else:
            self.select_csv_file()

    def plot_LV(self):
        self.mode = 3
        if self.file_name:
            self.clear_all()
            self.initialization()
        else:
            self.select_csv_file()

    def plot_Flags(self):
        self.mode = 4
        if self.file_name:
            self.clear_all()
            self.initialization()
        else:
            self.select_csv_file()

    def close_file(self):
        self.lists_dict.clear()
        self.w2.clear()
        self.clear_all()
        self.remove_check_all_buttons()

        for checkbox in self.checkboxes:
            checkbox.deleteLater()

        self.checkboxes.clear()
        self.file_name = ""

    def unselect_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    def select_all(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def clear_all(self):
        self.disconnectCursor()
        self.lists_dict.clear()
        self.flags_list.clear()
        self.plotDict.clear()
        self.values.clear()
        self.flags_values.clear()
        self.count = 0

        # Clear text widgets
        self.label_text.setHtml('')
        self.flags_text.setHtml('')

        # Clear all items from the GraphicsLayoutWidget
        self.w2.clear()
        self.container_widget2.setParent(None)
        self.container_widget.setParent(None)
        self.container = False

        for checkbox in self.checkboxes:
            checkbox.deleteLater()

        self.checkboxes.clear()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        open_csv_action = QAction('Open CSV', self)
        open_csv_action.triggered.connect(self.new_csv)
        file_menu.addAction(open_csv_action)

        clear_action = QAction('Clear Plots', self)
        clear_action.triggered.connect(self.unselect_all)
        file_menu.addAction(clear_action)

        close_action = QAction('Close File', self)
        close_action.triggered.connect(self.close_file)
        file_menu.addAction(close_action)

        new_window_action = QAction('Decode Log', self)
        new_window_action.triggered.connect(lambda: Decoder().exec_())
        file_menu.addAction(new_window_action)

        group_menu = menu_bar.addMenu('Plot By Group')

        revert_action = QAction('No Groups', self)
        revert_action.triggered.connect(self.all_plots)
        group_menu.addAction(revert_action)

        plot_BMS_action = QAction('BMS', self)
        plot_BMS_action.triggered.connect(self.plot_BMS)
        group_menu.addAction(plot_BMS_action)

        plot_Temp_action = QAction('Temp', self)
        plot_Temp_action.triggered.connect(self.plot_Temp)
        group_menu.addAction(plot_Temp_action)

        plot_LV_action = QAction('LV AMS', self)
        plot_LV_action.triggered.connect(self.plot_LV)
        group_menu.addAction(plot_LV_action)

        plot_flags_action = QAction('BMS Flags', self)
        plot_flags_action.triggered.connect(self.plot_Flags)
        group_menu.addAction(plot_flags_action)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    log_analyzer = LogAnalyzerApp()
    log_analyzer.show()
    sys.exit(app.exec_())
