from pyautogui import position
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLineEdit, QPushButton,
                             QVBoxLayout)


class SymbolEditDialog(QDialog):
    """특수문자 수정 창 클래스"""

    def __init__(self, parent, txt):
        super().__init__()
        self.parent = parent
        self.setWindowFlag(Qt.WindowStaysOnTopHint,
                           self.parent.parent.stayOnTop.isChecked())
        self.txt = txt

        lineEdit = QLineEdit()
        lineEdit.setMaxLength(30)
        lineEdit.setText(txt)
        okbtn = QPushButton('수정')
        okbtn.clicked.connect(lambda: self.editSymbol(lineEdit.text()))
        nobtn = QPushButton('취소')
        nobtn.clicked.connect(self.close)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        hbox.addWidget(okbtn)
        hbox.addWidget(nobtn)
        vbox.addWidget(lineEdit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('특수문자 수정')
        x, y = position()  # 마우스 위치 받기
        self.move(x - 50, y - 50)
        self.setWindowIcon(QIcon('icons/text.png'))
        self.exec()

    def editSymbol(self, e_txt):
        """특수문자 수정 사항 반영"""
        if self.txt != e_txt:
            self.parent.editSymbol(e_txt)
        self.close()
