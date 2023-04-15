# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os
import sys
import typing
import subprocess


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
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)

        self.setObjectName("tab")

        self.dirChanged = False
        self.currentDir = os.getcwd()

        # Create a text edit widget to display the output of the terminal
        self.stdout = QTextEdit(self)
        self.stdout.setObjectName("stdin")
        self.stdout.setGeometry(QRect(0, 560, 801, 41))
        self.stdout.setStyleSheet(
            "QLineEdit::cursor {\n"
            "        width:  3px;\n"
            "        background-color:  rgb(255, 72, 135);\n"
            "    }"
        )
        self.stdout.setReadOnly(True)

        # Create a directory label
        self.current_dir_label = QLabel(self)
        self.current_dir_label.setObjectName("label")
        self.current_dir_label.setGeometry(QRect(0, 540, 231, 16))
        self.current_dir_label.setStyleSheet(
            "color: rgb(255, 72, 135); font-size:14px; font-weight:600; "
        )
        self.current_dir_label.setText(self.currentDir)

        self.stdin = QLineEdit(self)
        self.stdin.setObjectName("commandIn")
        self.stdin.setGeometry(QRect(10, 440, 801, 91))
        self.stdin.setStyleSheet("")

        # Connect the returnPressed signal of the input widget to the executeCommand slot
        self.stdin.returnPressed.connect(self.executeCommand)

    def executeCommand(self):
        # Get the command to be executed from the input widget
        self.command = self.stdin.text().strip()

        # Clear the input widget
        self.stdin.clear()

        # Create a CommandRunner instance and connect its command_output signal to updateOutput
        self.runner = CommandRunner(self.command)
        self.stdout.setText(f"{self.stdout.text}\n{self.currentDir}")

        self.runner.cmd_stdout.connect(self.updateOutput)
        self.runner.exec_done.connect(self.executed)

        # Start the CommandRunner thread
        self.runner.start()

    def updateOutput(self, output):
        # Append the output to the text edit widget
        cursor = self.stdout.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(output + "\n")
        self.stdout.setTextCursor(cursor)

    def executed(self, state):
        if "cd" in self.command and state:
            self.currentDir = os.getcwd()
            self.current_dir_label = self.currentDir
