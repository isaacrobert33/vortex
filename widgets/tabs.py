import sys
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
)
from PySide2.QtGui import QIcon


class UiTabs(QWidget):
    def __init__(self, parent):
        super().__init__()
        # Create a tab widget
        self.tab_widget = QTabWidget()
        self.setParent(parent)

    def create_new_tab(self, tab_name, tab_widget: QWidget):
        # Add new tab to the tab widget
        tab = tab_widget(self)
        self.tab_widget.addTab(tab, tab_name)

        return self.tab_widget.currentIndex() + 1

    def close_tab(self, tab_index):
        self.tab_widget.removeTab(tab_index)

        return True
