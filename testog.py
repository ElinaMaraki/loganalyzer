import csv
import sys
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QScrollBar, QLineEdit, QTextEdit, QLabel, QAction, QWidget, QVBoxLayout, QScrollArea,
    QCheckBox, QFileDialog, QDialog, QPushButton
)
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
from PyQt5.QtCore import Qt
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess


class Decoder(QDialog):
    def __init__(self):
        super().__init__()
        self.decoderUI()

    def decoderUI(self):
        self.setWindowTitle("Log Decoder")
        self.resize(900, 600)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Select File Button
        self.buttonSelFile = QPushButton("Select File", self)
        self.buttonSelFile.clicked.connect(self.select_file)
        layout.addWidget(self.buttonSelFile)
        # File Locarion Label
        self.file_laber = QLabel("Selected File:", self)
        layout.addWidget(self.file_laber)
        # Selected File Location
        self.entry_input_file = QLineEdit(self)
        layout.addWidget(self.entry_input_file)
        # Threshold Label
        self.label_threshold = QLabel("Threshold Value:", self)
        layout.addWidget(self.label_threshold)
        # Threshold Field
        self.entry_threshold = QLineEdit(self)
        layout.addWidget(self.entry_threshold)
        # Output File Label
        self.label_output_file = QLabel("Output File Name:", self)
        layout.addWidget(self.label_output_file)
        # Ouput File Field
        self.entry_output_file = QLineEdit(self)
        layout.addWidget(self.entry_output_file)
        # Run Program Button and Action
        self.button_run_program = QPushButton("Run Program", self)
        self.button_run_program.clicked.connect(self.run_cpp_program)
        layout.addWidget(self.button_run_program)

        # Create a scroll area for the text widget
        self.scroll_area = QScrollArea()
        layout.addWidget(self.scroll_area)

        # Create a widget to contain the text widget
        self.text_widget_container = QWidget()
        self.text_widget_layout = QVBoxLayout()
        self.text_widget_container.setLayout(self.text_widget_layout)
        self.text_widget = QTextEdit(self)
        self.text_widget.setStyleSheet("background-color: black; color: white;")
        self.text_widget.setReadOnly(True)
        self.text_widget_layout.addWidget(self.text_widget)
        self.scroll_area.setWidget(self.text_widget_container)
        # Allow the text widget to resize with the scroll area
        self.scroll_area.setWidgetResizable(True)

        # Create scrollbar
        self.scrollbar = QScrollBar()
        self.scroll_area.setVerticalScrollBar(self.scrollbar)

    def run_cpp_program(self):
        input_file_path = self.entry_input_file.text()
        threshold_value = self.entry_threshold.text()
        output_file_name = self.entry_output_file.text()

        command = [" ./Parser.exe", input_file_path, threshold_value, output_file_name + ".csv"]
        print(command)
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
        self.checked_vars = {}
        self.plotDict = {}
        self.checkboxes = []
        self.count = 0
        self.selected_csv_file = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Log Analyzer')
        self.resize(900, 600)
        # Create DockArea to arrange widgets within main window
        self.area = DockArea()
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
        # Create graphics layout widget for plots
        self.w2 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
        # Add widget to plots dock
        d2.addWidget(self.w2)

    def select_csv_file(self):
        self.clear_plots()
        options = QFileDialog.Options()
        # Set the dialog to accept only CSV files
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            print("Selected CSV File:", file_name)

            with open(file_name, newline='') as f:
                reader = csv.reader(f)
                first_row = next(reader)

                for item in first_row:
                    self.lists_dict[item] = []

                for row in reader:
                    for i in range(len(row)):
                        try:
                            self.lists_dict[first_row[i]].append(float(row[i]))
                        except:
                            self.lists_dict[first_row[i]].append(float(0))

        def func1(a, c):
            if (c == 0):
                self.w2.removeItem(self.plotDict[a])
                self.count = self.count - 1
                if (self.count == 0):
                    self.plotDict["vtime"].show()
            else:
                self.plotDict[a] = self.w2.addPlot(title=a)
                y = self.lists_dict[a]
                x = (self.lists_dict['vtime'])[0:len(y)]
                self.plotDict[a].setXLink(self.plotDict["vtime"])
                self.plotDict[a].plot(x, y)
                self.plotDict[a].showGrid(x=True, y=True)
                # plotDict[a].setXRange(min(lists_dict['vtime']), max(lists_dict['vtime']), padding=0)
                self.w2.nextRow()
                self.count = self.count + 1
                self.plotDict["vtime"].hide()
                vb = self.plotDict[a].vb
                vLine = pg.InfiniteLine(angle=90, movable=False)
                self.plotDict[a].addItem(vLine, ignoreBounds=True)

                # def mouseMoved(evt):
                #     pos = evt[0]  # Get the position of the mouse cursor
                #     # Convert mouse cursor position to coordinates in the plot
                #     # pos = self.plotDict[a].getViewBox().mapSceneToView(pos)
                #     mousepoint=self.plotDict[a].vb.mapSceneToView(pos)
                #     # Update the position of the vertical and horizontal lines
                #     # vLine.setPos(pos.x())
                #     x = mousepoint.x()
                #     y_list = []
                #     for plot in self.plotDict:
                #         y_pos = self.lists_dict[plot]
                #         y_pos.append(y_list)
                #
                #     print(f"Mouse at x={x}: {y_list}")
                #
                # # Connect the mouseMoved function to mouse movement events
                # proxy = pg.SignalProxy(self.plotDict[a].scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
                #
                # # Enable mouse interaction
                # self.plotDict[a].setMouseEnabled(x=True, y=True)

                def mouseMoved(evt):
                    pos = evt
                    if self.plotDict[a].sceneBoundingRect().contains(pos):
                        mousePoint = vb.mapSceneToView(pos)
                        index = int(mousePoint.x())
                        if index > 0 and index < len(y):
                            self.label.setText(
                                "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>" % (
                                    mousePoint.x(), y[index]))
                        vLine.setPos(mousePoint.x())

                self.plotDict[a].scene().sigMouseMoved.connect(mouseMoved)


        # Add checkboxes from csv
        i = 0
        for title in first_row:
            if title == "vtime":
                continue
            # When checked plot
            self.checkboxes.append(QCheckBox(title))
            self.checkboxes[-1].stateChanged.connect(partial(func1, title))
            self.w1Layout.addWidget(self.checkboxes[-1])
            i = i + 1

        # Initial plot of vtime to use for each plot
        self.plotDict["vtime"] = self.w2.addPlot()  # to link axes
        self.plotDict["vtime"].plot(self.lists_dict['vtime'], [0] * len(self.lists_dict['vtime']))
        self.plotDict["vtime"].showGrid(x=True, y=True)
        self.w2.nextRow()

    def close_file(self):
        self.lists_dict.clear()
        self.w2.clear()

        for checkbox in self.checkboxes:
            checkbox.deleteLater()

        self.checkboxes.clear()

    def clear_plots(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        open_csv_action = QAction('Open CSV', self)
        open_csv_action.triggered.connect(self.select_csv_file)
        file_menu.addAction(open_csv_action)

        clear_action = QAction('Clear Plots', self)
        clear_action.triggered.connect(self.clear_plots)
        file_menu.addAction(clear_action)

        close_action = QAction('Close File', self)
        close_action.triggered.connect(self.close_file)
        file_menu.addAction(close_action)

        new_window_action = QAction('Decode Log', self)
        new_window_action.triggered.connect(lambda: Decoder().exec_())
        file_menu.addAction(new_window_action)

        group_menu = menu_bar.addMenu('Plot By Group')

        plot_BMS_action = QAction('BMS', self)
        # plot_BMS_action.triggered.connect(self.plot_BMS)
        group_menu.addAction(plot_BMS_action)

        plot_Temp_action = QAction('Temp', self)
        # plot_Temp_action.triggered.connect(self.plot_Temp)
        group_menu.addAction(plot_Temp_action)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    log_analyzer = LogAnalyzerApp()
    log_analyzer.show()
    sys.exit(app.exec_())