from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QDialog, QGridLayout, QLabel, QListWidget,
                             QPushButton, QVBoxLayout)

from .symbol_add import SymbolAddDialog
from .symbol_edit import SymbolEditDialog


class SymbolSetDialog(QDialog):
    """특수문자 설정 창 클래스"""

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        self.selectedItem = -1

        self.btn1 = QPushButton('추가(&A)')
        self.btn1.clicked.connect(self.showAddSymbolDialog)
        self.btn1.setEnabled(True)
        self.btn2 = QPushButton('수정(&E)')
        self.btn2.clicked.connect(self.showModifySymbolDialog)
        self.btn2.setDisabled(True)
        self.btn3 = QPushButton('삭제(&D)')
        self.btn3.clicked.connect(self.deleteSymbol)
        self.btn3.setDisabled(True)
        self.btn4 = QPushButton('올리기(&U)')
        self.btn4.clicked.connect(self.moveUp)
        self.btn4.setDisabled(True)
        self.btn5 = QPushButton('내리기(&D)')
        self.btn5.clicked.connect(self.moveDown)
        self.btn5.setDisabled(True)

        self.btn6 = QPushButton('OK')
        self.btn6.clicked.connect(self.close)

        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.clickedList)
        self.listwidget.doubleClicked.connect(self.showModifySymbolDialog)
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

        self.setLayout(grid)

        self.setWindowTitle('특수문자 설정')
        self.setWindowIcon(QIcon('icons/text.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 30, y + 120)
        self.exec()

    def listUp(self):
        """특수문자 리스트 불러들이는 함수"""
        self.listwidget.clear()
        for i, symbol in enumerate(self.parent.symbolList):
            self.listwidget.insertItem(i, symbol)

    def autoScroll(self, n):
        """업데이트 이후 기존 또는 새로 선택된 텍스트로 자동 스크롤하는 함수"""
        QTimer.singleShot(  # 시간을 늘릴수록 잘 작동할 확률은 높은듯?
            10, lambda: self.listwidget.scrollToItem(
                self.listwidget.item(n)
            )
        )

    def showAddSymbolDialog(self):
        """특수문자 추가 창 생성하는 함수"""
        addDialog = SymbolAddDialog(self)

    def addSymbol(self, txt):
        """받은 특수문자를 추가하는 함수"""
        self.parent.symbolList.append(txt)
        self.listUp()
        addedItemIdx = len(self.parent.symbolList) - 1
        self.listwidget.setCurrentItem(
            self.listwidget.item(addedItemIdx))
        self.autoScroll(addedItemIdx)
        self.clickedList()

    def showModifySymbolDialog(self):
        """특수문자 수정 창 생성하는 함수"""
        modifyDialog = SymbolEditDialog(
            self, self.parent.symbolList[self.selectedItem])

    def editSymbol(self, txt):
        """받은 특수문자로 수정하는 함수"""
        self.parent.symbolList[self.selectedItem] = txt
        self.listUp()
        self.listwidget.setCurrentItem(self.listwidget.item(self.selectedItem))
        self.autoScroll(self.selectedItem)

    def deleteSymbol(self):
        """특수문자 삭제하는 함수"""
        del self.parent.symbolList[self.selectedItem]
        self.selectedItem = -1
        self.listUp()
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.btn4.setDisabled(True)
        self.btn5.setDisabled(True)

    def moveUp(self):
        """선택된 항목을 위로 한 칸 올리는 함수"""
        if self.selectedItem == 0:
            return
        idx = self.selectedItem
        currentItem = self.parent.symbolList[idx]
        prevItem = self.parent.symbolList[idx - 1]
        self.parent.symbolList[idx - 1] = currentItem
        self.parent.symbolList[idx] = prevItem
        self.listUp()
        self.listwidget.setCurrentItem(
            self.listwidget.item(idx - 1))
        self.autoScroll(idx - 1)
        self.clickedList()

    def moveDown(self):
        """선택된 항목을 위로 한 칸 내리는 함수"""
        if self.selectedItem == len(self.parent.symbolList) - 1:
            return
        idx = self.selectedItem
        currentItem = self.parent.symbolList[idx]
        nextItem = self.parent.symbolList[idx + 1]
        self.parent.symbolList[idx + 1] = currentItem
        self.parent.symbolList[idx] = nextItem
        self.listUp()
        self.listwidget.setCurrentItem(
            self.listwidget.item(idx + 1))
        self.autoScroll(idx + 1)
        self.clickedList()

    def clickedList(self):
        """항목 클릭 시 해당 항목 선택"""
        self.selectedItem = self.listwidget.currentRow()
        self.btn2.setEnabled(True)
        self.btn3.setEnabled(True)
        self.btn4.setEnabled(True)
        self.btn5.setEnabled(True)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            if self.selectedItem != -1:
                self.deleteSymbol()
