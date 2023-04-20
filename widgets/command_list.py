from PySide2.QtCore import *
from PySide2.QtWidgets import *


class CommandList(QWidget):
    cmd_clicked = Signal(str)

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.item_list = QListWidget()
        self.layout.addWidget(self.item_list)
        self.setLayout(self.layout)
        self.item_list.itemClicked.connect(self.handle_item_clicked)
        self.setStyleSheet(
            "background-color: rgb(14, 46, 52); border-top-left-radius: 5px; border-top-right-radius: 5px;"
        )
        self.setWindowOpacity(0.5)
        # self.viewport().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def handle_item_clicked(self, item):
        self.cmd_clicked.emit(item.text())

    def load_items(self):
        for command in self.parent().shell_history:
            item = QListWidgetItem(command)
            self.item_list.addItem(item)
