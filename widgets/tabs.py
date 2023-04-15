import sys
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
)


class UiTabs(QWidget):
    def __init__(self, parent):
        super().__init__()
        # Create a tab widget
        self.tab_widget = QTabWidget()

        # # Set the tab widget as the central widget of the main window
        # self.setCentralWidget(self.tab_widget)
        self.setParent(parent=parent)

    def create_new_tab(self, tab_name, tab_widget: QWidget):
        # Add new tab to the tab widget
        self.tab_widget.addTab(tab_widget, tab_name)

        return self.tab_widget.currentIndex + 1

    def close_tab(self, tab_index):
        self.tab_widget.removeTab(tab_index)

        return True
