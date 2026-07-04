import random
import math
import os
import bisect
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap, QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QTimer

from InfoWindow import InfoWindow

class BasePet(QLabel):
    def __init__(self, evolution_line:str, manager, level:int = 5):
        super().__init__()
        # Directory related variables
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Manager related variables
        self.manager = manager
        self.windows = []

        # Gets the evolution levels to determine the evolution stage
        pet_data = manager.pet_data[evolution_line]
        evolution_levels = [pet_data["stages"][str(i)]["evolution_level"]
            for i in range(len(pet_data["stages"]))
            if "evolution_level" in pet_data["stages"][str(i)]
        ]

        # Pet state
        self.evolution_stage = bisect.bisect_right(evolution_levels, level)
        self.stage_data = pet_data["stages"][str(self.evolution_stage)]
        self.name = self.stage_data["name"]
        self.evolution_line = evolution_line
        self.image_path = os.path.join(self.base_dir, f"./imgs/{self.stage_data["image"]}")
        self.pos_x, self.pos_y = -500, -500
        self.direction, self.direction_y = random.choice([1, -1]), random.choice([1, -1]) 
        self.vx, self.vy = int(self.stage_data["base_speed"])*self.direction, 0
        self.level = level
        self.walk_cycle = 0
        self.info_window = InfoWindow(pet=self)

        # Flags / Utility
        self.is_walking = False
        self.is_flying = False
        self.is_teleporting = False
        self.in_battle = False

        # Initial configuration
        self._load_image()
        self._setup_window()
        self._setup_timers()
        self._setup_screens()
        self._setup_behaviours()
        self._create_context_menu()

    # ========== Setup ==========

    def _load_image(self, path=None):
        if path == None:
            path = self.image_path

        self.original_pixmap = QPixmap(path)
        pixmap = self.original_pixmap
        self.setPixmap(pixmap)

        # Flips image accordingly with direction.
        if self.direction == 1:
            self._flip_image()

    def _setup_window(self):
        self.setGeometry(self.pos_x, self.pos_y, 128, 128)
        # Unique window title for each pet
        self.setWindowTitle(f"Pet - {self.name.capitalize()}")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)

    def _setup_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._move_pet)
        self.timer.start(15)

    def _setup_screens(self):
        self.screens = QApplication.instance().screens()
        area = self.screens[0].virtualGeometry()
        self.left = area.left()
        self.top = area.top() - self.height() + 60
        self.right = area.right() - self.width()
        self.floor = area.bottom()

    def _setup_behaviours(self):
        self.behaviour_handlers = {
            "walking": self._walk_pet,
            "flying": self._fly_pet,
            "teleporting": self._teleport_pet,
        }

    def _create_context_menu(self):
        # Loads the qss file
        try:
            with open(os.path.join(self.base_dir, "./stylesheets/menu.qss"), "r") as f:
                menu_style = f.read()
        except FileNotFoundError:
            menu_style = ""
    
        # Creates the menu and stores it as an attribute
        self.context_menu = QMenu(self)
        self.context_menu.setStyleSheet(menu_style)
    
        # Creates actions
        self.info_action = QAction("[   ⓘ   Info   ]", self)
        self.close_action = QAction("[   ✖   Close  ]", self)
    
        # Connects actions
        self.info_action.triggered.connect(self.show_info)
        self.close_action.triggered.connect(self.close_pet)
    
        # Adds them to the menu
        self.context_menu.addAction(self.info_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.close_action)

    # ========== Movement ==========

    def _move_pet(self):
        pass

    def _fall_pet(self):
        """
        Simulates gravity.

        Returns:
            if the pet is falling (bool).
        """

        if self.is_walking or self.is_flying:
            return False

        # If the pet is above the floor level, it will begin to fall.
        if self.pos_y < self.floor:

            # Its vertical speed will increase with each iteration, until it reaches terminal velocity.
            self.vy = min(self.vy + 1, 50)
            self.pos_y += self.vy

            # Its horizontal speed remains the same, to simulate inertia.
            self.vx = min(self.vx, 50)
            self.pos_x += self.vx

            return True

        else:
            self.is_walking = True
            return False

    def _walk_pet(self):
        """
        Makes the pet walk.
        """

        if self._fall_pet() or not self.is_walking or self.in_battle:
            return

        self.walk_cycle += 1
        self.vx = int(self.stage_data["base_speed"]) * self.direction
        self.pos_x += self.vx

        # Smooth vertical motion (sinusoidal rocking)
        offset_y = 5 * math.sin(self.walk_cycle * 0.5)
        self.pos_y = math.floor(self.floor + offset_y)

        # Chance to change directions
        if random.random() < 0.005:
            self.direction *= -1
            self.vx *= -1
            self._flip_image()

        # Chance to pause (delay)
        elif random.random() < 0.002:
            delay_ms = random.randint(2000, 4000)  # between 2 and 4 seconds.
            self.reset_timer(callback=self._end_delay, interval=delay_ms)

        # Chance to jump
        elif random.random() < 0.001:
            self._jump_pet()

    def _fly_pet(self):
        """
        Makes the pet fly.
        """

        if self.floor - self.pos_y >= 100:
            self.is_flying = True
            self.is_walking = False

        if not self.is_flying:
            return
        
        self.walk_cycle += 1

        offset_y_1 = math.sin(self.walk_cycle * 0.1) * 2
        offset_y_2 = math.cos(self.walk_cycle * 0.05) * 1

        if self.direction_y == 1:
            self.pos_y = math.floor(self.pos_y + offset_y_1 + offset_y_2)
        else:
            self.pos_y = math.ceil(self.pos_y + offset_y_1 + offset_y_2)

        if self.in_battle:
            return

        self.vx = int(self.stage_data["base_speed"]) * self.direction
        self.pos_x += self.vx

        # Chance to change directions.
        if random.random() < 0.005:
            self.direction *= -1
            self._flip_image()

        # Chance to change vertical directions.
        elif random.random() < 0.005:
            self.direction_y *= -1

        # Chance to stop flying and start walking.
        elif random.random() < 0.001 and self.floor - self.pos_y<=100:
            self.is_flying = False

    def _teleport_pet(self):
        """
        Makes the pet teleport.
        """

        iteration_counter = 0

        def animate():
            nonlocal iteration_counter

            iteration_counter += 1
            scale = (
                # Shrinks if first phase
                1 - 0.05 * iteration_counter
                if self.is_teleporting
                # Expands if second phase
                else 0.05 * iteration_counter
            )

            # Pixmap changes accordingly to phase
            pixmap = self.original_pixmap.scaled(
                int(self.original_pixmap.width() * scale),
                self.original_pixmap.height()
            )
            self.setPixmap(pixmap)
            # Flips image accordingly with direction.
            if self.direction == 1:
                self._flip_image()

            if iteration_counter >= 20:
                # Teleports after first phase.
                if self.is_teleporting:
                    self.pos_x += random.randint(-1000, 1000)
                    self.pos_y += random.randint(-600, 600)
                # Resets the timer, and the pet starts to move normally again.
                self.reset_timer(callback=self._move_pet, interval=15)

        # Teleport first phase
        if not self.is_teleporting: 
            if random.random() < 0.001:
                self.reset_timer(callback=animate, interval=15)
                self.is_teleporting = True
        # Teleport second phase
        else:
            self.reset_timer(callback=animate, interval=15)
            self.is_teleporting = False
        

    def _jump_pet(self, min_height: int = -30, max_height: int = -15):
        """
        Makes the pet jump.

        Parameters
            min_height (int): minimum value.
            max_height (int): maximum value.
        """

        self.is_walking = False

        # Adds a random vertical speed to the pet.
        self.vy = random.randint(min_height, max_height)
        self.pos_y += self.vy

    def _evolve_pet(self):
        """
        Evolves the pet.
        """

        iteration_counter = 0
        # The sprite is whiten to simulate evolution.
        self._color_image(r=255, g=255, b=255, alpha=200)

        def animate():
            nonlocal iteration_counter
            iteration_counter += 1

            # When the evolution is over
            if iteration_counter >= 300:
                # Changes the pet sprite.
                self.evolution_stage += 1
                self.stage_data = self.manager.pet_data[self.evolution_line]["stages"][str(self.evolution_stage)]
                self.image_path = os.path.join(self.base_dir, f"./imgs/{self.stage_data["image"]}")
                self._load_image()

                # The original timer is run again.
                self.reset_timer(callback=self._move_pet, interval=15)

        # Starts a timer for the pet to evolve.
        self.reset_timer(callback=animate, interval=15)

    def lose_battle(self):
        """
        Does the animation when losing a battle.
        """

        self._jump_pet(min_height=-20, max_height=-10)
        self.vx = random.randint(10, 15) * -self.direction

    def win_battle(self):
        """
        Does the animation when winning a battle.
        """
        self._jump_pet(min_height=-10, max_height=-10)

    # ========== Mouse events ==========

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    # ========== Visual effects ==========

    def _flip_image(self):
        """
        Flips the image on the horizontal axis.
        """
        transform = QTransform()
        transform.scale(-1, 1)
        flipped_pixmap = self.pixmap().transformed(transform)
        self.setPixmap(flipped_pixmap)

    def _color_image(self, r: int, g: int, b: int, alpha: int = 200):
        """
        Colors the image.

        Parameters:
            alpha (int): Transparency.
            r (int): Color red.
            g (int): Color green.
            b (int): Color blue.
        """
        pixmap = self.pixmap().copy()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(r, g, b, alpha))
        painter.end()
        self.setPixmap(pixmap)

    # ========== Utility Functions ==========

    def reset_timer(self, callback, interval: int =15):
        """
        Resets the pet timer and connects a new callback.

        Parameters:
            callback: The new function that will be run every x seconds.
            interval (int): The interval (in milliseconds).
        """
        self.timer.stop()
        try:
            self.timer.timeout.disconnect()
        except TypeError:
            pass
    
        self.timer.timeout.connect(callback)
        self.timer.start(interval)

    def _end_delay(self):
        """
        Exit pause mode.
        """
        self.reset_timer(callback=self._move_pet, interval=15)

    def show_info(self):
        """
        Shows the pet info.
        """
        self.info_window.show()

    def close_pet(self):
        """
        Close the pet window, destroy it and remove it from the manager's pet list.
        """
        self.manager.remove_pet(pet=self)
        self.close()      
        self.deleteLater()  