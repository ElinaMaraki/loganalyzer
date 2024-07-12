import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a button to trigger file selection
        self.select_file_button = QPushButton('Select CSV File', self)
        self.select_file_button.clicked.connect(self.select_csv_file)
        self.select_file_button.setGeometry(50, 50, 200, 30)

    def select_csv_file(self):
        options = QFileDialog.Options()
        # Set the dialog to accept only CSV files
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            print("Selected CSV File:", file_name)
            # Do something with the selected file, such as loading data from it

def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.setGeometry(100, 100, 300, 200)
    window.setWindowTitle('CSV File Selector')
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



#chat
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