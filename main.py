import subprocess
import sys
import os

from PySide2 import QtCore, QtWidgets
from widgets.tab import UiTab
from widgets.tabs import UiTabs


class Terminal(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Terminal, self).__init__(parent)

        # Create a layout to hold the widgets
        self.tabs = UiTabs(self)
        self.setWindowOpacity(0.9)
        self.setGeometry(QtCore.QRect(200, 100, 960, 640))
        self.setStyleSheet(
            "color: rgb(255, 255, 255);\n" "background-color: rgb(33, 83, 83);"
        )

        self.tabs.create_new_tab(os.getcwd(), UiTab)
        # Set the layout for the widget
        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    # Create a QApplication instance
    app = QtWidgets.QApplication(sys.argv)

    # Create a Terminal instance
    terminal = Terminal()

    # Show the Terminal widget
    terminal.show()

    # Run the event loop of the application
    sys.exit(app.exec_())
