import subprocess
import sys
import os

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from widgets.tab import UiTab
from widgets.tabs import UiTabs
from widgets.settings import Settings
from utils.config import load_settings, setup_vortex


class SideBar(QDockWidget):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent, Qt.FramelessWindowHint)
        self.parent = parent
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.settings = Settings(mainwindow=self.parent)
        self.setWidget(self.settings)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.parent.side_bar_btn.setVisible(True)
        return super().closeEvent(event)


class Terminal(QMainWindow):
    ctrl_c_clicked = Signal(bool)
    windowResized = Signal(QSize)

    def __init__(self, parent=None):
        super(Terminal, self).__init__(parent)

        setup_vortex()
        settings = load_settings()

        # Create a layout to hold the widgets
        self.tabs = UiTabs(self)
        # self.setWindowOpacity(0.9)
        self.setGeometry(QRect(200, 100, 960, 640))
        # self.setStyleSheet(
        #     "color: rgb(255, 255, 255);\n" "background-color: rgb(33, 83, 83);"
        # )

        self.background_pixmap = QPixmap(settings["bg_image"])

        self.overlay_color = QColor(*settings["theme_color"], 150)
        self.overlay_pixmap = QPixmap(QSize(self.width() * 2, self.height() * 2))
        self.overlay_pixmap.fill(self.overlay_color)

        # Set the composition mode to source-over
        painter = QPainter(self.background_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, self.overlay_pixmap)
        painter.end()

        palette = QPalette()
        palette.setBrush(
            QPalette.Background,
            self.background_pixmap.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            ),
        )
        self.setPalette(palette)

        self.tabs.create_new_tab(os.getcwd(), UiTab)
        self.setCentralWidget(self.tabs)

        self.side_bar_btn = QPushButton(text="˅", parent=self)
        self.side_bar_btn.setGeometry(2, 1, self.width() - 910, self.height() - 620)
        self.side_bar_btn.setStyleSheet('font: 75 bold 20pt "Courier New";')
        self.side_bar_btn.clicked.connect(self.open_side_bar)
        self.side_bar = SideBar(self)
        self.side_bar.setVisible(False)
        self.side_bar.setFixedWidth(self.width() / 4)
        self.side_bar.dockLocationChanged.connect(self.handle_dock_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_bar)

        shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut.activated.connect(self.cancel_process)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.windowResized.emit(event.size())
        self.side_bar_btn.setGeometry(2, 1, 50, 20)
        self.side_bar.setGeometry(0, 0, self.width() / 4, self.height())
        return super().resizeEvent(event)

    def cancel_process(self):
        self.ctrl_c_clicked.emit(True)

    def open_side_bar(self):
        self.side_bar.setVisible(True)
        self.side_bar_btn.setVisible(False)

    def handle_dock_widget(self):
        if self.side_bar.isFloating() and not self.side_bar.isVisible():
            self.side_bar_btn.setVisible(True)

    def restart(self):
        self.close()
        new_instance = Terminal()
        new_instance.show()


if __name__ == "__main__":
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create a Terminal instance
    terminal = Terminal()

    # Show the Terminal widget
    terminal.show()

    # Run the event loop of the application
    sys.exit(app.exec_())
