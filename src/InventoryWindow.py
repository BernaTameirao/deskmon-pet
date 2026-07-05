import os
from functools import partial

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtCore import QTimer

class InventoryWindow(QDialog):
    def __init__(self, manager):
        super().__init__()

        self.manager = manager

        data = self.manager.pet_data
        self.inventory = list({
            item
            for pet_data in data.values()
            for stage_data in pet_data["stages"].values()
            for item in stage_data.get("evolution_item", [])
        })
        self.selected_item = None

        self.setWindowTitle("Inventory")
        self.setFixedWidth(350)
        self.setStyleSheet(self._info_style())

        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        content_layout = QVBoxLayout(content)

        for item in self.inventory:
            button = QPushButton(item)
            button.clicked.connect(partial(self._select_item, item))
            content_layout.addWidget(button)

    def _info_style(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, "./stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def _select_item(self, item):
        self.selected_item = item
        self.accept()
        