import photoshop.api as ps
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QCheckBox,
    QTabWidget,
    QFontComboBox,
    QSpinBox
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from SB2T.obj import AttributeOfTextItem
from .loading import LoadingDialog


class SetAttributeDialog(QDialog):
    """세부 문자 설정 창 클래스"""

    def __init__(self, parent, selectedIdx):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent
        self.selectedIdx = selectedIdx
        # self.font_list = font_list

        lbl_name = QLabel('이름:')
        self.lineEdit = QLineEdit()
        self.lineEdit.setMaxLength(40)

        if self.selectedIdx != 'none':
            self.selectedTIS = self.parent.parent.textItemStyleList[self.selectedIdx]
            self.tempAtr = self.selectedTIS
            self.lineEdit.setText(self.tempAtr.name)
        else:
            self.selectedTIS = 'none'
            self.tempAtr = AttributeOfTextItem()
            self.lineEdit.setText('기본 설정')

        btn = QPushButton('저장')
        btn.clicked.connect(self.saveAtr)

        layer1 = QHBoxLayout()
        layer1.addWidget(lbl_name)
        layer1.addWidget(self.lineEdit)
        layer1.setContentsMargins(0, 0, 0, 10)
        layer2 = QHBoxLayout()
        layer2.addWidget(btn)
        layer2.setAlignment(Qt.AlignRight)

        conTab = QWidget()
        conTab.setLayout(SetAttributeGrid(self, 'conversation'))
        thkTab = QWidget()
        thkTab.setLayout(SetAttributeGrid(self, 'think'))
        empTab = QWidget()
        empTab.setLayout(SetAttributeGrid(self, 'emphasis'))
        effTab = QWidget()
        effTab.setLayout(SetAttributeGrid(self, 'effect'))
        narTab = QWidget()
        narTab.setLayout(SetAttributeGrid(self, 'narration'))
        bgTab = QWidget()
        bgTab.setLayout(SetAttributeGrid(self, 'background'))

        tabs = QTabWidget()
        tabs.addTab(conTab, '대화')
        tabs.addTab(empTab, '강조')
        tabs.addTab(narTab, '독백')
        tabs.addTab(thkTab, '생각')
        tabs.addTab(bgTab, '배경')
        tabs.addTab(effTab, '효과')

        vbox = QVBoxLayout()
        vbox.addLayout(layer1)
        vbox.addWidget(tabs)
        vbox.addLayout(layer2)

        self.setLayout(vbox)
        self.setWindowIcon(QIcon('icons/setpsmode.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()
        self.move(x - 50, y + 100)
        if self.selectedTIS == 'none':
            self.setWindowTitle('대사별 문자 설정 추가')
        else:
            self.setWindowTitle('대사별 문자 설정 수정')
        self.exec()

    def saveAtr(self):
        """문자 설정을 저장하는 함수"""
        load_dialog = LoadingDialog(self, '저장 중입니다...', 'icons/setpsmode.png')

        style_list = self.parent.parent.textItemStyleList
        self.tempAtr.name = self.lineEdit.text()

        if self.selectedTIS != 'none':
            style_list[self.selectedIdx] = self.tempAtr
        else:
            style_list.append(self.tempAtr)
        self.parent.listUp()
        self.parent.updateComBoxForTIS()
        # print('save -> ' + self.parent.parent.textItemStyleList[self.selectedIdx].attributes['conversation']['family'])  # 디버깅
        self.close()


class SetAttributeGrid(QGridLayout):
    """태그별 탭 생성을 위한 그리드 클래스"""

    def __init__(self, parent, attribute):
        QGridLayout.__init__(self)
        self.parent = parent
        self.attribute = attribute

        self.chk_activate = QCheckBox('설정 활성화')
        
        self.chk_font = QCheckBox('글꼴:')
        self.fontComBox = QFontComboBox()
        self.hbox_font = QHBoxLayout()
        self.hbox_font.addWidget(self.chk_font)
        self.hbox_font.addWidget(self.fontComBox)
        self.hbox_font.setContentsMargins(0, 15, 0, 3)
        self.chk_font.setDisabled(True)
        self.fontComBox.setDisabled(True)

        self.chk_size = QCheckBox('크기:')
        self.spbx_size = QSpinBox()
        self.spbx_size.setSuffix(' pt')
        self.spbx_size.setRange(1, 100)
        self.spbx_size.setValue(20)
        self.hbox_size = QHBoxLayout()
        self.hbox_size.addWidget(self.chk_size)
        self.hbox_size.addWidget(self.spbx_size)
        self.hbox_size.setContentsMargins(0, 0, 5, 3)
        self.chk_size.setDisabled(True)
        self.spbx_size.setDisabled(True)

        self.chk_leading = QCheckBox('행간:')
        self.spbx_leading = QSpinBox()
        self.spbx_leading.setSuffix(' pt')
        self.spbx_leading.setRange(1, 150)
        self.spbx_leading.setValue(25)
        self.hbox_leading = QHBoxLayout()
        self.hbox_leading.addWidget(self.chk_leading)
        self.hbox_leading.addWidget(self.spbx_leading)
        self.hbox_leading.setContentsMargins(0, 0, 5, 3)
        self.chk_leading.setDisabled(True)
        self.spbx_leading.setDisabled(True)

        self.chk_tracking = QCheckBox('자간:')
        self.spbx_tracking = QSpinBox()
        self.spbx_tracking.setRange(-100, 200)
        self.spbx_tracking.setValue(0)
        self.hbox_tracking = QHBoxLayout()
        self.hbox_tracking.addWidget(self.chk_tracking)
        self.hbox_tracking.addWidget(self.spbx_tracking)
        self.hbox_tracking.setContentsMargins(0, 0, 5, 0)
        self.chk_tracking.setDisabled(True)
        self.spbx_tracking.setDisabled(True)

        self.chk_hscale = QCheckBox('가로 비율:')
        self.spbx_hscale = QSpinBox()
        self.spbx_hscale.setSuffix('%')
        self.spbx_hscale.setRange(0, 200)
        self.spbx_hscale.setValue(100)
        self.hbox_hscale = QHBoxLayout()
        self.hbox_hscale.addWidget(self.chk_hscale)
        self.hbox_hscale.addWidget(self.spbx_hscale)
        # self.hbox_hscale.setContentsMargins(0, 2, 10, 2)
        self.chk_hscale.setDisabled(True)
        self.spbx_hscale.setDisabled(True)

        self.chk_vscale = QCheckBox('세로 비율:')
        self.spbx_vscale = QSpinBox()
        self.spbx_vscale.setSuffix('%')
        self.spbx_vscale.setRange(0, 200)
        self.spbx_vscale.setValue(100)
        self.hbox_vscale = QHBoxLayout()
        self.hbox_vscale.addWidget(self.chk_vscale)
        self.hbox_vscale.addWidget(self.spbx_vscale)
        # self.hbox_vscale.setContentsMargins(10, 2, 10, 2)
        self.chk_vscale.setDisabled(True)
        self.spbx_vscale.setDisabled(True)

        self.chk_style = QCheckBox('스타일:')
        self.btn_bold = QPushButton(QIcon('icons/bold.png'), '', )
        self.btn_bold.setToolTip('볼드체')
        self.btn_bold.setCheckable(True)
        self.btn_bold.setAutoDefault(False)
        self.btn_italic = QPushButton(QIcon('icons/italic.png'), '', )
        self.btn_italic.setToolTip('이탤릭체')
        self.btn_italic.setCheckable(True)
        self.btn_italic.setAutoDefault(False)
        self.btn_hbox = QHBoxLayout()
        self.btn_hbox.addWidget(self.chk_style)
        self.btn_hbox.addWidget(self.btn_bold)
        self.btn_hbox.addWidget(self.btn_italic)
        # self.btn_hbox.setContentsMargins(10, 2, 0, 2)
        self.chk_style.setDisabled(True)
        self.btn_bold.setDisabled(True)
        self.btn_italic.setDisabled(True)

        if self.parent.selectedTIS != 'none':
            selTIS = self.parent.selectedTIS
            activate = selTIS.attributes[self.attribute]['activate']
            family = selTIS.attributes[self.attribute]['family']
            # print('selTIS.attributes -> ' + family)  #디버깅
            if family != 'none':
                self.chk_font.setChecked(True)
                self.fontComBox.setCurrentFont(QFont(family))
            size = selTIS.attributes[self.attribute]['size']
            if size != 'none':
                self.chk_size.setChecked(True)
                self.spbx_size.setValue(size)
            leading = selTIS.attributes[self.attribute]['leading']
            if leading != 'none':
                self.chk_leading.setChecked(True)
                self.spbx_leading.setValue(leading)
            tracking = selTIS.attributes[self.attribute]['tracking']
            if tracking != 'none':
                self.chk_tracking.setChecked(True)
                self.spbx_tracking.setValue(tracking)
            hscale = selTIS.attributes[self.attribute]['horizontalScale']
            if hscale != 'none':
                self.chk_hscale.setChecked(True)
                self.spbx_hscale.setValue(hscale)
            vscale = selTIS.attributes[self.attribute]['verticalScale']
            if vscale != 'none':
                self.chk_vscale.setChecked(True)
                self.spbx_vscale.setValue(vscale)
            bold = selTIS.attributes[self.attribute]['fauxBold']
            italic = selTIS.attributes[self.attribute]['fauxItalic']
            if bold != 'none' and italic != 'none':
                self.chk_style.setChecked(True)
                self.btn_bold.setChecked(bold)
                self.btn_italic.setChecked(italic)
            if activate:
                self.chk_activate.setChecked(True)
                self.actAll()

        self.chk_activate.stateChanged.connect(self.actAll)
        self.chk_font.stateChanged.connect(self.actFont)
        self.fontComBox.currentFontChanged.connect(self.changeFont)
        self.chk_size.stateChanged.connect(self.actSize)
        self.spbx_size.valueChanged.connect(self.changeSize)
        self.chk_leading.stateChanged.connect(self.actLeading)
        self.spbx_leading.valueChanged.connect(self.changeLeading)
        self.chk_tracking.stateChanged.connect(self.actTracking)
        self.spbx_tracking.valueChanged.connect(self.changeTracking)
        self.chk_hscale.stateChanged.connect(self.actHscale)
        self.spbx_hscale.valueChanged.connect(self.changeHscale)
        self.chk_vscale.stateChanged.connect(self.actVscale)
        self.spbx_vscale.valueChanged.connect(self.changeVscale)
        self.chk_style.stateChanged.connect(self.actStyle)
        self.btn_bold.clicked.connect(self.changeBold)
        self.btn_italic.clicked.connect(self.changeItalic)

        self.addWidget(self.chk_activate, 0, 0)
        self.addLayout(self.hbox_font, 1, 0, 1, 0, Qt.AlignLeft)
        self.addLayout(self.hbox_size, 2, 0)
        self.addLayout(self.hbox_leading, 2, 1)
        self.addLayout(self.hbox_tracking, 3, 1)
        self.addLayout(self.hbox_hscale, 2, 2)
        self.addLayout(self.hbox_vscale, 3, 2)
        self.addLayout(self.btn_hbox, 3, 0, Qt.AlignLeft)

    def actAll(self):
        """전체 설정 활성화 여부 함수"""
        if self.chk_activate.isChecked():
            self.parent.tempAtr.attributes[self.attribute]['activate'] = True
            self.chk_font.setEnabled(True)
            self.chk_size.setEnabled(True)
            self.chk_leading.setEnabled(True)
            self.chk_tracking.setEnabled(True)
            self.chk_hscale.setEnabled(True)
            self.chk_vscale.setEnabled(True)
            self.chk_style.setEnabled(True)
            self.actFont()
            self.actSize()
            self.actLeading()
            self.actTracking()
            self.actHscale()
            self.actVscale()
            self.actStyle()
        else:
            self.parent.tempAtr.attributes[self.attribute]['activate'] = False
            self.chk_font.setDisabled(True)
            self.chk_size.setDisabled(True)
            self.chk_leading.setDisabled(True)
            self.chk_tracking.setDisabled(True)
            self.chk_hscale.setDisabled(True)
            self.chk_vscale.setDisabled(True)
            self.chk_style.setDisabled(True)
            self.fontComBox.setDisabled(True)
            self.spbx_size.setDisabled(True)
            self.spbx_leading.setDisabled(True)
            self.spbx_tracking.setDisabled(True)
            self.spbx_hscale.setDisabled(True)
            self.spbx_vscale.setDisabled(True)
            self.btn_bold.setDisabled(True)
            self.btn_italic.setDisabled(True)

    def actFont(self):
        """폰트 설정 활성화 여부 함수"""
        if self.chk_font.isChecked():
            self.fontComBox.setEnabled(True)
            # print('actFont -> ' + self.fontComBox.currentFont().family())  #디버깅
            family = self.fontComBox.currentFont().family()
            self.parent.tempAtr.attributes[self.attribute]['family'] = family
        else:
            self.fontComBox.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['family'] = 'none'

    def actSize(self):
        """크기 설정 활성화 여부 함수"""
        if self.chk_size.isChecked():
            self.spbx_size.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['size'] = self.spbx_size.value()
        else:
            self.spbx_size.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['size'] = 'none'

    def actLeading(self):
        """행간 설정 활성화 여부 함수"""
        if self.chk_leading.isChecked():
            self.spbx_leading.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['leading'] = self.spbx_leading.value()
        else:
            self.spbx_leading.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['leading'] = 'none'

    def actTracking(self):
        """자간 설정 활성화 여부 함수"""
        if self.chk_tracking.isChecked():
            self.spbx_tracking.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['tracking'] = self.spbx_tracking.value()
        else:
            self.spbx_tracking.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['tracking'] = 'none'

    def actHscale(self):
        """가로 비율 설정 활성화 여부 함수"""
        if self.chk_hscale.isChecked():
            self.spbx_hscale.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['horizontalScale'] = self.spbx_hscale.value()
        else:
            self.spbx_hscale.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['horizontalScale'] = 'none'

    def actVscale(self):
        """세로 비율 설정 활성화 여부 함수"""
        if self.chk_vscale.isChecked():
            self.spbx_vscale.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['verticalScale'] = self.spbx_vscale.value()
        else:
            self.spbx_vscale.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['verticalScale'] = 'none'

    def actStyle(self):
        """스타일 설정 활성화 여부 함수"""
        if self.chk_style.isChecked():
            self.btn_bold.setEnabled(True)
            self.btn_italic.setEnabled(True)
            self.parent.tempAtr.attributes[self.attribute]['fauxBold'] = self.btn_bold.isChecked()
            self.parent.tempAtr.attributes[self.attribute]['fauxItalic'] = self.btn_italic.isChecked()
        else:
            self.spbx_vscale.setDisabled(True)
            self.btn_bold.setDisabled(True)
            self.btn_italic.setDisabled(True)
            self.parent.tempAtr.attributes[self.attribute]['fauxBold'] = False
            self.parent.tempAtr.attributes[self.attribute]['fauxItalic'] = False

    def changeFont(self, font):
        """폰트 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['family'] = font.family()

    def changeSize(self, num):
        """크기 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['size'] = num

    def changeLeading(self, num):
        """행간 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['leading'] = num

    def changeTracking(self, num):
        """자간 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['tracking'] = num

    def changeHscale(self, num):
        """가로 비율 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['horizontalScale'] = num

    def changeVscale(self, num):
        """세로 비율 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['verticalScale'] = num

    def changeBold(self):
        """볼드체 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['fauxBold'] = self.btn_bold.isChecked()

    def changeItalic(self):
        """이탤릭체 바꾸는 함수"""
        self.parent.tempAtr.attributes[self.attribute]['fauxItalic'] = self.btn_italic.isChecked()

