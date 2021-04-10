
import sys
from PySide2 import QtGui  # , QtWidgets
# TODO refactor reduce dependancies

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QGuiApplication(sys.argv)
    '''
    QtWidgets.QMessageBox.critical(None, "OpenGL textures",
                                   "PyOpenGL must be installed to run this example.",
                                   QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Default,
                                   QtWidgets.QMessageBox.NoButton)
    '''
    sys.exit(1)
