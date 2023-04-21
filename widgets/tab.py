# -*- coding: utf-8 -*-

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from .stdin import StdIn
from .command_list import CommandList
from .directory_list import DirectoryList
import os
import time
import typing
import subprocess

HOME_DIR = os.path.expanduser("~")
SHELL_HISTORY_FILENAME, SHELL = ".bash_history", "bash"

if os.environ["SHELL"].endswith("zsh"):
    SHELL_HISTORY_FILENAME, SHELL = ".zsh_history", "zsh"
elif os.environ["SHELL"].endswith("ksh"):
    SHELL_HISTORY_FILENAME, SHELL = ".sh_history", "sh"

current_cmd = None
executing = False

TIC, TOC = None, None


with open(os.path.join(HOME_DIR, SHELL_HISTORY_FILENAME), "r") as f:
    shell_history = list(set(f.read().split("\n")))

    for i, c in enumerate(shell_history):
        shell_history[i] = c.strip()
        if ";" in c:
            shell_history[i] = c.split(";")[1]

CHDIR = None


class ShellRunner(QThread):
    alive = True
    cmd_stdout = Signal(str)
    cmd_exec = Signal(bool)
    readerInitiated = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reader = None

    def run(self) -> None:
        global current_cmd, executing, TIC
        self.shell = subprocess.Popen(
            [SHELL],
            stderr=subprocess.PIPE,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        self.reader = ShellReader(self.shell, self)
        self.reader.start()
        self.readerInitiated.emit(True)

        while self.alive:
            if current_cmd is not None and not executing:
                print("executing", current_cmd)
                if current_cmd and "cd " in current_cmd:
                    current_cmd = (
                        current_cmd
                        + f' && pwd > ~/vortex/.chdir && export OLDPWD="{os.getcwd()}"'
                    )

                TIC = time.time()
                self.shell.stdin.write(
                    f"{current_cmd} && echo 'done_executing_vortex'\n".encode()
                )
                self.shell.stdin.flush()
                executing = True
                print("Done initiating execution", current_cmd)


class ShellReader(QThread):
    cmd_stdout = Signal(str)
    exec_done = Signal(bool)
    directoryChanged = Signal(str)

    def __init__(self, shell, parent_thread) -> None:
        super().__init__()
        self.parent_thread = parent_thread
        self.exit = False
        self.shell = shell

    def run(self) -> None:
        global TOC
        while not self.exit:
            if current_cmd and executing:
                print("Reading...", current_cmd, executing)
                output = self.shell.stdout.readline().decode().strip()
                print("io", output)
                if "done_executing_vortex" not in output:
                    self.cmd_stdout.emit(output)

                if executing and "done_executing_vortex" in output:
                    self.finished_exec()
                    TOC = time.time()

    def finished_exec(self):
        global current_cmd, executing

        if "cd " in current_cmd:
            with open(f"{HOME_DIR}/vortex/.chdir", "r") as f:
                dir = f.read().strip()
                self.directoryChanged.emit(dir)
            f.close()

        self.exec_done.emit(True)
        current_cmd = None
        executing = False
        print("finishing", current_cmd)


class UiTab(QWidget):
    def __init__(
        self, parent, mainwindow: typing.Optional[QMainWindow] = ..., tab_index=None
    ) -> None:
        super().__init__(parent)
        self.parent = parent
        self.tab_index = tab_index

        self.mainwindow = mainwindow
        self.command = None
        self.shell_history = shell_history

        self.currentDir = os.getcwd().replace(HOME_DIR, "~")
        self.setStyleSheet("background-color: transparent;")

        # Create a text edit widget to display the output of the terminal
        self.stdout = QTextEdit(self)
        self.stdout.setObjectName(f"stdout-{tab_index}")
        self.stdout.setStyleSheet(
            'border: 1px solid gray; background-color: transparent;font: 13pt "Courier New";'
        )
        self.stdout.setReadOnly(True)
        self.stdout.setWindowOpacity(0.5)
        self.stdout.setAlignment(Qt.AlignBottom)

        # Create a directory label
        self.current_dir_label = QLabel(self)
        self.current_dir_label.setObjectName(f"dir-{tab_index}")
        self.current_dir_label.setStyleSheet(
            "color: rgb(255, 72, 135); font-size:14px; font-weight:600; "
        )
        self.current_dir_label.setText(self.currentDir)

        self.suggestor = QTextEdit(self)
        self.suggestor.setReadOnly(True)
        self.suggestor.setObjectName(f"sgt-{tab_index}")
        self.suggestor.setStyleSheet(
            """border: none;
            font: 75 bold 13pt "Courier New";
            color: rgb(120, 120, 120);"""
        )
        self.suggestor.setWindowOpacity(0.5)

        # Create an stdin field
        self.stdin = StdIn(self)
        self.stdin.setObjectName(f"stdin-{tab_index}")
        self.stdin.setStyleSheet(
            """border: none;
            font: 75 bold 13pt "Courier New";"""
        )
        self.stdin.setWindowOpacity(0.5)
        # Connect the returnPressed signal of the input widget to the executeCommand slot
        self.stdin.returnPressed.connect(self.executeCommand)
        self.stdin.navigateUp.connect(self.navigate_cmd_list)
        self.stdin.navigateDown.connect(self.navigate_cmd_list)
        self.stdin.navigateDir.connect(self.navigate_dir_list)

        self.cmd_list = CommandList(self)
        self.cmd_list.setObjectName(f"cmd_list-{tab_index}")
        self.cmd_list.cmd_clicked.connect(self.update_stdin)
        self.cmd_list.load_items()
        self.cmd_list.setVisible(False)

        self.dir_list = DirectoryList(self)
        self.dir_list.setObjectName(f"dir_list-{tab_index}")
        self.dir_list.dir_clicked.connect(self.auto_complete)
        self.dir_list.setVisible(False)

        self.shell_proc = ShellRunner()
        self.shell_proc.readerInitiated.connect(self.thread_setup)
        self.shell_proc.start()

        self.mainwindow.ctrl_c_clicked.connect(self.cancel_execution)

        self.cmd_list_index = self.cmd_list.item_list.count()
        self.dir_list_index = 0

        self.mainwindow.windowResized.connect(self.setAllWidgetSize)
        self.setAllWidgetSize()

    def setAllWidgetSize(self, size=None):
        self.stdout.setGeometry(
            QRect(-5, 0, self.mainwindow.width(), self.mainwindow.height() - 100)
        )
        self.current_dir_label.setGeometry(
            QRect(0, self.mainwindow.height() - 85, self.mainwindow.width(), 16)
        )
        self.suggestor.setGeometry(
            QRect(0, self.mainwindow.height() - 55, self.mainwindow.width() - 5, 38)
        )
        self.stdin.setGeometry(
            QRect(0, self.mainwindow.height() - 55, self.mainwindow.width() - 5, 38)
        )
        self.cmd_list.setGeometry(
            QRect(0, self.mainwindow.width() - 290, self.mainwindow.width(), 200)
        )
        self.dir_list.setGeometry(
            QRect(0, self.mainwindow.width() - 290, self.mainwindow.width(), 200)
        )

    def thread_setup(self, dt=None):
        self.shell_proc.reader.cmd_stdout.connect(self.updateOutput)
        self.shell_proc.reader.exec_done.connect(self.executed)
        self.shell_proc.reader.directoryChanged.connect(self.dir_changed)

    def navigate_dir_list(self, direction="down"):
        if not self.dir_list.isVisible():
            t = self.stdin.toPlainText().split(" ")[-1]

            match = []
            if "/" in t:
                dir_ls = os.listdir("/".join(t.replace("~", HOME_DIR).split("/")[:-1]))
            else:
                dir_ls = os.listdir()

            if t.split("/")[-1]:
                for file in dir_ls:
                    if "/" in t and t.split("/")[-1] in file:
                        match.append(file)
                    elif not "/" in t and t in file:
                        match.append(file)
            else:
                match = dir_ls

            if len(match) == 1:
                self.auto_complete(match[0])
            elif match:
                self.dir_list.load_items(match)
                self.dir_list.setVisible(True)
        else:
            if (
                self.dir_list_index >= 0
                and self.dir_list_index <= self.dir_list.item_list.count()
            ):
                print("b", self.dir_list_index)
                if self.dir_list_index == self.dir_list.item_list.count():
                    self.dir_list_index = -1
                if self.dir_list_index < 0:
                    self.dir_list_index = self.dir_list.item_list.count() - 2

                self.dir_list_index = (
                    self.dir_list_index + 1
                    if direction == "down"
                    else self.dir_list_index - 1
                )
                self.dir_list.item_list.setCurrentItem(
                    self.dir_list.item_list.item(self.dir_list_index)
                )

    def navigate_cmd_list(self, direction="up"):
        if self.dir_list.isVisible():
            self.navigate_dir_list(direction=direction)
            return

        if not self.cmd_list.isVisible():
            self.cmd_list.setVisible(True)
        if (
            self.cmd_list_index >= 0
            and not self.cmd_list_index > self.cmd_list.item_list.count()
        ):
            self.cmd_list_index = (
                self.cmd_list_index - 1
                if direction == "up"
                else self.cmd_list_index + 1
            )
            self.cmd_list.item_list.setCurrentItem(
                self.cmd_list.item_list.item(self.cmd_list_index)
            )

    def update_stdin(self, text):
        self.stdin.setText(text)
        self.stdin.move_cursor_to_end()

    def cancel_execution(self):
        self.shell_proc.shell.send_signal(subprocess.signal.SIGINT)
        self.shell_proc.reader.finished_exec()

    def auto_complete(self, text):
        text_remnants = " ".join(self.stdin.toPlainText().split(" ")[:-1])

        if "/" in self.stdin.toPlainText().split(" ")[-1]:
            text = f'{"/".join(self.stdin.toPlainText().split(" ")[-1].split("/")[:-1])}/{text}'

        self.stdin.setText(f"{text_remnants} {text}")
        self.stdin.move_cursor_to_end()

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
            return

        current_cmd = self.command
        self.stdin.setDisabled(True)
        self.dir_list.setVisible(False)
        self.cmd_list.setVisible(False)
        self.dir_list_index = 0
        self.cmd_list_index = self.cmd_list.item_list.count()

    def updateOutput(self, output):
        # Append the output to the text edit widget
        cursor = self.stdout.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(output + "\n")
        self.stdout.setTextCursor(cursor)

    def dir_changed(self, new_dir):
        print("new dir", new_dir)
        self.current_dir_label.setText(new_dir.replace(HOME_DIR, "~"))

    def executed(self, state):
        print("Done executing...", self.command)

        if "clear" in self.command:
            self.stdout.setText("")

        # Clear the input widget
        self.stdin.clear()
        self.stdin.setDisabled(False)
        self.stdin.setFocus()

    def adjust_height(self):
        content_height = self.runtime_stdout.document().size().height()
        desired_height = self.runtime_stdout.sizeHint().height()
        self.current_dir_label.move(QPoint(0, self.current_dir_label.y() - 15))
        self.stdin.move(QPoint(0, self.stdin.y() - 15))
        self.runtime_stdout.move(QPoint(0, self.runtime_stdout.y() - 15))

        if content_height != desired_height:
            self.runtime_stdout.setMinimumHeight(content_height)
