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
        self.PB_ProgrammerPortReload.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))

        # (TAB) AVR SET
        self.avr_list_load()  # Load the List of AVRs and the List of Programmer

        # (TAB) Programmer
        self.programmer_port_load()  # load Port data (ex /dev/ttyUSB0)
        self.statusBar().showMessage(' Set Project Directory')  # Status Bar

        # ================================================================================
        # Event
        self.PB_makeMakefile.clicked.connect(self.make_makefile)                    # When PushB_make clicked -> make Makefile

        # (TAB) AVR SET
        self.TW_avrList.currentItemChanged.connect(self.avr_selected_inlist)        # if AVR is first selected or is changed to other AVR
        self.PB_SelectDirectory.clicked.connect(self.pb_select_directory_clicked)   # When PushB_Directory clicked
        self.LE_avrSearch.textChanged.connect(self.le_avr_search_changed)           # When Avr_search changed
        self.PB_ProgrammerPortReload.clicked.connect(self.programmer_port_load)     # When PushB_PortReload clicked

        # (TAB) Library
        self.PB_LibraryInclude.clicked.connect(self.library_include)
        self.PB_LibraryExclude.clicked.connect(self.library_exclude)

        # (TAB) Programmer
        self.PB_ProgrammerAddConfigure.clicked.connect(self.programmer_add_configure)
        self.LW_ProgrammerConfigureList.itemClicked.connect(self.programmer_configure_select)
        self.PB_ProgrammerDelConfigure.clicked.connect(self.programmer_delete_configure)

    # ================================================================================
    # Select Project Directory(Using Dialog)
    def pb_select_directory_clicked(self):
        tmp = QFileDialog.getExistingDirectory(
            self,
            self.tr("Set Project Directory"),
            "../",
            QFileDialog.ShowDirsOnly
        )
        if tmp != "":
            global workDirectory
            workDirectory = tmp
            self.statusBar().showMessage(workDirectory)
            self.label_Directory.setText(workDirectory.split("/")[-1])

        self.library_load()

    # ================================================================================
    # Load the List of AVRs and the List of Programmer
    def avr_list_load(self):
        self.TW_avrList.setAlternatingRowColors(True)

        with open("./resource/avr_list.txt", 'r') as file:
            lines = file.readlines()
            buffer = ""

            for line in lines:
                # make AVR type(e: ATmega, ATtiny etc.)
                # Don't make same headers
                if buffer != line.split(",")[0]:
                    item_top = QTreeWidgetItem(self.TW_avrList)
                    item_top.setText(0, line.split(",")[0])
                    buffer = line.split(",")[0]

                # add AVR List(e: ATmega328P:m328p)
                # Make sub Items
                sub_item = QTreeWidgetItem()
                sub_item.setText(0, line.split(",")[1])
                sub_item.setText(1, line.split(",")[2][:-1])  # delete \n
                item_top.addChild(sub_item)

        # load programmers
        with open("resource/programmers.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                self.CB_ProgrammerModel.addItem(line[:-1].split(",")[1])

    # ================================================================================
    # if AVR is first selected or is changed to other AVR
    # load selected AVR-name from the Tree and change label text
    def avr_selected_inlist(self):
        tmp_avr_name = self.TW_avrList.currentItem()
        if tmp_avr_name != None and tmp_avr_name.text(1) != "":
            self.LB_mcuSelected.setText(tmp_avr_name.text(0))
            self.statusBar().showMessage((" {} is selected.".format(tmp_avr_name.text(0))))

            global avrCode
            avrCode = self.TW_avrList.currentItem().text(1)

    # ================================================================================

    def le_avr_search_changed(self):
        self.TW_avrList.clearSelection()
        self.TW_avrList.collapseAll()

        # check whether Line Edit is blank
        if self.LE_avrSearch.text() != "":
            # find top | child
            tmp_search = self.TW_avrList.findItems(self.LE_avrSearch.text(), Qt.MatchContains | Qt.MatchRecursive, 0)
            if tmp_search:
                for item in tmp_search:
                    item.setSelected(1)

                    # if item is already parent
                    try:
                        self.TW_avrList.expandItem(item.parent())
                    except Exception as e:
                        continue

            # find top
            tmp_search_top = self.TW_avrList.findItems(self.LE_avrSearch.text(), Qt.MatchContains, 0)
            if tmp_search_top:
                for item in tmp_search_top:
                    item.setSelected(0)

            self.statusBar().showMessage((" There are {} match(es).".format(len(tmp_search) - len(tmp_search_top))))

        else:
            self.statusBar().showMessage(" There are 0 match(es).")

    # ================================================================================
    # (TAB) Library
    # Library Load
    def library_load(self):
        global workDirectory
        if workDirectory != "":
            self.LW_LibraryExcludeList.clear()
            self.LW_LibraryIncludeList.clear()

            # if there aren't directory, make
            if os.path.exists(workDirectory + "/libraries") != 1:
                os.mkdir(workDirectory + "/libraries")

            # only load folder
            for fileList in os.listdir(workDirectory + "/libraries"):
                if os.path.isdir(workDirectory + "/libraries/" + fileList):
                    self.LW_LibraryExcludeList.addItem(fileList)

            self.LW_LibraryExcludeList.sortItems()

    # library Include (When button is clicked)
    def library_include(self):
        tmp_library_name = self.LW_LibraryExcludeList.currentItem()
        if tmp_library_name != None:
            self.LW_LibraryIncludeList.addItem(tmp_library_name.text())
            self.LW_LibraryExcludeList.takeItem(self.LW_LibraryExcludeList.currentRow())
            self.LW_LibraryIncludeList.sortItems()
            self.LW_LibraryExcludeList.clearSelection()

    # Library Exclude (When button is clicked)
    def library_exclude(self):
        tmp_library_name = self.LW_LibraryIncludeList.currentItem()
        if tmp_library_name != None:
            self.LW_LibraryExcludeList.addItem(tmp_library_name.text())
            self.LW_LibraryIncludeList.takeItem(self.LW_LibraryIncludeList.currentRow())
            self.LW_LibraryExcludeList.sortItems()
            self.LW_LibraryIncludeList.clearSelection()

    # ================================================================================
    # (TAB) Programmer
    def programmer_add_configure(self):
        self.LW_ProgrammerConfigureList.addItem(
            self.CB_ProgrammerModel.currentText() + "," +
            self.CB_ProgrammerPort.currentText() + "," +
            self.CB_ProgrammerBR.currentText()
        )

    def programmer_configure_select(self):
        self.LE_ProgrammerSelect.setText(
            self.LW_ProgrammerConfigureList.currentItem().text()
        )

    def programmer_delete_configure(self):
        # check selected item and LE time is same
        tmp_selected_configure = self.LW_ProgrammerConfigureList.currentItem()
        if tmp_selected_configure != None:
            if tmp_selected_configure.text() == self.LE_ProgrammerSelect.text():
                self.LW_ProgrammerConfigureList.takeItem(self.LW_ProgrammerConfigureList.currentRow())
                self.LE_ProgrammerSelect.clear()

    # ================================================================================
    # Programmer Port Load
    def programmer_port_load(self):
        self.CB_ProgrammerPort.clear()

        # load Port
        for i in os.listdir('/dev'):
            if i[0:6] == "ttyUSB" or i[0:6] == "ttyACM":
                self.CB_ProgrammerPort.addItem("/dev/" + i)

    # ================================================================================
    #
    def make_makefile(self):
        print("Hey!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
