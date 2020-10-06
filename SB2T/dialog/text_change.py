from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QGridLayout,
    QLineEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class TextChangeDialog(QDialog):
    """텍스트 바꾸기 창 클래스"""
    
    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        self.index = 0
        self.findlist = []
        self.listlen = 0
        x, y = self.parent.pos().x(), self.parent.pos().y()
        self.move(x + 50, y + 150)

        self.textedit1 = QLineEdit()
        self.lbl1 = QLabel('찾는 내용')
        self.textedit2 = QLineEdit()
        self.lbl2 = QLabel('바꿀 내용')
        self.btn1 = QPushButton('모두 바꾸기(&A)')
        self.btn1.clicked.connect(self.allTextChange)
        self.btn1.setDisabled(True)
        self.btn2 = QPushButton('다음(&B)')
        self.btn2.clicked.connect(self.afterResult)
        self.btn2.setDisabled(True)
        self.btn3 = QPushButton('바꾸기(&C)')
        self.btn3.clicked.connect(self.textChange)
        self.btn3.setDisabled(True)
        self.resultlbl = QLabel()
        self.resultlbl.setText('검색 결과: 0 / 0 줄')

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.lbl1, 0, 0)
        self.grid.addWidget(self.textedit1, 0, 1)
        self.grid.addWidget(self.lbl2, 1, 0)
        self.grid.addWidget(self.textedit2, 1, 1)
        self.grid.addWidget(self.resultlbl, 2, 1)
        self.grid.addWidget(self.btn1, 2, 3)
        self.grid.addWidget(self.btn2, 0, 3)
        self.grid.addWidget(self.btn3, 1, 3)

        self.setWindowTitle('텍스트 바꾸기')
        self.setWindowIcon(QIcon('icons/change.png'))
        self.show()  # 이게 있어야 찾기 창 띄워 놓고 딴 짓 가능

        self.textedit1.textChanged.connect(self.findit)

    def findit(self, txt):
        """input이 변할 때마다 해당 텍스트 검색하는 함수"""
        self.index = 0
        self.listlen = 0
        self.findlist.clear()
        self.btn1.setDisabled(True)
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.resultlbl.setText('검색 결과: 0 / 0 줄')
        if txt != '':
            for i in range(len(self.parent.btn)):
                if self.parent.btn[i].mode:  # 일단 주석은 제외
                    if txt in self.parent.btn[i].text():
                        self.findlist.append(i)
            self.listlen = len(self.findlist)
            if self.listlen > 0:
                self.resultlbl.setText(
                    '검색 결과: ' + str(self.index + 1) + ' / ' + str(self.listlen) + ' 줄')
                self.parent.btn[self.findlist[0]].copyText()
                self.btn1.setEnabled(True)
                self.btn2.setEnabled(True)
                self.btn3.setEnabled(True)

    def textChange(self):
        """일치하는 텍스트 바꾸는 함수"""
        temp1 = self.textedit1.text()
        temp2 = self.textedit2.text()
        i = self.findlist[self.index]

        self.parent.btn[i].setText(self.parent.btn[i].text().replace(temp1, temp2))
        # self.parent.btn[i].setText(self.parent.btn[i].text().replace(temp1, temp2, 1))
        self.findlist.remove(i)
        self.listlen = len(self.findlist)
        self.parent.recordChange()

        if self.listlen != 0:
            if self.index == self.listlen:
                self.index = 0
            self.resultlbl.setText(
                '검색 결과: ' + str(self.index + 1) + ' / ' + str(self.listlen) + ' 줄')
            self.parent.btn[self.findlist[self.index]].copyText()
        else:
            self.index = 0
            self.listlen = 0
            self.findlist.clear()
            self.btn1.setDisabled(True)
            self.btn2.setDisabled(True)
            self.btn3.setDisabled(True)
            self.resultlbl.setText('검색 결과: 0 / 0 줄')

    def allTextChange(self):
        """일치하는 모든 텍스트 바꾸는 함수"""
        temp1 = self.textedit1.text()
        temp2 = self.textedit2.text()

        for i in self.findlist:
            self.parent.btn[i].setText(
                self.parent.btn[i].text().replace(temp1, temp2))
        self.findit(temp1)
        self.parent.recordChange()

    def afterResult(self):
        """다음 검색 결과로 넘어가는 함수"""
        self.index = (self.index + 1) % self.listlen
        self.resultlbl.setText(
            '검색 결과: ' + str(self.index + 1) + ' / ' + str(self.listlen) + ' 줄')
        self.parent.btn[self.findlist[self.index]].copyText()

