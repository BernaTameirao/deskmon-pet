import os

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

class InfoWindow(QDialog):
    def __init__(self, pet):
        super().__init__()

        self.pet = pet
        self.setWindowTitle(f"{pet.name.capitalize()} — Info")
        self.setFixedWidth(350)
        self.setStyleSheet(self._info_style())

        self._build_ui()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(100)
    
    def _build_ui(self):
        layout = QVBoxLayout()

        self.name_label = QLabel()
        self.level_label = QLabel()
        self.evo_label = QLabel()

        layout.addWidget(self.name_label)
        layout.addWidget(self.level_label)
        layout.addWidget(self.evo_label)

        self.setLayout(layout)

        self.update_info()

    def _info_style(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, "./stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def update_info(self):
        self.name_label.setText(f"Name: {self.pet.name.capitalize()}")
        self.level_label.setText(f"Level: {self.pet.level}")
        self.evo_label.setText(f"Evolution Stage: {self.pet.evolution_stage}")