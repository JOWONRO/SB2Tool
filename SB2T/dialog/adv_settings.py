from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QCheckBox,
    QGroupBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class AdvSettingsDialog(QDialog):
    """
    고급 설정창 클래스\n
    복사 기능, 붙여넣기 기능, UI 기능 조정 가능
    """

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        btn = QPushButton('OK')
        btn.clicked.connect(self.close)
        layer = QHBoxLayout()
        layer.addStretch(2)
        layer.addWidget(btn)

        grid = QGridLayout()
        grid.addWidget(self.createExceptCopyGroup(), 0, 0)
        grid.addWidget(self.createPasteGroup(), 1, 0)
        grid.addWidget(self.createUIGroup(), 2, 0)
        grid.addLayout(layer, 3, 0)

        self.setLayout(grid)

        self.setWindowTitle('고급 설정')
        self.setWindowIcon(QIcon("icons/advset.png"))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 50, y + 70)
        self.exec()

    def createExceptCopyGroup(self) -> QGroupBox:
        """복사 기능 그룹 생성 함수"""
        groupbox = QGroupBox('복사 기능')

        self.copycheckbox1 = QCheckBox('문장 양 끝 소괄호 제외')
        self.copycheckbox1.setChecked(self.parent.exceptbrackets)
        self.copycheckbox1.stateChanged.connect(self.setExceptBrackets)
        self.copycheckbox2 = QCheckBox('문장 양 끝 중괄호 제외')
        self.copycheckbox2.setChecked(self.parent.exceptCurlybrackets)
        self.copycheckbox2.stateChanged.connect(self.setExceptCurlyBrackets)
        self.copycheckbox3 = QCheckBox('문장 양 끝 대괄호 제외')
        self.copycheckbox3.setChecked(self.parent.exceptSquarebrackets)
        self.copycheckbox3.stateChanged.connect(self.setExceptSquareBrackets)
        self.copycheckbox4 = QCheckBox('문장 양 끝 큰 따옴표 제외')
        self.copycheckbox4.setChecked(self.parent.exceptDQuotaion)
        self.copycheckbox4.stateChanged.connect(self.setExceptDQuotation)
        self.copycheckbox5 = QCheckBox('문장 양 끝 작은 따옴표 제외')
        self.copycheckbox5.setChecked(self.parent.exceptSQuotaion)
        self.copycheckbox5.stateChanged.connect(self.setExceptSQuotation)

        vbox = QVBoxLayout()
        vbox.addWidget(self.copycheckbox1)
        vbox.addWidget(self.copycheckbox2)
        vbox.addWidget(self.copycheckbox3)
        vbox.addWidget(self.copycheckbox4)
        vbox.addWidget(self.copycheckbox5)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox

    def createPasteGroup(self) -> QGroupBox:
        """붙여넣기 기능 그룹 생성 함수"""
        groupbox = QGroupBox('붙여넣기 기능')

        self.pastecheckbox1 = QCheckBox('붙여넣기 후 자동으로 레이어 닫기 (포토샵 한정)')
        self.pastecheckbox1.setChecked(self.parent.pasteCtrlEnter)
        self.pastecheckbox1.stateChanged.connect(self.setpasteCtrlEnter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.pastecheckbox1)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox

    def createUIGroup(self) -> QGroupBox:
        """UI 설정 그룹 생성 함수"""
        groupbox = QGroupBox('UI 설정')

        self.subtitle1 = QLabel('툴바: ')
        self.uicheckbox1 = QCheckBox('툴바 표시')
        self.uicheckbox1.setChecked(self.parent.toolbar.isVisible())
        self.uicheckbox1.stateChanged.connect(self.parent.setToolbarVisible)

        self.space = QLabel('   ')
        self.subtitle2 = QLabel('주석: ')
        self.uicheckbox2 = QCheckBox("문장 맨 앞에 '숫자'가 오면 주석 처리")
        self.uicheckbox2.setChecked(self.parent.commentWithNumber)
        self.uicheckbox2.stateChanged.connect(self.setCommentWithNumber)
        self.uicheckbox3 = QCheckBox("문장 맨 앞에 'P' 또는 'p'가 오면 주석 처리")
        self.uicheckbox3.setChecked(self.parent.commentWithP)
        self.uicheckbox3.stateChanged.connect(self.setCommentWithP)

        self.subtitle3 = QLabel('기타: ')
        self.uicheckbox4 = QCheckBox("실행 시 창을 항상 위에 고정 (다음 실행 때 반영)")
        self.uicheckbox4.setChecked(self.parent.onTopDefault)
        self.uicheckbox4.stateChanged.connect(self.setOnTopDefault)

        vbox = QVBoxLayout()
        vbox.addWidget(self.subtitle1)
        vbox.addWidget(self.uicheckbox1)
        vbox.addStretch(1)
        vbox.addWidget(self.space)
        vbox.addWidget(self.subtitle2)
        vbox.addWidget(self.uicheckbox2)
        vbox.addWidget(self.uicheckbox3)
        vbox.addStretch(1)
        vbox.addWidget(self.space)
        vbox.addWidget(self.subtitle3)
        vbox.addWidget(self.uicheckbox4)
        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox

    def setExceptBrackets(self):
        """소괄호 제외 복사 기능 활성화 여부 함수"""
        if self.copycheckbox1.isChecked():
            self.parent.exceptbrackets = 1
        else:
            self.parent.exceptbrackets = 0
        self.parent.advSettingsList[0] = self.parent.exceptbrackets

    def setExceptCurlyBrackets(self):
        """중괄호 제외 복사 기능 활성화 여부 함수"""
        if self.copycheckbox2.isChecked():
            self.parent.exceptCurlybrackets = 1
        else:
            self.parent.exceptCurlybrackets = 0
        self.parent.advSettingsList[1] = self.parent.exceptCurlybrackets

    def setExceptSquareBrackets(self):
        """대괄호 제외 복사 기능 활성화 여부 함수"""
        if self.copycheckbox3.isChecked():
            self.parent.exceptSquarebrackets = 1
        else:
            self.parent.exceptSquarebrackets = 0
        self.parent.advSettingsList[2] = self.parent.exceptSquarebrackets

    def setExceptDQuotation(self):
        """큰 따옴표 제외 복사 기능 활성화 여부 함수"""
        if self.copycheckbox4.isChecked():
            self.parent.exceptDQuotaion = 1
        else:
            self.parent.exceptDQuotaion = 0
        self.parent.advSettingsList[3] = self.parent.exceptDQuotaion

    def setExceptSQuotation(self):
        """작은 따옴표 제외 복사 기능 활성화 여부 함수"""
        if self.copycheckbox5.isChecked():
            self.parent.exceptSQuotaion = 1
        else:
            self.parent.exceptSQuotaion = 0
        self.parent.advSettingsList[4] = self.parent.exceptSQuotaion

    def setpasteCtrlEnter(self):
        """붙여넣기 후 레이어 닫기 기능 활성화 여부 함수"""
        if self.pastecheckbox1.isChecked():
            self.parent.pasteCtrlEnter = 1
        else:
            self.parent.pasteCtrlEnter = 0
        self.parent.advSettingsList[5] = self.parent.pasteCtrlEnter

    def setCommentWithNumber(self):
        """숫자 주석 처리 기능 활성화 여부 함수"""
        if self.uicheckbox2.isChecked():
            self.parent.commentWithNumber = 1
        else:
            self.parent.commentWithNumber = 0
        self.parent.advSettingsList[6] = self.parent.commentWithNumber

    def setCommentWithP(self):
        """P, p 주석 처리 기능 활성화 여부 함수"""
        if self.uicheckbox3.isChecked():
            self.parent.commentWithP = 1
        else:
            self.parent.commentWithP = 0
        self.parent.advSettingsList[7] = self.parent.commentWithP

    def setOnTopDefault(self):
        """항상 위에 고정 여부 함수"""
        if self.uicheckbox4.isChecked():
            self.parent.onTopDefault = 1
        else:
            self.parent.onTopDefault = 0
        self.parent.advSettingsList[8] = self.parent.onTopDefault

