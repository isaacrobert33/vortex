from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import os


class StdIn(QTextEdit):
    returnPressed = Signal(str)
    navigateUp = Signal(bool)
    navigateDown = Signal(bool)

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.currentIndex = None

        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Up:
            self.navigateUp.emit(True)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.returnPressed.emit(self.toPlainText())
        elif event.key() == Qt.Key_Tab:
            t = self.toPlainText().split(" ")[-1]
            match = []
            dir = os.listdir()

            for file in dir:
                if t in file:
                    match.append(file)

            self.parent.dir_list.load_items(match)
            self.parent.dir_list.setVisible(True)
        else:
            super().keyPressEvent(event)

    def navigate_up(self):
        t = self.toPlainText().strip()
        if not self.currentIndex:
            self.parent.shell_history.append(t)
            self.setText(self.parent.shell_history[-2].strip())
            self.currentIndex = len(self.parent.shell_history) - 2
        else:
            if not self.currentIndex == 0:
                self.currentIndex -= 1
                self.setText(self.parent.shell_history[self.currentIndex])

        self.textCursor().movePosition(self.textCursor().Start)

    def navigate_down(self):
        t = self.toPlainText().strip()

        if t and self.currentIndex is not None:
            if not self.currentIndex == len(self.parent.shell_history):
                self.currentIndex += 1
                self.setText(self.parent.shell_history[self.currentIndex])

        self.textCursor().movePosition(self.textCursor().Start)
