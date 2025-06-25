import os
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog
from PyQt5.QtCore import Qt

class DeviceTab(QWidget):
    def __init__(self, parent=None, status_bar_callback=None):
        super().__init__(parent)
        self.parent_main_window = parent
        self.status_bar_callback = status_bar_callback
        self.workDirectory = "" # This will be set by the main window

        self.setup_ui_elements() # You'll need to define how UI elements from main.ui are accessed
                                # This might involve passing specific UI elements or their names
                                # or creating them dynamically here if they are solely for this tab.
                                # For simplicity in this example, assume direct access or passed elements.

        self.device_list_load()
        self.bind_events()

    def setup_ui_elements(self):
        # Access UI elements from the parent_main_window (assuming they are public attributes)
        # Or, if you design your .ui files such that each tab's content is a separate QWidget,
        # you can load them here.
        self.PB_SelectDirectory = self.parent_main_window.PB_SelectDirectory
        self.TW_DeviceList = self.parent_main_window.TW_DeviceList
        self.LE_DeviceSearch = self.parent_main_window.LE_DeviceSearch
        self.LB_DeviceSelected = self.parent_main_window.LB_DeviceSelected
        self.label_Directory = self.parent_main_window.label_Directory


    def bind_events(self):
        self.TW_DeviceList.currentItemChanged.connect(self.device_selected_inlist)
        self.PB_SelectDirectory.clicked.connect(self.pb_select_directory_clicked)
        self.LE_DeviceSearch.textChanged.connect(self.le_device_search_changed)
        self.LE_DeviceSearch.returnPressed.connect(self.TW_DeviceList.setFocus)

    def pb_select_directory_clicked(self):
        tmp_directory = QFileDialog.getExistingDirectory(
            self,
            "Set Project Directory",
            "../",
            QFileDialog.ShowDirsOnly
        )
        if tmp_directory != "":
            self.workDirectory = tmp_directory
            if self.status_bar_callback:
                self.status_bar_callback(self.workDirectory)
            self.label_Directory.setText(self.workDirectory.split("/")[-1])

            if not os.path.isdir(f"{self.workDirectory}/.out"):
                os.mkdir(f"{self.workDirectory}/.out")

    def device_list_load(self):
        self.TW_DeviceList.setAlternatingRowColors(True)

        try:
            with open("./resource/data/avr_list.csv", 'r') as file:
                lines = file.readlines()
                buffer = ""

                for line in lines:
                    if buffer != line.split(",")[0]:
                        item_top = QTreeWidgetItem(self.TW_DeviceList)
                        item_top.setText(0, line.split(",")[0])
                        buffer = line.split(",")[0]

                    sub_item = QTreeWidgetItem()
                    sub_item.setText(0, line.split(",")[1][:-1])
                    item_top.addChild(sub_item)
        except FileNotFoundError:
            if self.status_bar_callback:
                self.status_bar_callback("Error: avr_list.csv not found.")

    def device_selected_inlist(self):
        tmp_device_name = self.TW_DeviceList.currentItem()
        self.TW_DeviceList.scrollToItem(tmp_device_name)

        if tmp_device_name and tmp_device_name.text(0) != "":
            if tmp_device_name.parent():
                self.LB_DeviceSelected.setText(tmp_device_name.text(0))
                if self.status_bar_callback:
                    self.status_bar_callback(f" {tmp_device_name.text(0)} is selected.")

    def le_device_search_changed(self):
        self.TW_DeviceList.clearSelection()
        self.TW_DeviceList.collapseAll()

        if self.LE_DeviceSearch.text() != "":
            tmp_search = self.TW_DeviceList.findItems(self.LE_DeviceSearch.text(), Qt.MatchContains | Qt.MatchRecursive, 0)
            if tmp_search:
                self.TW_DeviceList.scrollToItem(tmp_search[-1])
                self.TW_DeviceList.setCurrentItem(tmp_search[-1])

                for item in tmp_search:
                    item.setSelected(1)
                    try:
                        self.TW_DeviceList.expandItem(item.parent())
                    except Exception as e:
                        continue

            tmp_search_top = self.TW_DeviceList.findItems(self.LE_DeviceSearch.text(), Qt.MatchContains, 0)
            if tmp_search_top:
                for item in tmp_search_top:
                    item.setSelected(0)

            if self.status_bar_callback:
                self.status_bar_callback(f" There are {len(tmp_search) - len(tmp_search_top)} match(es).")
        else:
            if self.status_bar_callback:
                self.status_bar_callback(" There are 0 match(es).")