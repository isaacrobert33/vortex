from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import subprocess
import time, os


HOME_DIR = os.path.expanduser("~")
SHELL_HISTORY_FILENAME, SHELL = ".bash_history", "bash"

if os.environ["SHELL"].endswith("zsh"):
    SHELL_HISTORY_FILENAME, SHELL = ".zsh_history", "zsh"
elif os.environ["SHELL"].endswith("ksh"):
    SHELL_HISTORY_FILENAME, SHELL = ".sh_history", "sh"

TIC, TOC = None, None


class ShellRunner(QThread):
    alive = True
    cmd_stdout = Signal(str)
    cmd_exec = Signal(bool)
    readerInitiated = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reader = None

    def run(self) -> None:
        global current_cmd, executed, TIC
        self.shell = subprocess.Popen(
            [SHELL],
            stderr=subprocess.PIPE,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        self.reader = ShellReader(self.shell)
        self.reader.start()
        self.readerInitiated.emit(True)

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
