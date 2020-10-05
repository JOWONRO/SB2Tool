from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QGroupBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from .macro_key_read import KeyReadDialog


class MacroAddDialog(QDialog):
    """매크로 추가 및 수정 창 클래스"""
    
    def __init__(self, parent, info):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent
        self.info = info

        lbl = QLabel('이름:')
        self.lineEdit = QLineEdit()
        self.lineEdit.setMaxLength(30)
        self.lineEdit.setText('매크로')
        btn = QPushButton('저장')
        btnCR = QPushButton('조건 초기화')
        btnCR.clicked.connect(self.resetCondition)
        btnAR = QPushButton('실행 초기화')
        btnAR.clicked.connect(self.resetAction)

        layer1 = QHBoxLayout()
        layer1.addWidget(lbl)
        layer1.addWidget(self.lineEdit)

        grid = QGridLayout()
        grid.addWidget(btn, 3, 1)
        grid.addLayout(layer1, 0, 0)
        grid.addWidget(self.createConditionGroup(), 1, 0)
        grid.addWidget(btnCR, 1, 1)
        grid.addWidget(self.createActionGroup(), 2, 0)
        grid.addWidget(btnAR, 2, 1)

        self.setLayout(grid)

        if self.info == 'none':  # 매크로 추가 버튼으로 생성됐을 때
            btn.clicked.connect(lambda: self.saveKeys(-1))
            self.setWindowTitle('매크로 추가')
        else:   # 매크로 수정 버튼으로 생성됐을 때
            btn.clicked.connect(lambda: self.saveKeys(self.parent.selectedItem))
            temp = self.info.split('#&@&#')
            self.lineEdit.setText(temp[0])
            if temp[1] != 'none':
                self.btnC1.setText(temp[1])
                self.btnC2.setEnabled(True)
                if temp[2] != 'none':
                    self.btnC2.setText(temp[2])
            if temp[3] != 'none':
                self.btnA1.setText(temp[3])
                self.btnA2.setEnabled(True)
                if temp[4] != 'none':
                    self.btnA2.setText(temp[4])
            self.setWindowTitle('매크로 수정')

        self.setWindowIcon(QIcon('icons/setmacro.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 30, y + 30)
        self.exec()

    def createConditionGroup(self) -> QGroupBox:
        """조건 키 설정 그룹 생성 함수"""
        groupbox = QGroupBox('조건 키')

        lblPlus = QLabel(' + ')
        self.btnC1 = QPushButton('선택 안 함')
        self.btnC1.clicked.connect(lambda: self.keyReadStart(1))
        self.btnC2 = QPushButton('선택 안 함')
        self.btnC2.clicked.connect(lambda: self.keyReadStart(2))
        self.btnC2.setDisabled(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btnC1)
        hbox.addWidget(lblPlus)
        hbox.addWidget(self.btnC2)
        groupbox.setLayout(hbox)

        return groupbox

    def createActionGroup(self) -> QGroupBox:
        """실행 키 설정 그룹 생성 함수"""
        groupbox = QGroupBox('실행 키')

        lblPlus = QLabel(' + ')
        self.btnA1 = QPushButton('선택 안 함')
        self.btnA1.clicked.connect(lambda: self.keyReadStart(3))
        self.btnA2 = QPushButton('선택 안 함')
        self.btnA2.clicked.connect(lambda: self.keyReadStart(4))
        self.btnA2.setDisabled(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btnA1)
        hbox.addWidget(lblPlus)
        hbox.addWidget(self.btnA2)
        groupbox.setLayout(hbox)

        return groupbox

    def keyReadStart(self, i):
        """키 읽어들이기 창 생성 함수"""
        dialog = KeyReadDialog(self, i)

    def resetCondition(self):
        """조건 키 설정 초기화하는 함수"""
        self.btnC1.setText('선택 안 함')
        self.btnC2.setText('선택 안 함')
        self.btnC2.setDisabled(True)

    def resetAction(self):
        """실행 키 설정 초기화하는 함수"""
        self.btnA1.setText('선택 안 함')
        self.btnA2.setText('선택 안 함')
        self.btnA2.setDisabled(True)

    def saveKeys(self, idx):
        """설정한 매크로 저장하고 리스트업하는 함수"""
        self.idx = idx
        btnA1txt = self.btnA1.text()
        if btnA1txt == '선택 안 함':
            btnA1txt = 'none'
        btnA2txt = self.btnA2.text()
        if btnA2txt == '선택 안 함':
            btnA2txt = 'none'
        btnC1txt = self.btnC1.text()
        if btnC1txt == '선택 안 함':
            btnC1txt = 'none'
        btnC2txt = self.btnC2.text()
        if btnC2txt == '선택 안 함':
            btnC2txt = 'none'

        if not self.checkDoubled():
            self.infotxt = self.lineEdit.text() + '#&@&#' + btnC1txt + '#&@&#' + btnC2txt + '#&@&#' + btnA1txt + '#&@&#' + btnA2txt + '#&@&#' + '1'
            if self.idx == -1:
                self.parent.parent.macroList.append(self.infotxt)
            else:
                self.parent.parent.macroList[idx] = self.infotxt
            self.parent.listUp()
            self.close()

    def checkDoubled(self) -> bool:
        """중복 키 체크하는 함수"""
        if self.btnC1.text() != '선택 안 함':
            if self.btnC1.text() == self.btnC2.text():
                self.btnC2.setText('선택 안 함')
                QMessageBox.warning(self, "오류", "동일한 키로 설정할 수 없습니다!")
                return True

        if self.btnA1.text() != '선택 안 함':
            if self.btnA1.text() == self.btnA2.text():
                self.btnA2.setText('선택 안 함')
                QMessageBox.warning(self, "오류", "동일한 키로 설정할 수 없습니다!")
                return True
        return False

