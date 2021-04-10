#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main module of this package call main with commandline parameters (which get passed to Qt)
or execute the csis application module which does this for you.
"""

import sys

from PySide2.QtWidgets import QApplication
from src.game import Game


def main(argv):
    app = QApplication(argv)
    game = Game(app)
    game.show()

    sys.exit(app.exec_())
