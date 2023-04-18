import sys
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
    QPushButton,
)
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect, Qt


class UiTabs(QTabWidget):
    def __init__(self, mainwindow):
        super().__init__(movable=True, tabsClosable=True, usesScrollButtons=True)
        self.mainwindow = mainwindow
        self.new_tab_btn = QPushButton("+")

        self.setTabShape(self.Rounded)
        self.setCornerWidget(self.new_tab_btn, corner=Qt.TopRightCorner)
        self.setStyleSheet("background-color: transparent;")

    def create_new_tab(self, tab_name, tab_widget: QWidget):
        # Add new tab to the tab widget
        tab = tab_widget(self, self.mainwindow)
        self.addTab(tab, tab_name)

        return self.currentIndex() + 1

    def close_tab(self, tab_index):
        self.removeTab(tab_index)

        return True
