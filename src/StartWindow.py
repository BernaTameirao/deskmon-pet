import os
import sys
from functools import partial
from PIL import Image

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QApplication, QWidget, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from Pet import Pet
from PetManager import PetManager

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.base_dir = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Pet related variables
        self.manager = PetManager(main_window = self)

        # Icon modifications
        img_path = os.path.join(self.base_dir, "./imgs/pikachu.png")
        x1, y1, x2, y2 = Image.open(img_path).getbbox()
        pixmap = QPixmap(img_path).copy(x1, y1, x2-x1, y2-y1)

        # Window configurations
        self.setWindowTitle("Deskmon Pet")
        self.setWindowIcon(QIcon(pixmap))
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.setStyleSheet(self._info_style())
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # UI construction        
        self.update()

    def update(self):
        self.pet_names = [name for name in self.manager.pet_data if self.manager.pet_data[name].get("unlocked")]
        self._build_ui()
    
    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        central_widget = QWidget()
        scroll.setWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        for name in self.pet_names:
            img_path = os.path.join(self.base_dir, f"./imgs/{self.manager.pet_data[name]["stages"]["0"]["image"]}")
            x1, y1, x2, y2 = Image.open(img_path).getbbox()
            pixmap = QPixmap(img_path).copy(x1, y1, x2-x1, y2-y1)

            button = QPushButton()
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(64, 64))
            button.clicked.connect(partial(self.create_pet, name))

            layout.addWidget(button)

    def _info_style(self):
        with open(os.path.join(self.base_dir, "./stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def create_pet(self, name):
        pet = Pet(evolution_line=name, manager=self.manager)
        pet.show()
        self.manager.add_pet(pet)

    def closeEvent(self, event):
        
        self.manager.save_data_into_json(path=os.path.join(self.manager.base_dir, "./data/data.json"))
        QApplication.quit()
        event.accept()