# Desktop Pet
# Copyright (C) 2026 Bernardo Tameirão
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.

import os
import sys
from functools import partial
from PIL import Image

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap

class InventoryWindow(QDialog):
    def __init__(self, manager):
        super().__init__()

        self.base_dir = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.manager = manager

        data = self.manager.pet_data
        self.inventory = list({
            item
            for pet_data in data.values()
            for stage_data in pet_data["stages"].values()
            for stage in ([stage_data] if isinstance(stage_data, dict) else stage_data)
            for item in stage.get("evolution_item", [])
        })
        self.selected_item = None

        # Icon modifications
        img_path = os.path.join(self.base_dir, "./imgs/poke-ball.png")
        x1, y1, x2, y2 = Image.open(img_path).getbbox()
        pixmap = QPixmap(img_path).copy(x1, y1, x2-x1, y2-y1)

        self.setWindowTitle("Inventory")
        self.setWindowIcon(QIcon(pixmap))
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
        with open(os.path.join(self.base_dir, "./stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def _select_item(self, item):
        self.selected_item = item
        self.accept()
        