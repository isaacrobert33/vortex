# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from threading import Thread
import os
import sys
import time
import typing
import subprocess
import select

HOME_DIR = os.path.expanduser("~")
current_cmd = None
executed = False


class CommandRunner(QThread):
    cmd_stdout = Signal(str)
    exec_done = Signal(bool)

    def __init__(self, command):
        super(CommandRunner, self).__init__()
        self.command = command
        self.chdir = None

    def run(self):
        # Execute the command using subprocess.Popen
        if "cd " in self.command:
            self.command = (
                self.command
                + f' && pwd > ~/vortex/.chdir && export OLDPWD="{os.getcwd()}"'
            )
            self.chdir = True

        process = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # Read the output stream of the process
        while True:
            output = process.stdout.readline().decode(sys.stdout.encoding).strip()

            if self.chdir:
                with open(f"{HOME_DIR}/vortex/.chdir", "r") as f:
                    dir = f.read().strip()
                    os.chdir(dir)
                f.close()

            if output == "" and process.poll() is not None:
                self.exec_done.emit(True)
                break

            self.cmd_stdout.emit(output)

        # Wait for the process to finish
        process.wait()


class ShellRunner(QThread):
    alive = True
    cmd_stdout = Signal(str)
    cmd_exec = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reader = None

    def run(self) -> None:
        global current_cmd, executed
        self.shell = subprocess.Popen(
            ["bash"],
            stderr=subprocess.PIPE,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        self.reader = ShellReader(self.shell)
        self.reader.start()

        while self.alive:
            if current_cmd and not executed:
                self.shell.stdin.write(f"{current_cmd}\n".encode())
                self.shell.stdin.flush()
                executed = True


def exec_timer():
    time.sleep(5)


class ShellReader(QThread):
    cmd_stdout = Signal(str)
    exec_done = Signal(bool)

    def __init__(self, shell) -> None:
        super().__init__()

        self.exit = False
        self.shell = shell

    def run(self) -> None:
        while not self.exit:
            if select.select([self.shell.stdout], [], [], 0)[0]:
                output = self.shell.stdout.readline().decode().strip()
                print(output, self.shell.poll())
                # if output == "" and self.shell.poll() is not None:
                #     break

                self.cmd_stdout.emit(output)
            else:
                if executed:
                    self.finished_exec()

    def finished_exec(self):
        print("Done executing")
        global current_cmd, executed
        self.exec_done.emit(True)
        current_cmd = None
        executed = False


class UiTab(QWidget):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = ...,
        mainwindow: typing.Optional[QMainWindow] = ...,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("tab")
        self.mainwindow = mainwindow
        self.command = None

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

        self.shell_proc = ShellRunner()
        self.shell_proc.started.connect(self.thread_setup)
        self.shell_proc.start()

    def thread_setup(self, dt=None):
        self.shell_proc.reader.cmd_stdout.connect(self.updateOutput)
        self.shell_proc.reader.exec_done.connect(self.executed)

    def executeCommand(self):
        global current_cmd
        # Get the command to be executed from the input widget
        self.command = self.stdin.text().strip()

        # Create a CommandRunner instance and connect its command_output signal to updateOutput
        # self.runner = CommandRunner(self.command)
        stdout = f"{self.stdout.toHtml().replace('</html>', '')}<hr>{self.currentDir}<br><b>{self.command}</b><br></html>"
        self.stdout.setText(stdout)

        # self.runner.cmd_stdout.connect(self.updateOutput)
        # self.runner.exec_done.connect(self.executed)
        if "exit" in self.command:
            self.mainwindow.close()

        current_cmd = self.command

        # Start the CommandRunner thread
        # self.runner.start()
        self.stdin.setDisabled(True)

    def updateOutput(self, output):
        # Append the output to the text edit widget
        cursor = self.stdout.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(output + "\n")
        self.stdout.setTextCursor(cursor)

    def executed(self, state):
        if "cd " in self.command and state:
            self.currentDir = os.getcwd().replace(HOME_DIR, "~")
            print(self.currentDir)
            self.current_dir_label.setText(self.currentDir)
        elif "clear" in self.command:
            self.stdout.setText("")

        # Clear the input widget
        self.stdin.clear()
        self.stdin.setDisabled(False)
        self.stdin.setFocus()
