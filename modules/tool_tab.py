import os
import sys

import serial.tools.list_ports

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget, QComboBox

# Connect UI file (for ToolWindow if it uses a separate UI)
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "../resource/ui/", relative_path)

form_tool = uic.loadUiType(resource_path('sub_tool.ui'))[0]

class ToolWindow(QMainWindow, form_tool): # This class should be defined in a separate file if it's a standalone window
    def __init__(self):
        super(ToolWindow, self).__init__()
        self.setupUi(self)

    def return_tool(self):
        tmp_tool = self.LB_SelectedTool.text()
        if tmp_tool != "None":
            if tmp_tool.split(',')[0] == "1":
                return tmp_tool
            else:
                return 0

class ToolTab(QWidget):
    def __init__(self, parent=None, status_bar_callback=None):
        super().__init__(parent)
        self.parent_main_window = parent
        self.status_bar_callback = status_bar_callback

        self.second_tool_window = None # To hold the instance of ToolWindow

        self.setup_ui_elements()
        self._load_port_info()
        self.bind_events()

    def setup_ui_elements(self):
        self.PB_ToolPortReload = self.parent_main_window.PB_ToolPortReload
        self.CB_ToolModel = self.parent_main_window.CB_ToolModel
        self.CB_ToolModelCode = self.parent_main_window.CB_ToolModelCode
        self.CB_ToolPort = self.parent_main_window.CB_ToolPort
        self.CB_ToolBR = self.parent_main_window.CB_ToolBR
        self.PB_ToolAddConfigure = self.parent_main_window.PB_ToolAddConfigure
        self.LW_ToolConfigureList = self.parent_main_window.LW_ToolConfigureList
        self.LE_ToolSelect = self.parent_main_window.LE_ToolSelect
        self.PB_ToolDelConfigure = self.parent_main_window.PB_ToolDelConfigure
        self.PB_ToolModelMore = self.parent_main_window.PB_ToolModelMore

        # Initialize CB_ToolModelCode if it's not a direct part of the .ui loaded
        self.CB_ToolModelCode.hide()
        with open("resource/data/tools.csv", 'r') as f:
            lines = f.readlines()
            for line in lines:
                tmp_data = line[:-1].split(",")
                if int(tmp_data[3]):
                    self.CB_ToolModel.addItem(tmp_data[1])
                    self.CB_ToolModelCode.addItem(tmp_data[2])

    def bind_events(self):
        self.PB_ToolPortReload.clicked.connect(self._load_port_info)
        self.PB_ToolAddConfigure.clicked.connect(self.tool_add_configure)
        self.LW_ToolConfigureList.itemClicked.connect(self.tool_configure_select)
        self.PB_ToolDelConfigure.clicked.connect(self.tool_delete_configure)
        self.PB_ToolModelMore.clicked.connect(self.tool_more_load)

    def tool_add_configure(self):
        tmp_tool_model_index = self.CB_ToolModel.currentIndex()
        self.LW_ToolConfigureList.addItem(
            self.CB_ToolModel.currentText() + "," +
            self.CB_ToolModelCode.itemText(tmp_tool_model_index) + "," +
            self.CB_ToolPort.currentText() + "," +
            self.CB_ToolBR.currentText()
        )
        if self.status_bar_callback:
            self.status_bar_callback("Tool configuration added.")


    def tool_configure_select(self):
        self.LE_ToolSelect.setText(
            self.LW_ToolConfigureList.currentItem().text()
        )

    def tool_delete_configure(self):
        tmp_selected_configure = self.LW_ToolConfigureList.currentItem()

        if tmp_selected_configure is not None:
            if tmp_selected_configure.text() == self.LE_ToolSelect.text():
                self.LW_ToolConfigureList.takeItem(self.LW_ToolConfigureList.currentRow())
                self.LE_ToolSelect.clear()
                if self.status_bar_callback:
                    self.status_bar_callback(f" {tmp_selected_configure.text()} is deleted.")

    def tool_more_load(self):
        self.second_tool_window = ToolWindow()
        self.second_tool_window.show()
        # You might want to handle data exchange with this sub-window here.

    def _load_port_info(self):
        self.CB_ToolPort.clear()

        try:
            if sys.platform == 'linux':
                for i in os.listdir("/dev"):
                    if i.startswith("ttyUSB") or i.startswith("ttyACM"):
                        self.CB_ToolPort.addItem(f"/dev/{i}")
                if self.status_bar_callback:
                    self.status_bar_callback("Serial ports reloaded.")
            elif 'win32':
                # Linux에서도 사용할 수 있을 듯 해보이나, 테스트 필요
                ports = serial.tools.list_ports.comports()
                for port, desc, hwid in sorted(ports):
                    self.CB_ToolPort.addItem(f"{desc}")

        except Exception as e:
            print(e)
            if self.status_bar_callback:
                self.status_bar_callback(f"Error loading serial ports: {e}")

