import math
import random
import os
from PyQt5.QtCore import Qt

from BasePet import BasePet

class Pet(BasePet):
    def __init__(self, evolution_line:str, manager, level:int=5):
        super().__init__(evolution_line=evolution_line, manager=manager, level=level)

        # Pet state
        self.pos_x, self.pos_y = manager.main_window.x() + random.randint(-500, 500), manager.main_window.y() + random.randint(-200, 200)

        # Flags / Utility
        self.drag_offset = None
        self.last_mouse_pos = None

    # ========== Movement ==========

    def _move_pet(self):
        """
        Main movement loop.
        """

        if self.drag_offset:
            return
        
        if "flying" in self.stage_data["behaviour"]:
            if self.floor - self.pos_y >= 100:
                self.is_flying = True
                self.is_walking = False

            self._fly_pet()
        
        if "walking" in self.stage_data["behaviour"]:
            if not self._fall_pet():
                self._walk_pet()

        if "teleporting" in self.stage_data["behaviour"]:
            self._teleport_pet()

        if self.stage_data.get("evolution_level") and self.level >= self.stage_data["evolution_level"]:
            self._evolve_pet()

        self._cant_escape_bounds()
        self.move(self.pos_x, self.pos_y)

    def _cant_escape_bounds(self):
        """
        Prevents the pet from escaping the screen bounds.
        """
        # Floor is determined by the bottom bound of which screen the pet is in.
        bounds = [screen.geometry() for screen in self.screens]
        aux_top = bounds[0].top() + 50
        for bound in bounds:
            if self.pos_x >= bound.left() and self.pos_x <= bound.right():
                self.floor = bound.bottom()
                # Top limit is determined to prevent out of vision pet-window interaction.
                aux_top = bound.top() + 50
                break

        # Floor can be determined by the top of open windows.
        for window in self.windows:
            if self.pos_x + self.width()/2 >= window[0] and self.pos_x + self.width()/2 <= window[2]:
                if self.pos_y <= window[1] and self.floor > window[1] and aux_top < window[1]:
                    self.floor = window[1] - self.height() + 20
                    break

        # If the difference between pos_y and the floor is greater than 30 pixels, it is considered a fall.
        if abs(self.pos_y - self.floor) > 30:
            self.is_walking = False
        
        # If beyond any of the limits, the pet is obstructed to go any further.
        self.pos_x = max(self.left, min(self.pos_x, self.right))
        self.pos_y = max(self.top, min(self.pos_y, self.floor))

    # ========== Mouse events ==========

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.pos()  # Click position within the pet.
            self.is_walking = False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_offset:
            global_pos = self.mapToGlobal(event.pos())
            new_x = global_pos.x() - self.drag_offset.x()
            new_y = global_pos.y() - self.drag_offset.y()

            # Calculates the velocity using the difference between positions.
            if self.last_mouse_pos:
                dx = global_pos.x() - self.last_mouse_pos.x()
                dy = global_pos.y() - self.last_mouse_pos.y()

                self.vx = math.floor(dx)
                self.vy = math.floor(dy)

            self.last_mouse_pos = global_pos

            # Updates the pet position to the mouse position.
            self.pos_x = new_x
            self.pos_y = new_y
            self.move(self.pos_x, self.pos_y)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.last_mouse_pos = None