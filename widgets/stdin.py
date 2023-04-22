from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import os


class StdIn(QTextEdit):
    returnPressed = Signal(str)
    navigateUp = Signal(str)
    navigateDown = Signal(str)
    navigateDir = Signal(str)

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.currentIndex = None
        self.textChanged.connect(self.auto_suggestor)

    def auto_suggestor(self):
        if self.toPlainText():
            for each in self.parent.shell_history[::-1]:
                if each.startswith(self.toPlainText()):
                    self.parent.suggestor.setText(each)
                    break
                else:
                    self.parent.suggestor.setText("")
        else:
            self.parent.cmd_list.setVisible(False)
            self.parent.dir_list.setVisible(False)
            self.parent.suggestor.setText("")

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Up:
            self.navigateUp.emit("up")
        elif event.key() == Qt.Key_Down:
            self.navigateDown.emit("down")
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.returnPressed.emit(self.toPlainText())
            super().keyPressEvent(event)
        elif event.key() == Qt.Key_Right and self.parent.suggestor.toPlainText():
            self.setText(self.parent.suggestor.toPlainText())
            self.parent.suggestor.setText("")
            super().keyPressEvent(event)
            self.move_cursor_to_end()
        elif event.key() == Qt.Key_Tab:
            self.navigateDir.emit("down")
        else:
            super().keyPressEvent(event)

    def move_cursor_to_end(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
