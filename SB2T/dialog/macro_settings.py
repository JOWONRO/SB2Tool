from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QListWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from SB2T.dialog import MacroAddDialog


class MacroSetDialog(QDialog):
    """매크로 설정 창 클래스"""

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        self.selectedItem = -1

        self.lblinfo = QLabel('')
        self.btn1 = QPushButton('추가(&A)')
        self.btn1.clicked.connect(self.addMacro)
        self.btn1.setEnabled(True)
        self.btn2 = QPushButton('수정(&E)')
        self.btn2.clicked.connect(self.modifyMacro)
        self.btn2.setDisabled(True)
        self.btn3 = QPushButton('삭제(&D)')
        self.btn3.clicked.connect(self.deleteMacro)
        self.btn3.setDisabled(True)
        self.btn4 = QPushButton('활성화(&V)')
        self.btn4.clicked.connect(lambda: self.activate(True))
        self.btn4.setDisabled(True)
        self.btn5 = QPushButton('비활성화(&B)')
        self.btn5.clicked.connect(lambda: self.activate(False))
        self.btn5.setDisabled(True)

        self.btn6 = QPushButton('OK')
        self.btn6.clicked.connect(self.close)

        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.clickedList)
        self.listwidget.doubleClicked.connect(self.modifyMacro)
        self.listUp()

        layer = QVBoxLayout()
        layer.addWidget(self.btn1)
        layer.addWidget(self.btn2)
        layer.addWidget(self.btn3)
        layer.addWidget(self.btn4)
        layer.addWidget(self.btn5)
        layer.addStretch(2)

        grid = QGridLayout()
        grid.addWidget(self.btn6, 1, 1)
        grid.addWidget(self.listwidget, 0, 0)
        grid.addLayout(layer, 0, 1)
        grid.addWidget(self.lblinfo, 1, 0)

        self.setLayout(grid)

        self.setWindowTitle('키보드 매크로 설정')
        self.setWindowIcon(QIcon('icons/setmacro.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 30, y + 120)
        self.exec()

    def listUp(self):
        """매크로 리스트 불러들이는 함수"""
        self.listwidget.clear()
        for i in range(len(self.parent.macroList)):
            temp = self.parent.macroList[i].split('#&@&#')
            self.listwidget.insertItem(i, temp[0])
            if temp[5] == '0':  # 활성화된 건 검정, 비활성화된 건 회색으로 표시
                item = self.listwidget.item(i).setForeground(Qt.gray)
            else:
                item = self.listwidget.item(i).setForeground(Qt.black)
        self.lblinfo.setText('')

    def addMacro(self):
        """매크로 추가 창 생성하는 함수"""
        addDialog = MacroAddDialog(self, 'none')
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.btn4.setDisabled(True)
        self.btn5.setDisabled(True)

    def modifyMacro(self):
        """매크로 수정 창 생성하는 함수"""
        modifyDialog = MacroAddDialog(self, self.parent.macroList[self.selectedItem])
        self.listwidget.setCurrentItem(self.listwidget.item(self.selectedItem))
        self.clickedList()

    def deleteMacro(self):
        """매크로 삭제하는 함수"""
        del self.parent.macroList[self.selectedItem]
        self.selectedItem = -1
        self.listUp()
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.btn4.setDisabled(True)
        self.btn5.setDisabled(True)

    def activate(self, boolean):
        """매크로 활성화 여부 함수"""
        temp = self.parent.macroList[self.selectedItem].split('#&@&#')
        if boolean:
            txt = temp[0] + '#&@&#' + temp[1] + '#&@&#' + temp[2] + '#&@&#' + temp[3] + '#&@&#' + temp[4] + '#&@&#' + '1'
        else:
            txt = temp[0] + '#&@&#' + temp[1] + '#&@&#' + temp[2] + '#&@&#' + temp[3] + '#&@&#' + temp[4] + '#&@&#' + '0'
        self.parent.macroList[self.selectedItem] = txt
        self.listUp()
        self.listwidget.setCurrentItem(self.listwidget.item(self.selectedItem))
        self.clickedList()

    def clickedList(self):
        """매크로 항목 클릭 시 해당 매크로 선택 및 상세 내용 표시"""
        self.selectedItem = self.listwidget.currentRow()
        temp = self.parent.macroList[self.selectedItem].split('#&@&#')
        if temp[1] == 'none':
            c = '선택 안 함'
        elif temp[2] != 'none':
            c = temp[1] + ' + ' + temp[2]
        else:
            c = temp[1]
        if temp[3] == 'none':
            a = '선택 안 함'
        elif temp[4] != 'none':
            a = temp[3] + ' + ' + temp[4]
        else:
            a = temp[3]
        if temp[5] == '1':
            act = '활성화'
        else:
            act = '비활성화'
        self.btn2.setEnabled(True)
        self.btn3.setEnabled(True)
        self.btn4.setEnabled(True)
        self.btn5.setEnabled(True)
        self.lblinfo.setText('(' + act + ') 조건: ' + c + ' / 액션: ' + a)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            if self.selectedItem != -1:
                self.deleteMacro()

