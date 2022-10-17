
import sys, os, os.path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt

# Connect UI file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # base_path : py code directory
    return os.path.join(base_path, "resource/ui/", relative_path)

form_tool = uic.loadUiType(resource_path('sub_tool.ui'))[0]