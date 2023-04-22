from PySide2.QtCore import *
from PySide2.QtWidgets import *
from utils.config import setup_vortex, load_settings

setup_vortex()
settings = load_settings()


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
            f"background-color: rgb({settings['theme_color'][0]+30}, {settings['theme_color'][1]+30}, {settings['theme_color'][2]+30}); border-top-left-radius: 5px; border-top-right-radius: 5px;"
        )
        self.setWindowOpacity(0.5)
        self.item_list.itemSelectionChanged.connect(self.on_item_selection)

    def handle_item_clicked(self, item):
        self.cmd_clicked.emit(item.text())
        self.setVisible(False)

    def on_item_selection(self):
        current_item = self.item_list.currentItem()
        if current_item:
            self.cmd_clicked.emit(current_item.text())

    def add_cmd(self, cmd):
        item = QListWidgetItem(text=cmd)
        self.item_list.addItem(item)

    def load_items(self):
        for command in self.parent().shell_history:
            item = QListWidgetItem(command)
            self.item_list.addItem(item)

    def setVisible(self, visible: bool) -> None:
        if visible:
            self.load_items()
            self.parent().cmd_list_index = self.item_list.count()
        else:
            self.item_list.clear()
            self.parent().cmd_list_index = 0
        return super().setVisible(visible)
