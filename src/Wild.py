import math
import random
import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction

from BasePet import BasePet

class Wild(BasePet):
    def __init__(self, evolution_line:str, manager, level:int=5):
        super().__init__(evolution_line=evolution_line, manager=manager, level=level)

        # Pet state
        self.health = self.stage_data["health"]
        out_of_bounds, aux = (self.left, -1) if random.random() < 0.5 else (self.right, 1)
        self.pos_x = out_of_bounds + 500 * aux
        self.pos_y = random.randint(self.top, self.floor)

        # Timers
        self.despawn_timer = QTimer()

    # ========== Movement ==========

    def _move_pet(self):
        """
        Main movement loop.
        """
        
        for behaviour in self.stage_data["behaviour"]:
            handler = self.behaviour_handlers.get(behaviour)
            if handler:
                handler()

        if self.stage_data.get("evolution_level") and self.level >= self.stage_data["evolution_level"]:
            self._evolve_pet()

        self._cant_fall_floor()
        self._escape_bounds()
        self.move(self.pos_x, self.pos_y)

    def _cant_fall_floor(self):
        """
        Prevents the wild pet from falling through the floor.
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
        self.pos_y = min(self.pos_y, self.floor)

    def _escape_bounds(self):
        """
        If the wild pet get outside of bounds, it will despawn.
        """
        # If it is out of bounds, begin timer
        if self.pos_x > self.right or self.pos_x < self.left or self.pos_y < self.top:
            self._start_despawn_timer(time=15000)

        # If it comes back inside, stop timer
        else:
            self._stop_despawn_timer()

    def _take_damage(self):
        self.health -= 1
    
        if self.health >= 1:
            callback = self._load_image
        else:
            callback = self._be_captured

        self._color_image(r=255, g=255, b=255, alpha=255)
        damage_timer = QTimer.singleShot(32, callback)

    def _be_captured(self):
        """
        Captures the wild pet.
        """
        iteration_counter = 0
        # The sprite is changed to a pokeball.
        path = os.path.join(self.base_dir, "./imgs/poke-ball.png")
        self._load_image(path=path)

        def shake_image():
            nonlocal iteration_counter

            iteration_counter += 1
            shake_time = iteration_counter/5

            angle = math.sin(shake_time) * 15

            transform = QTransform()
            transform.rotate(angle)
            rotated = self.original_pixmap.transformed(transform, mode=1)
            self.setPixmap(rotated)

            # When the pet is captured.
            if iteration_counter >= 300:
                # Stops the timer to prevent crash.
                self.timer.stop()
                # Closes the pet.
                self.close_pet()

        # Starts a timer for the pet to be captured.
        self.reset_timer(callback=shake_image, interval=15)
        self.manager.pet_data[self.evolution_line]["unlocked"] = True
        self.manager.main_window.update()

    # ========== Mouse events ==========

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._take_damage()

    # ========== Utility Functions ==========

    def _start_despawn_timer(self, time:int=15000):
        if not self.despawn_timer.isActive():
            self.despawn_timer.start(time)
            self.despawn_timer.timeout.connect(self.close_pet)

    def _stop_despawn_timer(self):
        self.despawn_timer.stop()