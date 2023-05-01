from pyautogui import position
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLineEdit, QPushButton,
                             QVBoxLayout)


class SymbolAddDialog(QDialog):
    """특수문자 추가 창 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowFlag(Qt.WindowStaysOnTopHint,
                           self.parent.parent.stayOnTop.isChecked())

        lineEdit = QLineEdit()
        lineEdit.setMaxLength(30)
        okbtn = QPushButton('추가')
        okbtn.clicked.connect(lambda: self.addSymbol(lineEdit.text()))
        nobtn = QPushButton('취소')
        nobtn.clicked.connect(self.close)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        hbox.addWidget(okbtn)
        hbox.addWidget(nobtn)
        vbox.addWidget(lineEdit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('특수문자 추가')
        x, y = position()  # 마우스 위치 받기
        self.move(x - 50, y - 50)
        self.setWindowIcon(QIcon('icons/text.png'))
        self.exec()

    def addSymbol(self, txt):
        self.parent.addSymbol(txt)
        self.close()
