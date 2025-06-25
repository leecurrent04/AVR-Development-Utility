import os
from PyQt5.QtWidgets import QWidget

class PreviewTab(QWidget):
    def __init__(self, parent=None, status_bar_callback=None, get_device_code_callback=None, get_library_list_callback=None, get_tool_list_callback=None, get_work_directory_callback=None):
        super().__init__(parent)
        self.parent_main_window = parent
        self.status_bar_callback = status_bar_callback
        self.get_device_code = get_device_code_callback
        self.get_library_list = get_library_list_callback
        self.get_tool_list = get_tool_list_callback
        self.get_work_directory = get_work_directory_callback

        self.setup_ui_elements()
        self.bind_events()

    def setup_ui_elements(self):
        self.PB_PreviewLoadConfigure = self.parent_main_window.PB_PreviewLoadConfigure
        self.PB_PreviewMakeFile = self.parent_main_window.PB_PreviewMakeFile
        self.TE_Preview = self.parent_main_window.TE_Preview

    def bind_events(self):
        self.PB_PreviewLoadConfigure.clicked.connect(self.makefile_data_load)
        self.PB_PreviewMakeFile.clicked.connect(self.make_makefile)

    def makefile_data_load(self):
        make_libraries = ""
        make_tool = ""
        tmp_file_data = ""

        # Get data from other tabs via callbacks
        avr_code = self.get_device_code()
        library_items = self.get_library_list()
        tool_items = self.get_tool_list()
        work_directory = self.get_work_directory()

        # Load libraries
        for n, item in enumerate(library_items):
            line, _ = item.text().split('(')[1].split(')')
            if n + 1 == len(library_items):
                make_libraries += f"{line}"
            else:
                make_libraries += f"{line} \\\n\t"

        # Load tool
        for n, item in enumerate(tool_items):
            _, tmp_tool, tmp_port, tmp_baudrate = item.text().split(',')

            if avr_code == "None" or not avr_code:
                make_tool += "# [Warning] Check Device again.\n"

            if not tmp_port:
                make_tool += "# [Warning] Check Port again.\n"
            else:
                tmp_port = f"-P {tmp_port} "

            if not tmp_baudrate:
                make_tool += "# [Warning] Check Baudrate again.\n"
            else:
                tmp_baudrate = f"-b {tmp_baudrate} "

            make_tool += f"upload{n}:\n\tavrdude -v -p {avr_code} -c {tmp_tool} {tmp_port}{tmp_baudrate}-U flash:w:./.out/main.hex:i\n\n\n"

        if avr_code == "None" or not avr_code:
            tmp_file_data = "# [Warning] Check Device again.\n"

        try:
            with open("./resource/data/Makefile", 'r') as tmp_resource:
                tmp_file_data += tmp_resource.read() % (make_libraries, avr_code, avr_code, make_tool)
        except FileNotFoundError:
            tmp_file_data += "# Error: Makefile template not found.\n"
            if self.status_bar_callback:
                self.status_bar_callback("Error: Makefile template not found.")

        self.TE_Preview.setText(tmp_file_data)
        if self.status_bar_callback:
            self.status_bar_callback("Makefile preview loaded.")

    def make_makefile(self):
        work_directory = self.get_work_directory()
        if work_directory != "":
            if os.path.isdir(work_directory):
                with open(f"{work_directory}/Makefile", 'w') as fp:
                    fp.write(self.TE_Preview.toPlainText())
                if self.status_bar_callback:
                    self.status_bar_callback("Makefile is generated.")
            else:
                if self.status_bar_callback:
                    self.status_bar_callback("Work Directory does not exist")
        else:
            if self.status_bar_callback:
                self.status_bar_callback("You must define Work Directory")