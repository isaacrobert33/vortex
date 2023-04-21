from PySide2.QtWidgets import (
    QApplication,
    QColorDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()

        # Create a button to open the color dialog
        self.color_btn = QPushButton("Pick a color")
        self.color_btn.clicked.connect(self.open_color_dialog)

        # Create a layout to hold the button
        layout = QVBoxLayout()
        layout.addWidget(self.color_btn)
        self.setLayout(layout)

    def open_color_dialog(self):
        # Open a color dialog and get the selected color
        color = QColorDialog.getColor()

        # If a color was selected, get its RGB values
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            return r, g, b
