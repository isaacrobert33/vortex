from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import os


class DirectoryList(QWidget):
    dir_clicked = Signal(str)

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.item_list = QListWidget()
        self.layout.addWidget(self.item_list)
        self.setLayout(self.layout)
        # self.item_list.itemClicked.connect(self.handle_item_clicked)
        self.setStyleSheet(
            "background-color: rgb(14, 46, 52); border-top-left-radius: 5px; border-top-right-radius: 5px;"
        )
        self.setWindowOpacity(0.5)
        self.item_list.itemSelectionChanged.connect(self.on_item_selection)

    def handle_item_clicked(self, item):
        self.dir_clicked.emit(item.text())
        self.setVisible(False)

    def on_item_selection(self):
        current_item = self.item_list.currentItem()
        if current_item:
            self.dir_clicked.emit(current_item.text())

    def load_items(self, dir_list: list):
        for element in dir_list:
            item = QListWidgetItem(
                QIcon("images/file.svg")
                if os.path.isfile(element)
                else QIcon("images/folder.svg"),
                element,
            )
            self.item_list.addItem(item)