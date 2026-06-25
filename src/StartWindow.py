import os
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

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Pet related variables
        self.manager = PetManager(main_window = self)
        self.pet_names = [name for name in self.manager.pet_data if self.manager.pet_data[name].get("unlocked")]

        # Window configurations
        self.setWindowTitle("Deskmon Pet")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.setStyleSheet(self._info_style())
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # UI construction        
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
            img = Image.open(img_path)
            x1, y1, x2, y2 = img.getbbox()

            pixmap = QPixmap(img_path)
            pixmap = pixmap.copy(x1, y1, x2-x1, y2-y1)

            button = QPushButton()
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(64, 64))
            button.clicked.connect(partial(self.create_pet, name))

            layout.addWidget(button)

    def _info_style(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "../stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def create_pet(self, name):
        pet = Pet(evolution_line=name, manager=self.manager)
        pet.show()
        self.manager.add_pet(pet)

    def closeEvent(self, event):
        self.manager.save_data_into_json(path=os.path.join(self.base_dir, "./data/data.json"))
        QApplication.quit()
        event.accept()