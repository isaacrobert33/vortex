import sys
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
)
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect


class UiTabs(QTabWidget):
    def __init__(self, mainwindow):
        super().__init__()

        self.mainwindow = mainwindow

    def create_new_tab(self, tab_name, tab_widget: QWidget):
        # Add new tab to the tab widget
        tab = tab_widget(self, self.mainwindow)
        self.addTab(tab, tab_name)

        return self.currentIndex() + 1

    def close_tab(self, tab_index):
        self.removeTab(tab_index)

        return True
