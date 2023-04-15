import subprocess
import sys

from PySide2 import QtCore, QtWidgets


class CommandRunner(QtCore.QThread):
    command_output = QtCore.Signal(str)

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
                break
            self.command_output.emit(output)

        # Wait for the process to finish
        process.wait()


class Terminal(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Terminal, self).__init__(parent)

        # Create a layout to hold the widgets
        layout = QtWidgets.QVBoxLayout()
        self.setWindowOpacity(0.9)

        # Create a text edit widget to display the output of the terminal
        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Create a line edit widget to input the command to be executed
        self.input = QtWidgets.QLineEdit()
        layout.addWidget(self.input)

        # Connect the returnPressed signal of the input widget to the executeCommand slot
        self.input.returnPressed.connect(self.executeCommand)

        # Set the layout for the widget
        self.setLayout(layout)

    def executeCommand(self):
        # Get the command to be executed from the input widget
        command = self.input.text().strip()

        # Clear the input widget
        self.input.clear()

        # Create a CommandRunner instance and connect its command_output signal to updateOutput
        self.runner = CommandRunner(command)
        self.runner.command_output.connect(self.updateOutput)

        # Start the CommandRunner thread
        self.runner.start()

    def updateOutput(self, output):
        # Append the output to the text edit widget
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(output + "\n")
        self.output.setTextCursor(cursor)


if __name__ == "__main__":
    # Create a QApplication instance
    app = QtWidgets.QApplication(sys.argv)

    # Create a Terminal instance
    terminal = Terminal()

    # Show the Terminal widget
    terminal.show()

    # Run the event loop of the application
    sys.exit(app.exec_())
