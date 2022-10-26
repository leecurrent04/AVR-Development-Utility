import sys
import os
import os.path
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


form_main = uic.loadUiType(resource_path('main.ui'))[0]
form_tool = uic.loadUiType(resource_path('sub_tool.ui'))[0]

# global variable
workDirectory: str = ""


class WindowMainClass(QMainWindow, form_main):
    def __init__(self):
        super().__init__()
        self.second = None
        self.setupUi(self)

        # ================================================================================
        # Preset
        # Button's Icon
        self.setWindowIcon(QIcon('resource/img/ADU.svg'))
        self.setWindowTitle("AVR Development Utility")

        self.PB_SelectDirectory.setIcon(QIcon('resource/img/document-open-symbolic.svg'))
        self.PB_ToolPortReload.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))
        self.PB_PreviewLoadConfigure.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))

        # set TAB Current Index
        self.MainTab.setCurrentIndex(0)
        self.Programming.setCurrentIndex(0)
        self.Information.setCurrentIndex(0)

        # (TAB) Device SET
        self.device_list_load()  # Load the List of AVRs and the List of Programmer

        # (TAB) Tool
        self.tool_port_load()  # load Port data (ex /dev/ttyUSB0)
        self.statusBar().showMessage(" Set Project Directory")  # Status Bar

        # ================================================================================
        # Event
        # (TAB) Device SET
        self.TW_DeviceList.currentItemChanged.connect(self.device_selected_inlist)  # AVR is selected or changed
        self.PB_SelectDirectory.clicked.connect(self.pb_select_directory_clicked)   # When PushB_Directory clicked
        self.LE_DeviceSearch.textChanged.connect(self.le_device_search_changed)     # When Avr_search changed
        self.PB_ToolPortReload.clicked.connect(self.tool_port_load)                 # When PushB_PortReload clicked
        self.LE_DeviceSearch.returnPressed.connect(self.TW_DeviceList.setFocus)

        # (TAB) Library
        self.PB_LibraryAdd.clicked.connect(self.library_add)
        self.PB_LibraryDelete.clicked.connect(self.library_delete)
        self.LW_LibraryIncludeList.itemClicked.connect(self.library_selected_inlist)

        # (TAB) Tool
        self.PB_ToolAddConfigure.clicked.connect(self.tool_add_configure)
        self.LW_ToolConfigureList.itemClicked.connect(self.tool_configure_select)
        self.PB_ToolDelConfigure.clicked.connect(self.tool_delete_configure)
        self.PB_ToolModelMore.clicked.connect(self.tool_more_load)

        # (TAB) Preview
        self.PB_PreviewLoadConfigure.clicked.connect(self.makefile_data_load)
        self.PB_PreviewMakeFile.clicked.connect(self.make_makefile)                 # make Makefile

        # Shortcut
        QShortcut(QKeySequence("Alt+up"), self).activated.connect(
            lambda: self.MainTab.setCurrentIndex(self.MainTab.currentIndex()-1)
        )

        QShortcut(QKeySequence("Alt+down"), self).activated.connect(
            lambda: self.MainTab.setCurrentIndex(self.MainTab.currentIndex()+1)
        )

        QShortcut(QKeySequence("Alt+left"), self).activated.connect(self.shortcut_left_arrow)
        QShortcut(QKeySequence("Alt+right"), self).activated.connect(self.shortcut_right_arrow)

        QShortcut(QKeySequence("/"), self).activated.connect(self.shortcut_input)

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

            # make ".out/"
            if not os.path.isdir("%s/.out" % workDirectory):
                os.mkdir("%s/.out" % workDirectory)

        # self.library_load()

    # ================================================================================
    # Load the List of AVRs and the List of Programmer
    def device_list_load(self):
        self.TW_DeviceList.setAlternatingRowColors(True)

        with open("./resource/data/avr_list.csv", 'r') as file:
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
                sub_item.setText(0, line.split(",")[1][:-1])
                # sub_item.setText(1, line.split(",")[2][:-1])
                item_top.addChild(sub_item)

        # load Tools
        self.CB_ToolModelCode.hide()
        with open("resource/data/tools.csv", 'r') as f:
            lines = f.readlines()
            for line in lines:
                # delete \n
                tmp_data = line[:-1].split(",")

                # Category, name, code, default
                if int(tmp_data[3]):
                    self.CB_ToolModel.addItem(tmp_data[1])
                    self.CB_ToolModelCode.addItem(tmp_data[2])

    # ================================================================================
    # if AVR is first selected or is changed to other AVR
    # load selected AVR-name from the Tree and change label text
    def device_selected_inlist(self):
        tmp_device_name = self.TW_DeviceList.currentItem()
        self.TW_DeviceList.scrollToItem(tmp_device_name)

        if tmp_device_name != None and tmp_device_name.text(0) != "":
            if tmp_device_name.parent() != None:
                self.LB_DeviceSelected.setText(tmp_device_name.text(0))
                self.statusBar().showMessage((" %s is selected."%(tmp_device_name.text(0))))

    # ================================================================================
    # device search

    def le_device_search_changed(self):
        self.TW_DeviceList.clearSelection()
        self.TW_DeviceList.collapseAll()

        # check whether Line Edit is blank
        if self.LE_DeviceSearch.text() != "":
            # find top | child
            tmp_search = self.TW_DeviceList.findItems(self.LE_DeviceSearch.text(), Qt.MatchContains | Qt.MatchRecursive, 0)
            if tmp_search:
                self.TW_DeviceList.scrollToItem(tmp_search[-1])
                self.TW_DeviceList.setCurrentItem(tmp_search[-1])

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

            self.statusBar().showMessage((" There are %d match(es)." % (len(tmp_search) - len(tmp_search_top))))

        else:
            self.statusBar().showMessage(" There are 0 match(es).")

    # ================================================================================
    # (TAB) Library
    # library Include (When button is clicked)
    def library_add(self):
        # return data : ('[file path]','file type')
        tmp_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Library Source Code Files",
            "./",
            "C(*.c)"
        )

        if tmp_files:
            overlap_library_num:int = 0

            for tmp_file in tmp_files:
                tmp_file_name = "%s (%s)" % (tmp_file.split("/")[-1], tmp_file)
                overlap_library = self.LW_LibraryIncludeList.findItems(tmp_file_name, Qt.MatchExactly)

                # Check overlap entries
                if overlap_library:
                    overlap_library_num += 1
                # Add files
                else:
                    self.LW_LibraryIncludeList.addItem(tmp_file_name)

                self.statusBar().showMessage((" Added except for %d duplicate entries." % overlap_library_num))

    # library Selected
    def library_selected_inlist(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()
        if tmp_library_selected != None and tmp_library_selected.text() != "":
            self.LE_LibrarySelect.setText(tmp_library_selected.text())
            # self.statusBar().showMessage((" {} is selected.".format(tmp_library_selected.text().split(" ")[0])))

    # Library Exclude (When button is clicked)
    def library_delete(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()

        # check if current item is null
        if tmp_library_selected!= None:
            # check if selected item nas LE item is same
            if tmp_library_selected.text() == self.LE_LibrarySelect.text():
                self.LW_LibraryIncludeList.takeItem(self.LW_LibraryIncludeList.currentRow())
                self.LE_LibrarySelect.clear()
                self.statusBar().showMessage((" %s is deleted."%(tmp_library_selected.text().split(" ")[0])))

    # ================================================================================
    # (TAB) Tool
    def tool_add_configure(self):
        tmp_tool_model_index = self.CB_ToolModel.currentIndex()
        self.LW_ToolConfigureList.addItem(
            self.CB_ToolModel.currentText() + "," +
            self.CB_ToolModelCode.itemText(tmp_tool_model_index) + "," +
            self.CB_ToolPort.currentText() + "," +
            self.CB_ToolBR.currentText()
        )

    def tool_configure_select(self):
        self.LE_ToolSelect.setText(
            self.LW_ToolConfigureList.currentItem().text()
        )

    def tool_delete_configure(self):
        tmp_selected_configure = self.LW_ToolConfigureList.currentItem()

        # check if current item is null
        if tmp_selected_configure != None:
            # check if selected item and LE itme is same
            if tmp_selected_configure.text() == self.LE_ToolSelect.text():
                self.LW_ToolConfigureList.takeItem(self.LW_ToolConfigureList.currentRow())
                self.LE_ToolSelect.clear()

                self.statusBar().showMessage((" %s is deleted."%(tmp_selected_configure.text())))

    # ================================================================================
    # Tool load sub window

    def tool_more_load(self):
        print("clicked")
        # self.hide()
        self.second = ToolWindow()
        # self.second.show()
        print(self.second.LB_SelectedTool.text())
        # self.second.exec()
        # self.show()

    # ================================================================================
    # Tool Port Load
    def tool_port_load(self):
        self.CB_ToolPort.clear()

        # load Port
        for i in os.listdir("/dev"):
            if i[0:6] == "ttyUSB" or i[0:6] == "ttyACM":
                self.CB_ToolPort.addItem("/dev/" + i)

    # ================================================================================
    # (TAB) Preview
    def makefile_data_load(self):
        make_libraries: str = ""
        make_tool: str = ""
        tmp_file_data: str = ""
        avr_code: str = self.LB_DeviceSelected.text()

        # load libraries
        for n in range(self.LW_LibraryIncludeList.count()):
            # name.c (path) -> take path only
            line, _ = (self.LW_LibraryIncludeList.item(n).text()).split('(')[1].split(')')

            if n+1 == self.LW_LibraryIncludeList.count():
                make_libraries += "%s" % line
            else:
                make_libraries += "%s \\\n\t" % line
        
        # load tool
        for n in range(self.LW_ToolConfigureList.count()):
            # load data
            _, tmp_tool, tmp_port, tmp_baudrate = self.LW_ToolConfigureList.item(n).text().split(',')

            # Show error message
            if avr_code == "None":
                make_tool += "# [Warning] Check Device again.\n"

            if tmp_port == "":
                make_tool += "# [Warning] Check Port again.\n"
            else:
                tmp_port = "-P %s " % tmp_port

            if tmp_baudrate == "":
                make_tool += "# [Warning] Check Baudrate again.\n"
            else:
                tmp_baudrate = "-b %s " % tmp_baudrate

            # add upload code
            make_tool += "upload%d:\n\tavrdude -v -p %s -c %s %s%s-U flash:w:./.out/main.hex:i\n\n\n" % (
                n, avr_code, tmp_tool, tmp_port, tmp_baudrate
                )

        # Show error message
        if avr_code == "None":
            tmp_file_data = "# [Warning] Check Device again.\n"

        with open("./resource/data/Makefile", 'r') as tmp_resource:
            tmp_file_data += tmp_resource.read() % (make_libraries, avr_code, avr_code, make_tool)

        # show preview
        self.TE_Preview.setText(tmp_file_data)

    def make_makefile(self):
        # Check whether user has selected directory
        if workDirectory != "":
            # Check whether directory exists
            if os.path.isdir(workDirectory):
                with open(("%s/Makefile" % workDirectory), 'w') as fp:
                    fp.write(self.TE_Preview.toPlainText())

                self.statusBar().showMessage("Makefile is generated.")

            else:
                self.statusBar().showMessage("Work Directory does not exist")

        else:
            self.statusBar().showMessage("You must define Work Directory")

    # ================================================================================
    # Shortcut
    def shortcut_left_arrow(self):
        tmp_index: int = self.MainTab.currentIndex()
        if tmp_index == 0:
            # check if current index in min value
            if self.Programming.currentIndex != 0:
                self.Programming.setCurrentIndex(self.Programming.currentIndex()-1)
        elif tmp_index == 1:
            if self.Information.currentIndex != 0:
                self.Information.setCurrentIndex(self.Information.currentIndex()-1)

    def shortcut_right_arrow(self):
        tmp_index: int = self.MainTab.currentIndex()
        if tmp_index == 0:
            # check if current index is max value
            if self.Programming.currentIndex != self.Programming.count()-1:
                self.Programming.setCurrentIndex(self.Programming.currentIndex()+1)
        elif tmp_index == 1:
            if self.Information.currentIndex != self.Information.count()-1:
                self.Information.setCurrentIndex(self.Information.currentIndex()+1)

    def shortcut_input(self):
        main_tab = self.MainTab.currentIndex()
        if main_tab == 0:                   # Programming tab
            programming_tab = self.Programming.currentIndex()

            if programming_tab == 0:        # Device tab
                self.LE_DeviceSearch.setFocus()
            elif programming_tab == 3:      # Tool tab
                self.LE_ToolSelect.setFocus()
            elif programming_tab == 4:      # Library tab
                self.LE_LibrarySelect.setFocus()
            elif programming_tab == 5:      # Preview tab
                self.TE_Preview.setFocus()
        # elif main_tab == 1:


class ToolWindow(QMainWindow, form_tool):
    def __init__(self):
        super(ToolWindow, self).__init__()
        self.setupUi(self)
        # self.show()
        # self.connect(ButtonBox,)
        # print(WindowMainClass().LB_DeviceSelected.text())

    def return_tool(self):
        tmp_tool = self.LB_SelectedTool.text()
        if tmp_tool != "None":
            if tmp_tool.split(',')[0] == "1":
                return tmp_tool
            else:
                return 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowMainClass()
    mainWindow.show()
    app.exec_()
