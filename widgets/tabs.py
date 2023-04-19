import sys, os
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
    QPushButton,
)
from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect, Qt
from widgets.tab import UiTab


class UiTabs(QTabWidget):
    def __init__(self, mainwindow):
        super().__init__(movable=True, tabsClosable=True, usesScrollButtons=True)
        self.mainwindow = mainwindow
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setStyleSheet('font: 75 bold 20pt "Courier New";')
        self.new_tab_btn.clicked.connect(self.create_new_tab)

        self.setTabShape(self.Rounded)
        self.setCornerWidget(self.new_tab_btn, corner=Qt.TopRightCorner)
        self.setStyleSheet("background-color: transparent;")

        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, index):
        # Get the widget at the specified index
        widget = self.widget(index)
        # Remove the tab and its associated widget
        self.removeTab(index)
        widget.deleteLater()

        if self.count() == 0:
            self.mainwindow.close()

    def create_new_tab(self, tab_name=os.getcwd(), tab_widget: QWidget = UiTab):
        # Add new tab to the tab widget
        tab = tab_widget(self, self.mainwindow, tab_index=self.currentIndex() + 1)
        self.addTab(tab, tab_name)

        return self.currentIndex() + 1

    def close_tab(self, tab_index):
        self.removeTab(tab_index)

        return True
