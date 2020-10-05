from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QGridLayout,
    QLineEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class TextFindDialog(QDialog):
    """특정 텍스트 찾기 창 클래스"""
    
    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        self.index = 0
        self.findlist = []
        self.listlen = 0
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 50, y + 150)

        self.textedit = QLineEdit()
        self.btn2 = QPushButton('다음(&B)')
        self.btn2.clicked.connect(self.afterResult)
        self.btn2.setDisabled(True)
        self.btn1 = QPushButton('이전(&V)')
        self.btn1.clicked.connect(self.beforeResult)
        self.btn1.setDisabled(True)
        self.resultlbl = QLabel()
        self.resultlbl.setText('검색 결과: 0 / 0 줄')

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.textedit, 0, 0)
        self.grid.addWidget(self.btn2, 0, 4)
        self.grid.addWidget(self.btn1, 0, 3)
        self.grid.addWidget(self.resultlbl, 1, 0)

        self.setWindowTitle('텍스트 찾기')
        self.setWindowIcon(QIcon("icons/find.png"))
        self.show()  # 이게 있어야 찾기 창 띄워 놓고 딴 짓 가능

        self.textedit.textChanged.connect(self.findit)

    def findit(self, txt):
        """input이 변할 때마다 해당 텍스트 검색하는 함수"""
        self.index = 0
        self.listlen = 0
        self.findlist.clear()
        self.btn1.setDisabled(True)
        self.btn2.setDisabled(True)
        self.resultlbl.setText('검색 결과: 0 / 0 줄')
        if txt != '':
            for i in range(len(self.parent.btn)):
                if self.parent.btn[i].mode:   # 일단 주석은 제외
                    if txt in self.parent.btn[i].text():
                        self.findlist.append(i)
            self.listlen = len(self.findlist)
            if self.listlen > 0:
                self.resultlbl.setText('검색 결과: 1 / ' + str(self.listlen) + ' 줄')
                self.parent.btn[self.findlist[0]].copyText()
                self.btn1.setEnabled(True)
                self.btn2.setEnabled(True)

    def afterResult(self):
        """다음 검색 결과로 넘어가는 함수"""
        self.index = (self.index + 1) % self.listlen
        self.resultlbl.setText(
            '검색 결과: ' + str(self.index + 1) + ' / ' + str(self.listlen) + ' 줄')
        self.parent.btn[self.findlist[self.index]].copyText()

    def beforeResult(self):
        """이전 검색 결과로 넘어가는 함수"""
        if self.index == 0:
            self.index = self.listlen - 1
        else:
            self.index -= 1
        self.resultlbl.setText(
            '검색 결과: ' + str(self.index + 1) + ' / ' + str(self.listlen) + ' 줄')
        self.parent.btn[self.findlist[self.index]].copyText()

