import sys
import os
import os.path

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Import tab modules
from modules.device_tab import DeviceTab
from modules.library_tab import LibraryTab
from modules.tool_tab import ToolTab, ToolWindow # ToolWindow might also need to be imported if it's a separate class
from modules.preview_tab import PreviewTab

# Connect UI file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "resource/ui/", relative_path)

form_main = uic.loadUiType(resource_path('main.ui'))[0]

# global variable - consider moving this into the main window class if possible
# workDirectory: str = "" # Moved to DeviceTab and passed via callback


class WindowMainClass(QMainWindow, form_main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ================================================================================
        # Preset
        self.setWindowIcon(QIcon('resource/img/ADU.svg'))
        self.setWindowTitle("AVR Development Utility")

        # Set button icons (if they are on the main window and not tab-specific)
        self.PB_SelectDirectory.setIcon(QIcon('resource/img/document-open-symbolic.svg'))
        self.PB_ToolPortReload.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))
        self.PB_PreviewLoadConfigure.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))

        # Initialize status bar
        self.statusBar().showMessage(" Application Started")

        # ================================================================================

        # Add widgets to the tabs
        self._initProgammingTabs()
        # self._initInformationTabs()


        # Initial tab selection (can be done here or in individual tab modules if they need to update on activation)
        self.MainTab.setCurrentIndex(0)
        self.Programming.setCurrentIndex(0)
        self.Information.setCurrentIndex(0) # Assuming Information tab is empty or handled separately

        # ================================================================================
        # Shortcut (can remain in main if they control main window tabs directly)
        self._initShortKeys()


    def update_status_bar(self, message):
        """Callback function to update the main window's status bar."""
        self.statusBar().showMessage(message)

    # Callbacks to get data from other tabs for the Preview tab
    def get_selected_device_code(self):
        return self.device_tab.LB_DeviceSelected.text()

    def get_library_list_items(self):
        items = []
        for i in range(self.library_tab.LW_LibraryIncludeList.count()):
            items.append(self.library_tab.LW_LibraryIncludeList.item(i))
        return items

    def get_tool_list_items(self):
        items = []
        for i in range(self.tool_tab.LW_ToolConfigureList.count()):
            items.append(self.tool_tab.LW_ToolConfigureList.item(i))
        return items

    def get_work_directory_path(self):
        return self.device_tab.workDirectory

    # ================================================================================
    # Shortcut (retained in main as they control main window tabs directly)
    def _bindShortkeyLeft(self):
        tmp_index: int = self.MainTab.currentIndex()
        if tmp_index == 0:  # Programming tab
            current_prog_index = self.Programming.currentIndex()
            if current_prog_index > 0:
                self.Programming.setCurrentIndex(current_prog_index - 1)
        elif tmp_index == 1:  # Information tab
            current_info_index = self.Information.currentIndex()
            if current_info_index > 0:
                self.Information.setCurrentIndex(current_info_index - 1)

    def _bindShortKeyRight(self):
        tmp_index: int = self.MainTab.currentIndex()
        if tmp_index == 0:  # Programming tab
            current_prog_index = self.Programming.currentIndex()
            if current_prog_index < self.Programming.count() - 1:
                self.Programming.setCurrentIndex(current_prog_index + 1)
        elif tmp_index == 1:  # Information tab
            current_info_index = self.Information.currentIndex()
            if current_info_index < self.Information.count() - 1:
                self.Information.setCurrentIndex(current_info_index + 1)

    def _bindShortkeySlash(self):
        main_tab = self.MainTab.currentIndex()
        if main_tab == 0:  # Programming tab
            programming_tab = self.Programming.currentIndex()

            match programming_tab:
                case 0 : self.device_tab.LE_DeviceSearch.setFocus()
                case 3:  self.tool_tab.LE_ToolSelect.setFocus()
                case 4:  self.library_tab.LE_LibrarySelect.setFocus()
                case 5:  self.preview_tab.TE_Preview.setFocus()

    def _initShortKeys(self):
        QShortcut(QKeySequence("Alt+up"), self).activated.connect(
            lambda: self.MainTab.setCurrentIndex(self.MainTab.currentIndex()-1)
        )
        QShortcut(QKeySequence("Alt+down"), self).activated.connect(
            lambda: self.MainTab.setCurrentIndex(self.MainTab.currentIndex()+1)
        )
        QShortcut(QKeySequence("Alt+left"), self).activated.connect(self._bindShortkeyLeft)
        QShortcut(QKeySequence("Alt+right"), self).activated.connect(self._bindShortKeyRight)
        QShortcut(QKeySequence("/"), self).activated.connect(self._bindShortkeySlash)


    # Add widgets to the tabs
    # Assuming your main.ui has QTabWidget named MainTab, Programming, Information
    # And within those, specific pages for each tab content.
    # You'll need to adapt this based on how your .ui is structured.
    # For instance, if each tab in Programming is a QWidget in the designer,
    # you can replace that QWidget with your custom tab instance.

    # Example for replacing a placeholder widget in a tab (assuming `main.ui` has a QWidget named `device_placeholder_widget` on the Device tab):
    def _initProgammingTabs(self):
        # Initialize and add tabs
        self.device_tab = DeviceTab(self, self.update_status_bar)
        self.library_tab = LibraryTab(self, self.update_status_bar)
        self.tool_tab = ToolTab(self, self.update_status_bar)
        self.preview_tab = PreviewTab(
            self,
            self.update_status_bar,
            self.get_selected_device_code,
            self.get_library_list_items,
            self.get_tool_list_items,
            self.get_work_directory_path
        )

        # Find the index of the Device tab (e.g., Programming tab, first sub-tab)
        programming_tab_index = self.MainTab.indexOf(self.Programming) # Get index of Programming tab
        if programming_tab_index != -1:
            # Assuming 'Device' tab is the first sub-tab in 'Programming'
            device_tab_widget = self.Programming.widget(0) # Get the existing widget at index 0 of Programming tab
            if device_tab_widget:
                # Remove the old widget
                self.Programming.removeTab(0)
                # Insert your custom tab widget
                self.Programming.insertTab(0, self.device_tab, "Device SET")
                self.Programming.setCurrentIndex(0) # Set current to the new tab

            library_tab_widget = self.Programming.widget(1) # Assuming Library is at index 1
            if library_tab_widget:
                self.Programming.removeTab(1)
                self.Programming.insertTab(1, self.library_tab, "Library")

            tool_tab_widget = self.Programming.widget(2) # Assuming Tool is at index 2
            if tool_tab_widget:
                self.Programming.removeTab(2)
                self.Programming.insertTab(2, self.tool_tab, "Tool")

            preview_tab_widget = self.Programming.widget(3) # Assuming Preview is at index 3
            if preview_tab_widget:
                self.Programming.removeTab(3)
                self.Programming.insertTab(3, self.preview_tab, "Preview")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowMainClass()
    mainWindow.show()
    sys.exit(app.exec_())