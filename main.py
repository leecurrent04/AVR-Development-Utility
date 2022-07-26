import sys, os, os.path
# from typing import Set

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

# UI파일 연결
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # base_path : py code directory
    return os.path.join(base_path, "resource/", relative_path)

form_class = uic.loadUiType(resource_path('util.ui'))[0]

avrCode = ""
workDirectory = ""

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Preset
        # Button's Icon
        self.PushB_Directory.setIcon(QIcon('resource/img/document-open-symbolic.svg'))
        self.PushB_PortReload.setIcon(QIcon('resource/img/view-refresh-symbolic.svg'))

        # load Avr_Tree data
        self.avr_Tree_DataLoad()

        # Status Bar
        self.statusBar().showMessage('Set Working Directory')

        # load programmers
        with open("resource/programmers.txt",'r') as f:
            lines = f.readlines()
            for line in lines:
                self.Avr_Programmer.addItem(line[:-1].split(",")[1])

        # load Port data (ex /dev/ttyUSB0)
        self.portLoad()

        # Event
        # When other device selected
        self.Avr_Tree.currentItemChanged.connect(self.avr_Tree_changed)

        # When PushB_Directory clicked
        self.PushB_Directory.clicked.connect(self.pushB_Directory_clicked)

        # When Avr_search changed
        self.Avr_search.textChanged.connect(self.avr_search_changed)

        # When PushB_PortReload clicked
        self.PushB_PortReload.clicked.connect(self.portLoad)

        # When PushB_make clicked -> make Makefile
        self.PushB_make.clicked.connect(self.makeMfile)


    def avr_Tree_DataLoad(self):
        self.Avr_Tree.setAlternatingRowColors(True)

        with open("./resource/avr_list.txt", 'r') as file:
            lines = file.readlines()
            buffer = ""

            for line in lines:
                # Don't make same headers
                if buffer != line.split(",")[0]:
                    itemTop = QTreeWidgetItem(self.Avr_Tree)
                    itemTop.setText(0, line.split(",")[0])
                    buffer = line.split(",")[0]

                # Make sub Items
                subItem = QTreeWidgetItem()
                subItem.setText(0, line.split(",")[1])
                subItem.setText(1, line.split(",")[2][:-1])     # delete \n
                itemTop.addChild(subItem)

    def avr_Tree_changed(self):
        if self.Avr_Tree.currentItem().text(1) != "":
            self.Avr_SelAvr.setText(self.Avr_Tree.currentItem().text(0))
            avrCode = self.Avr_Tree.currentItem().text(1)

    def pushB_Directory_clicked(self):
        tmp = ""
        tmp = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Working Directory"),
            "../",
            QFileDialog.ShowDirsOnly
        )
        if tmp != "":
            workDirectory = tmp
            self.statusBar().showMessage(workDirectory)
            self.label_Directory.setText(workDirectory.split("/")[-1])

    def avr_search_changed(self):
        print(self.Avr_search.text())

    def portLoad(self):
        self.Avr_Port.clear()

        # load Port
        for i in os.listdir('/dev'):
            if i[0:6] == "ttyUSB" or i[0:6] == "ttyACM":
                self.Avr_Port.addItem("/dev/" + i)

    def makeMfile(self):
        print("Hey!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
