from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog

class LibraryTab(QWidget):
    def __init__(self, parent=None, status_bar_callback=None):
        super().__init__(parent)
        self.parent_main_window = parent
        self.status_bar_callback = status_bar_callback

        self.setup_ui_elements()
        self.bind_events()

    def setup_ui_elements(self):
        self.PB_LibraryAdd = self.parent_main_window.PB_LibraryAdd
        self.PB_LibraryDelete = self.parent_main_window.PB_LibraryDelete
        self.LW_LibraryIncludeList = self.parent_main_window.LW_LibraryIncludeList
        self.LE_LibrarySelect = self.parent_main_window.LE_LibrarySelect

    def bind_events(self):
        self.PB_LibraryAdd.clicked.connect(self.library_add)
        self.PB_LibraryDelete.clicked.connect(self.library_delete)
        self.LW_LibraryIncludeList.itemClicked.connect(self.library_selected_inlist)

    def library_add(self):
        tmp_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Library Source Code Files",
            "./",
            "C(*.c)"
        )

        if tmp_files:
            overlap_library_num = 0
            for tmp_file in tmp_files:
                tmp_file_name = f"{tmp_file.split('/')[-1]} ({tmp_file})"
                overlap_library = self.LW_LibraryIncludeList.findItems(tmp_file_name, Qt.MatchExactly)

                if overlap_library:
                    overlap_library_num += 1
                else:
                    self.LW_LibraryIncludeList.addItem(tmp_file_name)

            if self.status_bar_callback:
                self.status_bar_callback(f" Added except for {overlap_library_num} duplicate entries.")

    def library_selected_inlist(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()
        if tmp_library_selected and tmp_library_selected.text() != "":
            self.LE_LibrarySelect.setText(tmp_library_selected.text())

    def library_delete(self):
        tmp_library_selected = self.LW_LibraryIncludeList.currentItem()

        if tmp_library_selected is not None:
            if tmp_library_selected.text() == self.LE_LibrarySelect.text():
                self.LW_LibraryIncludeList.takeItem(self.LW_LibraryIncludeList.currentRow())
                self.LE_LibrarySelect.clear()
                if self.status_bar_callback:
                    self.status_bar_callback(f" {tmp_library_selected.text().split(' ')[0]} is deleted.")