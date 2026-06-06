import os
from functools import partial
from PIL import Image
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QApplication, QWidget, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from Pet import Pet
from PetManager import PetManager

class StartWindow(QMainWindow):
    def __init__(self, pet_names:list[str]):
        super().__init__()

        # Pet related variables
        self.pet_names = pet_names
        self.pets = []
        self.manager = PetManager(main_window = self)

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

        label = QLabel()
        label.setFixedHeight(50)
        label.setText("Your Deskmon:")
        layout.addWidget(label)

        for name in self.pet_names:
            img = Image.open(f"imgs/{name}_0.png")
            x1, y1, x2, y2 = img.getbbox()

            pixmap = QPixmap(f"imgs/{name}_0.png")
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
        self.pets.append(Pet(name=name, manager=self.manager))
        self.pets[-1].show()
        self.manager.add_pet(self.pets[-1])

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()