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
SHELL_HISTORY_FILENAME, SHELL = ".bash_history", "bash"

if os.environ["SHELL"].endswith("zsh"):
    SHELL_HISTORY_FILENAME, SHELL = ".zsh_history", "zsh"
elif os.environ["SHELL"].endswith("ksh"):
    SHELL_HISTORY_FILENAME, SHELL = ".sh_history", "sh"

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


TIC, TOC = None, None


class ShellRunner(QThread):
    alive = True
    cmd_stdout = Signal(str)
    cmd_exec = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reader = None

    def run(self) -> None:
        global current_cmd, executed, TIC
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
                TIC = time.time()
                self.shell.stdin.write(
                    f"{current_cmd} && echo 'done_executing_vortex'\n".encode()
                )
                self.shell.stdin.flush()
                executed = True


class ShellReader(QThread):
    cmd_stdout = Signal(str)
    exec_done = Signal(bool)

    def __init__(self, shell) -> None:
        super().__init__()

        self.exit = False
        self.shell = shell

    def run(self) -> None:
        while not self.exit:
            output = self.shell.stdout.readline().decode().strip()

            if "done_executing_vortex" not in output:
                self.cmd_stdout.emit(output)

            if executed and "done_executing_vortex" in output:
                self.finished_exec()
                TOC = time.time()

    def finished_exec(self):
        print("Done executing")
        global current_cmd, executed
        self.exec_done.emit(True)
        current_cmd = None
        executed = False


with open(os.path.join(HOME_DIR, SHELL_HISTORY_FILENAME), "r") as f:
    shell_history = f.read().split("\n")

    for i, c in enumerate(shell_history):
        if ";" in c:
            shell_history[i] = c.split(";")[1]


class StdIn(QTextEdit):
    returnPressed = Signal(str)

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.currentIndex = None

        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Up:
            self.navigate_up()
        elif event.key() == Qt.Key_Down:
            self.navigate_down()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.returnPressed.emit(self.toPlainText())
        else:
            super().keyPressEvent(event)

    def navigate_up(self):
        t = self.toPlainText().strip()
        if not self.currentIndex:
            shell_history.append(t)
            self.setText(shell_history[-2].strip())
            self.currentIndex = len(shell_history) - 2
        else:
            if not self.currentIndex == 0:
                self.currentIndex -= 1
                self.setText(shell_history[self.currentIndex])

        self.textCursor().movePosition(self.textCursor().End)

    def navigate_down(self):
        t = self.toPlainText().strip()

        if t and self.currentIndex is not None:
            if not self.currentIndex == len(shell_history):
                self.currentIndex += 1
                self.setText(shell_history[self.currentIndex])

        self.textCursor().movePosition(self.textCursor().End)


class UiTab(QWidget):
    def __init__(
        self, parent, mainwindow: typing.Optional[QMainWindow] = ..., tab_index=None
    ) -> None:
        super().__init__(parent)
        self.parent = parent
        self.tab_index = tab_index

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
            'border: 1px solid gray; background-color: transparent;font: 13pt "Courier New";'
        )
        self.stdout.setReadOnly(True)
        self.stdout.setWindowOpacity(0.5)
        self.stdout.setAlignment(Qt.AlignBottom)

        # Create a directory label
        self.current_dir_label = QLabel(self)
        self.current_dir_label.setObjectName("label")
        self.current_dir_label.setGeometry(QRect(0, 555, 960, 16))
        self.current_dir_label.setStyleSheet(
            "color: rgb(255, 72, 135); font-size:14px; font-weight:600; "
        )
        self.current_dir_label.setText(self.currentDir)

        # Create an stdin field
        self.stdin = StdIn(self)
        self.stdin.setObjectName("stdin")
        self.stdin.setGeometry(QRect(0, 575, 955, 38))
        self.stdin.setStyleSheet(
            """border: none;
            font: 75 bold 13pt "Courier New";"""
        )
        self.stdin.setWindowOpacity(0.5)
        # Connect the returnPressed signal of the input widget to the executeCommand slot
        self.stdin.returnPressed.connect(self.executeCommand)

        self.shell_proc = ShellRunner()
        self.shell_proc.started.connect(self.thread_setup)
        self.shell_proc.start()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            print("Ctrl+C was pressed")

        return super().keyPressEvent(event)

    def thread_setup(self, dt=None):
        self.shell_proc.reader.cmd_stdout.connect(self.updateOutput)
        self.shell_proc.reader.exec_done.connect(self.executed)

    def executeCommand(self, ls=None):
        global current_cmd
        # Get the command to be executed from the input widget
        self.command = self.stdin.toPlainText().strip()
        shell_history.append(self.command)

        with open(os.path.join(HOME_DIR, SHELL_HISTORY_FILENAME), "a") as f:
            f.write(f"\n{self.command}")
        f.close()

        stdout = f"{self.stdout.toHtml().replace('</html>', '')}<hr>{self.currentDir}<br><b>{self.command}</b><br></html>"
        self.stdout.setText(stdout)

        if "exit" in self.command:
            self.parent.closeTab(self.tab_index)

        current_cmd = self.command
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
            self.current_dir_label.setText(self.currentDir)
        elif "clear" in self.command:
            self.stdout.setText("")

        # Clear the input widget
        self.stdin.clear()
        self.stdin.setDisabled(False)
        self.stdin.setFocus()
        self.stdout.setText(
            f"{self.stdout.toHtml().replace('</html>', '')}<hr>{self.currentDir}<br><b>{self.command}</b><br></html>"
        )

    def adjust_height(self):
        content_height = self.runtime_stdout.document().size().height()
        desired_height = self.runtime_stdout.sizeHint().height()
        self.current_dir_label.move(QPoint(0, self.current_dir_label.y() - 15))
        self.stdin.move(QPoint(0, self.stdin.y() - 15))
        self.runtime_stdout.move(QPoint(0, self.runtime_stdout.y() - 15))

        if content_height != desired_height:
            self.runtime_stdout.setMinimumHeight(content_height)
