from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from pyautogui import position


class TextEditDialog(QDialog):
    """텍스트 라인의 텍스트 수정 창 생성 함수"""

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        lineEdit = QLineEdit()
        lineEdit.setText(self.parent.txt)
        okbtn = QPushButton()
        okbtn.setText('수정')
        okbtn.clicked.connect(lambda: self.editText(lineEdit.text()))
        nobtn = QPushButton()
        nobtn.setText('취소')
        nobtn.clicked.connect(self.close)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        hbox.addWidget(okbtn)
        hbox.addWidget(nobtn)
        vbox.addWidget(lineEdit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('텍스트 수정')
        self.setWindowIcon(QIcon('icons/text.png'))
        x, y = position()  # 창 위치 조정
        self.move(x - 50, y - 50)
        self.exec()

    def editText(self, txt):
        """텍스트 수정 사항 반영"""
        if self.parent.txt != txt:
            self.parent.txt = txt
            self.parent.setLine()
            self.parent.parent.recordChange()
        self.close()

