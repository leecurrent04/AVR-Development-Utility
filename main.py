import sys, os, os.path
# from typing import Set

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt


# Connect UI file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # base_path : py code directory
    return os.path.join(base_path, "resource/", relative_path)


form_class = uic.loadUiType(resource_path('main.ui'))[0]

# global variable
avrCode: str = ""  # e: m168(ATmega168)
workDirectory: str = ""


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ================================================================================
        # Preset
        # Button's Icon
        self.setWindowIcon(QIcon('resource/img/ADU.svg'))
        self.setWindowTitle("AVR Development Utility")

        self.PB_SelectDirectory.setIcon(QIcon('resource/img/document-open-symbolic.svg'))
        self.PB_ToolPortReload.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))
        self.PB_PreviewLoadConfigure.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))

        # (TAB) Device SET
        self.device_list_load()  # Load the List of AVRs and the List of Programmer

        # (TAB) Tool
        self.tool_port_load()  # load Port data (ex /dev/ttyUSB0)
        self.statusBar().showMessage(' Set Project Directory')  # Status Bar

        # ================================================================================
        # Event
        self.PB_PreviewMakeFile.clicked.connect(self.make_makefile)                    # When PushB_make clicked -> make Makefile

        # (TAB) Device SET
        self.TW_DeviceList.currentItemChanged.connect(self.device_selected_inlist)  # if AVR is first selected or is changed to other AVR
        self.PB_SelectDirectory.clicked.connect(self.pb_select_directory_clicked)   # When PushB_Directory clicked
        self.LE_DeviceSearch.textChanged.connect(self.le_device_search_changed)     # When Avr_search changed
        self.PB_ToolPortReload.clicked.connect(self.tool_port_load)                 # When PushB_PortReload clicked

        # (TAB) Library
        self.PB_LibraryAdd.clicked.connect(self.library_add)
        self.PB_LibraryDelete.clicked.connect(self.library_delete)
        self.LW_LibraryIncludeList.itemClicked.connect(self.library_selected_inlist)

        # (TAB) Tool
        self.PB_ToolAddConfigure.clicked.connect(self.tool_add_configure)
        self.LW_ToolConfigureList.itemClicked.connect(self.tool_configure_select)
        self.PB_ToolDelConfigure.clicked.connect(self.tool_delete_configure)

    # ================================================================================
    # Select Project Directory(Using Dialog)
    def pb_select_directory_clicked(self):
        tmp_directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Set Project Directory"),
            "../",
            QFileDialog.ShowDirsOnly
        )
        if tmp_directory != "":
            global workDirectory
            workDirectory = tmp_directory
            self.statusBar().showMessage(workDirectory)
            self.label_Directory.setText(workDirectory.split("/")[-1])

        #self.library_load()

    # ================================================================================
    # Load the List of AVRs and the List of Programmer
    def device_list_load(self):
        self.TW_DeviceList.setAlternatingRowColors(True)

        with open("./resource/avr_list.txt", 'r') as file:
            lines = file.readlines()
            buffer = ""

            for line in lines:
                # make AVR type(e: ATmega, ATtiny etc.)
                # Don't make same headers
                if buffer != line.split(",")[0]:
                    item_top = QTreeWidgetItem(self.TW_DeviceList)
                    item_top.setText(0, line.split(",")[0])
                    buffer = line.split(",")[0]

                # add AVR List(e: ATmega328P:m328p)
                # Make sub Items
                sub_item = QTreeWidgetItem()
                sub_item.setText(0, line.split(",")[1])
                sub_item.setText(1, line.split(",")[2][:-1])  # delete \n
                item_top.addChild(sub_item)

        # load Tools
        with open("resource/tools.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                self.CB_ToolModel.addItem(line[:-1].split(",")[1])

    # ================================================================================
    # if AVR is first selected or is changed to other AVR
    # load selected AVR-name from the Tree and change label text
    def device_selected_inlist(self):
        tmp_device_name = self.TW_DeviceList.currentItem()
        if tmp_device_name != None and tmp_device_name.text(1) != "":
            self.LB_DeviceSelected.setText(tmp_device_name.text(0))
            self.statusBar().showMessage((" {} is selected.".format(tmp_device_name.text(0))))

            global avrCode
            avrCode = self.TW_DeviceList.currentItem().text(1)

    # ================================================================================

    def le_device_search_changed(self):
        self.TW_DeviceList.clearSelection()
        self.TW_DeviceList.collapseAll()

        # check whether Line Edit is blank
        if self.LE_DeviceSearch.text() != "":
            # find top | child
            tmp_search = self.TW_DeviceList.findItems(self.LE_DeviceSearch.text(), Qt.MatchContains | Qt.MatchRecursive, 0)
            if tmp_search:
                for item in tmp_search:
                    item.setSelected(1)

                    # if item is already parent
                    try:
                        self.TW_DeviceList.expandItem(item.parent())
                    except Exception as e:
                        continue

            # find top
            tmp_search_top = self.TW_DeviceList.findItems(self.LE_DeviceSearch.text(), Qt.MatchContains, 0)
            if tmp_search_top:
                for item in tmp_search_top:
                    item.setSelected(0)

            self.statusBar().showMessage((" There are {} match(es).".format(len(tmp_search) - len(tmp_search_top))))

        else:
            self.statusBar().showMessage(" There are 0 match(es).")

    # ================================================================================
    # (TAB) Library
    # library Include (When button is clicked)
    def library_add(self):
        # count same libraries
        same_library_num:int = 0

        # return data : ('[file path]','file type')
        tmp_files,_ = QFileDialog.getOpenFileNames(
            self,
            "Select Library Source Code Files",
            "./",
            "C/C++(*.c *.cpp)"
        )

        # empty list return 0, other return 1
        if tmp_files:
            for tmp_file_path in tmp_files:
                tmp_file_name = "{} ({})".format(tmp_file_path.split("/")[-1],tmp_file_path)
                same_library = self.LW_LibraryIncludeList.findItems(tmp_file_name,Qt.MatchExactly)

                if same_library:
                    if same_library[0].text() != tmp_file_name:
                        self.LW_LibraryIncludeList.addItem(tmp_file_name)
                    else:
                        same_library_num += 1
                else:
                    self.LW_LibraryIncludeList.addItem(tmp_file_name)

        self.statusBar().showMessage((" Added except for {} duplicate entries.".format(same_library_num)))

    # library Selected
    def library_selected_inlist(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()
        if tmp_library_selected != None and tmp_library_selected.text() != "":
            self.LE_LibrarySelect.setText(tmp_library_selected.text())
            #self.statusBar().showMessage((" {} is selected.".format(tmp_library_selected.text().split(" ")[0])))

    # Library Exclude (When button is clicked)
    def library_delete(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()
        if tmp_library_selected!= None:
            if tmp_library_selected.text() == self.LE_LibrarySelect.text():
                self.LW_LibraryIncludeList.takeItem(self.LW_LibraryIncludeList.currentRow())
                self.LE_LibrarySelect.clear()

            self.statusBar().showMessage((" {} is deleted.".format(tmp_library_selected.text().split(" ")[0])))

    # ================================================================================
    # (TAB) Tool
    def tool_add_configure(self):
        self.LW_ToolConfigureList.addItem(
            self.CB_ToolModel.currentText() + "," +
            self.CB_ToolPort.currentText() + "," +
            self.CB_ToolBR.currentText()
        )

    def tool_configure_select(self):
        self.LE_ToolSelect.setText(
            self.LW_ToolConfigureList.currentItem().text()
        )

    def tool_delete_configure(self):
        # check selected item and LE time is same
        tmp_selected_configure = self.LW_ToolConfigureList.currentItem()
        if tmp_selected_configure != None:
            if tmp_selected_configure.text() == self.LE_ToolSelect.text():
                self.LW_ToolConfigureList.takeItem(self.LW_ToolConfigureList.currentRow())
                self.LE_ToolSelect.clear()

            self.statusBar().showMessage((" {} is deleted.".format(tmp_selected_configure.text())))

    # ================================================================================
    # Tool Port Load
    def tool_port_load(self):
        self.CB_ToolPort.clear()

        # load Port
        for i in os.listdir('/dev'):
            if i[0:6] == "ttyUSB" or i[0:6] == "ttyACM":
                self.CB_ToolPort.addItem("/dev/" + i)

    # ================================================================================
    #
    def make_makefile(self):
        print("Hey!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
