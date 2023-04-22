from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from utils.config import load_settings, set_settings, VORTEX_ASSETS, setup_vortex
import os, shutil

setup_vortex()
settings = load_settings()


class Settings(QWidget):
    colorChoice = Signal(tuple)
    newBackgroundPath = Signal(str)

    def __init__(self, parent: QWidget = None, mainwindow=None) -> None:
        super().__init__(parent)

        self.mainwindow = mainwindow

        self.color_btn = QPushButton("Choose a Theme color")
        self.color_btn.clicked.connect(self.open_color_dialog)

        self.bg_image_btn = QPushButton("Select Wallpaper")
        self.bg_image_btn.clicked.connect(self.open_file_dialog)

        self.colorChoice.connect(self.set_color_theme)
        self.newBackgroundPath.connect(self.set_bg_image)

        layout = QVBoxLayout()
        layout.addWidget(self.color_btn)
        layout.addWidget(self.bg_image_btn)
        self.setLayout(layout)

    def open_color_dialog(self):
        # Open a color dialog and get the selected color
        color = QColorDialog.getColor(initial=QColor(*settings["theme_color"]))

        # If a color was selected, get its RGB values
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            self.colorChoice.emit((r, g, b))

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "Select wallpaper", ".", "All Files (*)"
        )
        if filename:
            self.newBackgroundPath.emit(filename)
        else:
            pass

    def set_color_theme(self, rgb_color):
        background_pixmap = QPixmap(settings["bg_image"])
        overlay_color = QColor(*rgb_color, 230)
        overlay_pixmap = QPixmap(
            QSize(self.mainwindow.width(), self.mainwindow.height() * 2)
        )
        overlay_pixmap.fill(overlay_color)

        # Set the composition mode to source-over
        painter = QPainter(background_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, overlay_pixmap)
        painter.end()

        palette = QPalette()
        palette.setBrush(
            QPalette.Background,
            background_pixmap.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            ),
        )
        self.mainwindow.setPalette(palette)
        set_settings(theme_color=rgb_color)

    def set_bg_image(self, filename):
        bg_path = filename
        if os.path.exists(bg_path):
            shutil.copy(bg_path, f"{VORTEX_ASSETS}/{os.path.basename(bg_path)}")
            background_pixmap = QPixmap(bg_path)
            overlay_color = QColor(*settings["theme_color"], 230)
            overlay_pixmap = QPixmap(
                QSize(self.mainwindow.width(), self.mainwindow.height() * 2)
            )
            overlay_pixmap.fill(overlay_color)

            # Set the composition mode to source-over
            painter = QPainter(background_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(0, 0, overlay_pixmap)
            painter.end()

            palette = QPalette()
            palette.setBrush(
                QPalette.Background,
                background_pixmap.scaled(
                    self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                ),
            )
            self.mainwindow.setPalette(palette)
            set_settings(bg_image=f"{VORTEX_ASSETS}/{os.path.basename(bg_path)}")
        else:
            print("BG Path doesn't exists")
