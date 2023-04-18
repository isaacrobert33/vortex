# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os
import sys
import typing
import subprocess

HOME_DIR = os.path.expanduser("~")


class CommandRunner(QThread):
    cmd_stdout = Signal(str)
    exec_done = Signal(bool)

    def __init__(self, command):
        super(CommandRunner, self).__init__()
        self.command = command

    def run(self):
        # Execute the command using subprocess.Popen
        process = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # Read the output stream of the process
        while True:
            output = process.stdout.readline().decode(sys.stdout.encoding).strip()

            if output == "" and process.poll() is not None:
                self.exec_done.emit(True)
                break

            self.cmd_stdout.emit(output)

        # Wait for the process to finish
        process.wait()


class UiTab(QWidget):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = ...,
        mainwindow: typing.Optional[QMainWindow] = ...,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("tab")
        self.mainwindow = mainwindow

        self.currentDir = os.getcwd().replace(HOME_DIR, "~")
        self.setStyleSheet("background-color: transparent;")

        # Create a text edit widget to display the output of the terminal
        self.stdout = QTextEdit(self)
        self.stdout.setObjectName("stdout")
        self.stdout.setGeometry(QRect(-5, 0, 960, 540))
        self.stdout.setStyleSheet(
            "border: 1px solid gray; background-color: transparent;"
        )
        self.stdout.setReadOnly(True)
        self.stdout.setWindowOpacity(0.5)

        # Create a directory label
        self.current_dir_label = QLabel(self)
        self.current_dir_label.setObjectName("label")
        self.current_dir_label.setGeometry(QRect(0, 555, 960, 16))
        self.current_dir_label.setStyleSheet(
            "color: rgb(255, 72, 135); font-size:14px; font-weight:600; "
        )
        self.current_dir_label.setText(self.currentDir)

        # Create an stdin field
        self.stdin = QLineEdit(self)
        self.stdin.setObjectName("stdin")
        self.stdin.setGeometry(QRect(0, 575, 955, 38))
        self.stdin.setStyleSheet(
            """border: none;
            QLineEdit::focus {border: none; }"""
        )
        self.stdin.setWindowOpacity(0.5)
        # Connect the returnPressed signal of the input widget to the executeCommand slot
        self.stdin.returnPressed.connect(self.executeCommand)

    def executeCommand(self):
        # Get the command to be executed from the input widget
        self.command = self.stdin.text().strip()

        # Create a CommandRunner instance and connect its command_output signal to updateOutput
        self.runner = CommandRunner(self.command)
        stdout = f"{self.stdout.toHtml().replace('</html>', '')}<hr>{self.currentDir}<br><b>{self.command}</b><br></html>"
        self.stdout.setText(stdout)

        self.runner.cmd_stdout.connect(self.updateOutput)
        self.runner.exec_done.connect(self.executed)

        # Start the CommandRunner thread
        self.runner.start()
        self.stdin.setDisabled(True)

    def updateOutput(self, output):
        # Append the output to the text edit widget
        cursor = self.stdout.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(output + "\n")
        self.stdout.setTextCursor(cursor)

    def executed(self, state):
        if "cd" in self.command and state:
            self.currentDir = os.getcwd().replace(HOME_DIR, "~")
            self.current_dir_label = self.currentDir
        if "exit" in self.command:
            self.mainwindow.close()

        # Clear the input widget
        self.stdin.clear()
        self.stdin.setDisabled(False)
        self.stdin.setFocus()
