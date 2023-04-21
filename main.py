import subprocess
import sys
import os

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from widgets.tab import UiTab
from widgets.tabs import UiTabs

background_path = "images/background.jpg"


class Terminal(QMainWindow):
    ctrl_c_clicked = Signal(bool)

    def __init__(self, parent=None):
        super(Terminal, self).__init__(parent)

        # Create a layout to hold the widgets
        self.tabs = UiTabs(self)
        # self.setWindowOpacity(0.9)
        self.setGeometry(QRect(200, 100, 960, 640))
        # self.setStyleSheet(
        #     "color: rgb(255, 255, 255);\n" "background-color: rgb(33, 83, 83);"
        # )

        background_pixmap = QPixmap(background_path)

        overlay_color = QColor(7, 23, 26, 230)
        overlay_pixmap = QPixmap(QSize(960, self.height() * 2))
        overlay_pixmap.fill(overlay_color)

        # Set the composition mode to source-over
        painter = QPainter(background_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, overlay_pixmap)
        painter.end()

        palette = QPalette()
        palette.setBrush(
            QPalette.Background,
            background_pixmap.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            ),
        )
        self.setPalette(palette)

        self.tabs.create_new_tab(os.getcwd(), UiTab)
        self.setCentralWidget(self.tabs)

        shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut.activated.connect(self.cancel_process)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # if event.key() == Qt.Key_C:
        #     print(event.modifiers() == Qt.ControlModifier)

        return super().keyPressEvent(event)

    def cancel_process(self):
        self.ctrl_c_clicked.emit(True)


if __name__ == "__main__":
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create a Terminal instance
    terminal = Terminal()

    # Show the Terminal widget
    terminal.show()

    # Run the event loop of the application
    sys.exit(app.exec_())
