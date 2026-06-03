import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

from StartWindow import StartWindow

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet_names = set()
    for img in os.listdir("imgs"):
        pet_name = img.split("_")[0]
        pet_names.add(pet_name)
    
    logging.info(f"Starting pets: {', '.join(pet_names)}")

    start_window = StartWindow(pet_names=pet_names)
    start_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
