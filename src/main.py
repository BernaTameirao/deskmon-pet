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

    start_window = StartWindow()
    start_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
