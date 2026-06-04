import os
from functools import partial
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QApplication, QWidget
from PyQt5.QtCore import Qt

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
        self.setStyleSheet(self._info_style())
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # UI construction        
        self._build_ui()
    
    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        for name in self.pet_names:
            button = QPushButton(name.capitalize())
            button.clicked.connect(partial(self.create_pet, name))

            layout.addWidget(button)
        
        self.adjustSize()
        self.setMaximumHeight(self.sizeHint().height())

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