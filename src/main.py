# Desktop Pet
# Copyright (C) 2026 Bernardo Tameirão
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.

import sys
import os

from PyQt5.QtWidgets import QApplication

from StartWindow import StartWindow

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    start_window = StartWindow()
    start_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
