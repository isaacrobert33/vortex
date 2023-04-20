from PySide2.QtWidgets import *
from PySide2.QtCore import *
import subprocess, os, sys

HOME_DIR = os.path.expanduser("~")


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
