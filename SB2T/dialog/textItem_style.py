from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QListWidget,
    QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from SB2T.obj import AttributeOfTextItem
from SB2T.dialog import SetAttributeDialog#, LoadingDialog


class TextItemStyleDialog(QDialog):
    """대사별 포토샵 문자 설정 관리 창 클래스"""

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent
        self.selectedItem = -1

        self.lbl_currentTIS = QLabel('현재 지정된 설정:')
        self.comboBoxForTIS = QComboBox(self)
        
        self.updateComBoxForTIS()
        self.comboBoxForTIS.activated[str].connect(self.setCurrentTextItemStyle)

        self.btn1 = QPushButton('추가(&A)')
        self.btn1.clicked.connect(self.addTIS)
        self.btn1.setEnabled(True)
        self.btn2 = QPushButton('수정(&E)')
        self.btn2.clicked.connect(self.modifyTIS)
        self.btn2.setDisabled(True)
        self.btn3 = QPushButton('복사(&C)')
        self.btn3.clicked.connect(self.copyTIS)
        self.btn3.setDisabled(True)
        self.btn4 = QPushButton('삭제(&D)')
        self.btn4.clicked.connect(self.deleteTIS)
        self.btn4.setDisabled(True)

        self.btn5 = QPushButton('OK')
        self.btn5.clicked.connect(self.close)

        self.listwidget = QListWidget()
        self.listwidget.clicked.connect(self.clickedList)
        self.listwidget.doubleClicked.connect(self.modifyTIS)
        self.listUp()

        layer1 = QVBoxLayout()
        layer1.addWidget(self.btn1)
        layer1.addWidget(self.btn2)
        layer1.addWidget(self.btn3)
        layer1.addWidget(self.btn4)
        layer1.addStretch(3)
        layer1.addWidget(self.btn5)

        layer2 = QHBoxLayout()
        layer2.addWidget(self.lbl_currentTIS)
        layer2.addWidget(self.comboBoxForTIS)

        grid = QGridLayout()
        grid.addLayout(layer2, 0, 0)
        grid.addWidget(self.listwidget, 1, 0)
        grid.addLayout(layer1, 1, 1)

        self.setLayout(grid)
        self.setWindowTitle('포토샵 전용 문자 설정')
        self.setWindowIcon(QIcon("icons/setpsmode.png"))
        x, y = self.parent.pos().x(), self.parent.pos().y()
        self.move(x + 30, y + 100)
        self.exec()

    def updateComBoxForTIS(self):
        """현재 지정된 설정을 업데이트하는 함수"""
        currentTIS = self.parent.currentTextItemStyle
        self.comboBoxForTIS.clear()
        for i in self.parent.textItemStyleList:
            self.comboBoxForTIS.addItem(i.name)
        self.comboBoxForTIS.addItem('지정 안 함')
        self.comboBoxForTIS.setCurrentText('지정 안 함')
        self.parent.currentTextItemStyle = None

        if currentTIS != None:
            for i in self.parent.textItemStyleList:  # 설정 삭제 시 체크
                if i.name == currentTIS.name:
                    self.comboBoxForTIS.setCurrentText(i.name)
                    self.parent.currentTextItemStyle = i
                    break

    def setCurrentTextItemStyle(self, name):
        """특정 문자 설정을 지정하는 함수"""
        if name == '지정 안 함':
            self.parent.currentTextItemStyle = None
        else:
            for i in self.parent.textItemStyleList:
                if i.name == name:
                    self.parent.currentTextItemStyle = i
                    break

    def listUp(self):
        """문자 설정 리스트 불러들이는 함수"""
        self.listwidget.clear()
        for i in range(len(self.parent.textItemStyleList)):
            self.listwidget.insertItem(i, self.parent.textItemStyleList[i].name)

    def addTIS(self):
        """문자 설정 추가 창 생성하는 함수"""
        # if len(self.font_list) == 0:
        #     self.load_dialog = LoadingDialog(self, '폰트 목록을 불러오는 중입니다...', 'icons/setpsmode.png')
        dialog = SetAttributeDialog(self, 'none')
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.btn4.setDisabled(True)

    def modifyTIS(self):
        """문자 설정 수정 창 생성하는 함수"""
        # if len(self.font_list) == 0:
        #     self.load_dialog = LoadingDialog(self, '폰트 목록을 불러오는 중입니다...', 'icons/setpsmode.png')
        dialog = SetAttributeDialog(self, self.selectedItem)
        self.listwidget.setCurrentItem(self.listwidget.item(self.selectedItem))
        self.clickedList()

    def copyTIS(self):
        """선택한 문자 설정을 복사하는 함수"""
        temp = self.parent.textItemStyleList
        num = self.selectedItem
        copy = AttributeOfTextItem()
        copy.name = temp[num].name + ' - 복사'
        copy.attributes['conversation'] = temp[num].attributes['conversation'].copy()
        copy.attributes['think'] = temp[num].attributes['think'].copy()
        copy.attributes['narration'] = temp[num].attributes['narration'].copy()
        copy.attributes['emphasis'] = temp[num].attributes['emphasis'].copy()
        copy.attributes['effect'] = temp[num].attributes['effect'].copy()
        copy.attributes['background'] = temp[num].attributes['background'].copy()
        temp = temp[0:num + 1] + [copy] + temp[num + 1:]
        self.parent.textItemStyleList = temp
        self.listUp()
        self.updateComBoxForTIS()
        self.listwidget.setCurrentItem(self.listwidget.item(self.selectedItem))
        self.clickedList()

    def deleteTIS(self):
        """선택한 문자 설정을 삭제하는 함수"""
        del self.parent.textItemStyleList[self.selectedItem]
        self.selectedItem = -1
        self.listUp()
        self.updateComBoxForTIS()
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
        self.btn4.setDisabled(True)

    def clickedList(self):
        """선택된 설정 인덱스를 저장하고 버튼을 활성화하는 함수"""
        self.selectedItem = self.listwidget.currentRow()
        self.btn2.setEnabled(True)
        self.btn3.setEnabled(True)
        self.btn4.setEnabled(True)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            if self.selectedItem != -1:
                self.deleteTIS()

