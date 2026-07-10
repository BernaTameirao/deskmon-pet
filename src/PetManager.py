import time
import random
import math
import json
import os
import sys

from PyQt5.QtCore import QTimer

from Wild import Wild
from InventoryWindow import InventoryWindow

class PetManager:
    def __init__(self, main_window):
        
        base_dir = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._get_pet_data_from_json(path=os.path.join(base_dir, "./data/data.json"))
        
        self.main_window = main_window
        self.inventory_window = InventoryWindow(manager=self)
        self.pets = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 20 frames/second

    def _get_pet_data_from_json(self, path):
        """
        Gets the pet data from the json file.
        """
        with open(path, "r", encoding="utf-8") as f:
            self.pet_data = json.load(f)

    def save_data_into_json(self, path):
        """
        Stores the pet data into a new json file.
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.pet_data, f, indent=4)

    def add_pet(self, pet):
        """
        Adds a pet to the list of managed pets.

        Parameters:
            pet: object to be added to the list.
        """
        self.pets.append(pet)

    def remove_pet(self, pet):
        """
        Removes a pet from the list of managed pets.

        Parameters:
            pet: object to be removed from the list.
        """
        if pet in self.pets:
            self.pets.remove(pet)

    def update(self):
        """
        Checks for interactions between the pets.
        """
        # Update the coords of every visible window to every pet.
        windows = self._get_windows()
        for pet in self.pets:
            pet.windows = windows

        # Gets a list of only avaliable pets.
        active_pets = [p for p in self.pets if not p.in_battle]
        
        for i, pet1 in enumerate(active_pets):
            for pet2 in active_pets[i+1:]:
                
                # TO DO: Fazer a lista iterar antes dos pets entrarem em batalha.
                # If all conditions are met, there is a random chance that a battle occurs.
                if self.check_proximity(pet1, pet2, proximity_x=100, proximity_y=100) and random.random() < 0.1:
                    self.battle(pet1, pet2)
        
        # Each tick has a chance to spawn a wild pet.
        if random.random() < 0.0005:
            self._spawn_wild_pet()

    
    def check_proximity(self, pet1, pet2, proximity_x: int = 100, proximity_y: int = 100):
        """
        Checks if two pets are close, and facing each other.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
            proximity_x (int): Maximum number of pixels in the x-axis for the interaction to occur.
            proximity_y (int): Maximum number of pixels in the y-axis for the interaction to occur.

        Returns:
            If all the conditions are met. (bool)
        """
        # Gets the distance between the pets.
        dx = abs(pet1.pos_x - pet2.pos_x)
        dy = abs(pet1.pos_y - pet2.pos_y)

        # Checks if they are facing each other.
        if pet1.pos_x < pet2.pos_x:
            facing_each_other = pet1.direction == 1 and pet2.direction == -1
        else:
            facing_each_other = pet1.direction == -1 and pet2.direction == 1
            
        return dx < proximity_x and dy < proximity_y and facing_each_other

    def battle(self, pet1, pet2):
        """
        Group the functions related to battle.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
        """

        winner = self.resolve_battle(pet1, pet2)
        self.handle_battle_result(pet1, pet2, winner)

    def resolve_battle(self, pet1, pet2):
        """
        Decides the winner of the battle.

        Parameters:
            pet1: First pet.
            pet2: Second pet.

        Returns:
            The winner of the battle. (object)
        """

        n = 5
        # Two moves are chosen at random.
        move1 = random.randint(1, n)
        time.sleep(0.01)
        move2 = random.randint(1, n)

        # A rock-paper-scissor like script decides the winner.
        # If tie, the winner is None
        if move1 == move2:
            return None
        
        if (move1 + 1) % n == move2:
            return pet1
        elif (move2 + 1) % n == move1:
            return pet2
        else: # If an error happens
            return None 

    def handle_battle_result(self, pet1, pet2, winner):
        """
        Animates the pets according to the battle results.

        Parameters:
            pet1: First pet.
            pet2: Second pet.
            winner: Pet that won the battle.
        """
        iteration_counter = 0
        pet1.in_battle = True
        pet2.in_battle = True

        def animate():
            nonlocal iteration_counter
            iteration_counter += 1

            # If the pet is moved to somewhere distant from the other pet, the battle ends.
            if not self.check_proximity(pet1, pet2, proximity_x=200, proximity_y=200):
                pet1.in_battle = False
                pet2.in_battle = False
                timer.stop()
                return

            # Idle animation that the pets do when in battle.
            offset_y = 5 * math.sin(iteration_counter * 0.5)
            if pet1.is_walking:
                pet1.pos_y = math.floor(pet1.floor + offset_y)
            if pet2.is_walking:
                pet2.pos_y = math.floor(pet2.floor + offset_y)
            
            # When the battle is over
            if iteration_counter >= 500:
                timer.stop()
                
                if winner is pet1:
                    pet1.win_battle()
                    pet2.lose_battle()
                    pet1.level += 1
                    
                elif winner is pet2:
                    pet1.lose_battle()
                    pet2.win_battle()
                    pet2.level += 1

                else:
                    pet1.win_battle()
                    pet2.win_battle()
                
                pet1.in_battle = False
                pet2.in_battle = False

        # Starts the timer for the battle animations.
        timer = QTimer()
        timer.timeout.connect(animate)
        timer.start(15)

    def _get_windows(self):
        """
        Gets the coords of every open window and sends to every pet.
        """
        import win32gui
        windows = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((hwnd, rect))

        win32gui.EnumWindows(enum_handler, None)

        # Removes the pets' own windows from the list.
        pet_ids = [int(pet.winId()) for pet in self.pets]
        filtered_windows = [rect for hwnd, rect in windows if hwnd not in pet_ids]

        # Sorts them and returns
        sorted_windows = sorted(filtered_windows, key=lambda a: a[1])
        return sorted_windows

    def _spawn_wild_pet(self):
        """
        Chooses a pet from some random rarity to spawn.
        """
        rarity = ""
        random_number = random.random()
        
        # Chooses the rarity randomly.
        if random_number < 1/64:
            rarity = "legendary"
        elif random_number < 1/32:
            rarity = "epic"
        elif random_number < 1/16:
            rarity = "rare"
        elif random_number < 1/4:
            rarity = "uncommon"
        else:
            rarity = "common"

        # Gets every pet belonging to that rarity.
        can_spawn = [name for name in self.pet_data if self.pet_data[name].get("rarity") == rarity]
        if not can_spawn:
            return

        # Chooses a random pet and spawns as a wild pet.
        name = random.choice(can_spawn)
        level = round(random.triangular(0, 100, 20))

        wild_pet = Wild(evolution_line=name, manager=self, level=level)
        wild_pet.show()
        self.add_pet(wild_pet)