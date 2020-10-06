import photoshop.api as ps
from os import remove, path

from PyQt5.QtWidgets import (
    QMessageBox,
    QPushButton,
    QMenu,
    QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from pyautogui import hotkey, position
from clipboard import copy, paste
import time
from re import match

from SB2T.dialog import TextEditDialog


class TextLine(QPushButton):
    """메인 텍스트 라인을 담당하는 버튼 클래스"""

    def __init__(self, parent, num, mode, txt, connected_mode, head):
        super().__init__()
        self.num = num  # 텍스트 라인 인덱스
        self.parent = parent
        self.mode = mode  # 0: 주석, 1: 버튼
        self.txt = txt
        self.pasted = 0  # 붙여넣기 흔적용 플래그 (0:X, 1:최근, 2:흔적)
        self.connected_mode = connected_mode  # 0: 머리, 1: 중간, 2: 꼬리
        self.head = head
        if self.connected_mode != -1:
            self.act_connection = 1
        else:
            self.act_connection = 0
        self.attribute = 'none' # 대화 = conversation, 
                                # 생각 = think,
                                # 독백 = narration,
                                # 강조 = emphasis,
                                # 효과 = effect,
                                # 배경 = background
        self.clicked.connect(self.copyPasteEvent)
        self.setIconSize(QSize(24, 24))
        self.setLine()
        self.setContextMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def setLine(self):
        """모드에 따라 텍스트 라인을 세팅하는 함수"""
        self.setTextOfLine()
        self.setStyleOfLine('default')
        self.setCheckableOfLine()

    def setTextOfLine(self):
        """버튼에 표시되는 텍스트 설정 함수"""
        self.attribute = 'none'
        self.setIcon(QIcon(''))
        if self.mode:   # 기본 버튼 모드
            if self.txt[0] == '[':
                try:
                    index = self.txt.index(']')
                    temp = self.txt[1:index]
                    self.setText(self.txt[index + 1:])
                    if temp == '대화':
                        self.attribute = 'conversation'
                        self.setIcon(QIcon('icons/conversation.png'))
                    elif temp == '생각':
                        self.attribute = 'think'
                        self.setIcon(QIcon('icons/think.png'))
                    elif temp == '독백':
                        self.attribute = 'narration'
                        self.setIcon(QIcon('icons/narration.png'))
                    elif temp == '강조':
                        self.attribute = 'emphasis'
                        self.setIcon(QIcon('icons/emphasis.png'))
                    elif temp == '효과':
                        self.attribute = 'effect'
                        self.setIcon(QIcon('icons/effect.png'))
                    elif temp == '배경':
                        self.attribute = 'background'
                        self.setIcon(QIcon('icons/background.png'))
                except:
                    self.setText(self.txt)
            else:
                self.setText(self.txt)
        else:   # 주석 처리
            if self.txt[0] == '/' or self.txt[0] == '`':
                self.setText(self.txt[1:])
            else:
                self.setText(self.txt)

    def setStyleOfLine(self, status):
        """
        텍스트 라인의 성격에 따라 스타일 설정하는 함수\n
        hover: #ffffa8 / chekced: yellow / 
        last pasted: #ffe0b2 / pasted: #f9f9f9 / 
        connected-act: #ff9800 / connected-deact: #969696
        """
        bmk = ''
        border_left = ''
        if self.parent.bookmark == self.num:
            border_left = 'border-left: 3px solid #e5aa17;'
            bmk = (
                'border-top: 3px solid #e5aa17;'
                'border-right: 3px solid #e5aa17;'
                'border-bottom: 3px solid #e5aa17;'
                'font-weight: bold;'
                # 'color: #803701'
                'color: white;'
            )

        if status == 'default':
            if self.pasted == 0:
                background_color = ''
                if self.parent.bookmark == self.num:
                    background_color = 'background-color: #e5aa17;'
                else:
                    background_color = ''
            elif self.pasted == 1:
                background_color = 'background-color: #ffe0b2;'
            elif self.pasted == 2:
                background_color = 'background-color: #f9f9f9;'
            chk_bg_color = 'background-color: yellow;'
        elif status == 'hover':
            background_color = 'background-color: #ffffa8;'
            chk_bg_color = 'background-color: #ffffa8;'

        if self.connected_mode == -1:
            margin = 'margin: 2px 0px;'
            if self.attribute != 'none':
                padding = 'padding: 6px 10px 6px 10px;'
            else:
                padding = 'padding: 10px;'
        else:
            if self.connected_mode == 0:
                margin = 'margin-top: 2px;'
                if self.attribute != 'none':
                    padding = 'padding: 6px 10px 1px 10px;'
                else:
                    padding = 'padding: 10px 10px 5px 10px;'
            elif self.connected_mode == 1:
                margin = ''
                if self.attribute != 'none':
                    padding = 'padding: 1px 10px;'
                else:
                    padding = 'padding: 5px 10px;'
            elif self.connected_mode == 2:
                margin = 'margin-bottom: 2px;'
                if self.attribute != 'none':
                    padding = 'padding: 1px 10px 6px 10px;'
                else:
                    padding = 'padding: 5px 10px 10px 10px;'
            if self.act_connection:
                border_left = 'border-left: 3px solid #ff3d00;'
            else:
                border_left = 'border-left: 3px solid #969696;'
                if self.attribute != 'none':
                    padding = 'padding: 6px 10px 6px 10px;'
                else:
                    padding = 'padding: 10px;'

        self.setStyleSheet(self.makeStyleStr(
            chk_bg_color, background_color, border_left, margin, padding, bmk))

    def makeStyleStr(
    self, chk_bg_color, background_color, border_left, margin, padding, bmk) -> str:
        """설정된 속성을 스타일 텍스트에 적용시켜 리턴하는 함수"""
        if self.mode:
            return (
                " QPushButton {border: none; text-align: left;"
                + padding + margin + background_color + border_left + bmk + "}"
                " QPushButton:checked {" + chk_bg_color + "color: black;" + "}"
                " QPushButton:hover {background-color: #ffffa8; color: black;} ")
        else:
            return (
                " QPushButton {border: none; text-align: left; font-style: italic;"
                " background-color: #E2E2E2; padding: 5px 10px; "
                + margin + border_left + bmk + "color: black;" + "}")

    def setCheckableOfLine(self):
        """모드에 따라 버튼 체크 가능 여부 정하는 함수"""
        if self.mode:
            self.setCheckable(True)
        else:
            self.setCheckable(False)

    def enterEvent(self, e):
        """마우스 포인터를 버튼 위에 올렸을 때 실행되는 함수"""
        if self.act_connection:  # 연결 여부에 따라 연결된 버튼을 일괄 hover화
            if self.connected_mode == 0:
                self.parent.btn[self.num + 1].setConnectStyle(-1, 'hover')
            elif self.connected_mode == 1:
                self.parent.btn[self.num - 1].setConnectStyle(1, 'hover')
                self.parent.btn[self.num + 1].setConnectStyle(-1, 'hover')
            elif self.connected_mode == 2:
                self.parent.btn[self.num - 1].setConnectStyle(1, 'hover')

    def leaveEvent(self, e):
        """마우스 포인터를 버튼에서 떨어뜨렸을 때 실행되는 함수"""
        if self.act_connection:  # 강제 hover 해제
            if self.connected_mode == 0:
                self.parent.btn[self.num + 1].setConnectStyle(-1, 'default')
            elif self.connected_mode == 1:
                self.parent.btn[self.num - 1].setConnectStyle(1, 'default')
                self.parent.btn[self.num + 1].setConnectStyle(-1, 'default')
            elif self.connected_mode == 2:
                self.parent.btn[self.num - 1].setConnectStyle(1, 'default')

    def setConnectStyle(self, way, status):
        """연결된 라인들을 순차적으로 인자로 받은 스타일로 변경하는 함수"""
        self.setStyleOfLine(status)
        if self.connected_mode == 1:
            self.parent.btn[self.num - way].setConnectStyle(way, status)

    def setContextMenu(self):
        """콘텍스트 메뉴 초기 설정 함수"""
        self.textEditAction = QAction('텍스트 수정(&E)')
        self.textEditAction.triggered.connect(self.setTextEditDialog)
        self.chgToCmtAction = QAction('주석 적용(&C)')
        self.chgToCmtAction.triggered.connect(self.changeMode)
        self.chgToBtnAction = QAction('주석 해제(&C)')
        self.chgToBtnAction.triggered.connect(self.changeMode)
        self.disconnectAction = QAction('연결 비활성화(&A)')
        self.disconnectAction.triggered.connect(lambda: self.setActiveConnection(False))
        self.connectAction = QAction('연결 활성화(&A)')
        self.connectAction.triggered.connect(lambda: self.setActiveConnection(True))
        self.delBmkAction = QAction('책갈피 삭제(&B)')
        self.delBmkAction.triggered.connect(lambda: self.setBookmark(False))
        self.createBmkAction = QAction('책갈피 생성(&B)')
        self.createBmkAction.triggered.connect(lambda: self.setBookmark(True))
        self.con = QAction('대화(&1)')
        self.con.setCheckable(True)
        self.con.triggered.connect(lambda: self.changeAttribute('대화', self.con))
        self.emp = QAction('강조(&2)')
        self.emp.setCheckable(True)
        self.emp.triggered.connect(lambda: self.changeAttribute('강조', self.emp))
        self.nar = QAction('독백(&3)')
        self.nar.setCheckable(True)
        self.nar.triggered.connect(lambda: self.changeAttribute('독백', self.nar))
        self.thk = QAction('생각(&4)')
        self.thk.setCheckable(True)
        self.thk.triggered.connect(lambda: self.changeAttribute('생각', self.thk))
        self.bkg = QAction('배경(&5)')
        self.bkg.setCheckable(True)
        self.bkg.triggered.connect(lambda: self.changeAttribute('배경', self.bkg))
        self.eff = QAction('효과(&6)')
        self.eff.setCheckable(True)
        self.eff.triggered.connect(lambda: self.changeAttribute('효과', self.eff))

        self.tag_menu = QMenu('대사 태그 변경(&T)', self)
        self.tag_menu.addAction(self.con)
        self.tag_menu.addAction(self.emp)
        self.tag_menu.addAction(self.nar)
        self.tag_menu.addAction(self.thk)
        self.tag_menu.addAction(self.bkg)
        self.tag_menu.addAction(self.eff)

    def showContextMenu(self, pos):
        """콘텍스트 메뉴 보여주는 함수"""
        menu = QMenu(self)
        menu.addAction(self.textEditAction)
        menu.addSeparator()
        if self.mode:
            menu.addAction(self.chgToCmtAction)
        else:
            menu.addAction(self.chgToBtnAction)
        if self.connected_mode != -1:
            if self.act_connection:
                menu.addAction(self.disconnectAction)
            else:
                menu.addAction(self.connectAction)
        menu.addSeparator()
        if self.parent.bookmark == self.num:
            menu.addAction(self.delBmkAction)
        else:
            menu.addAction(self.createBmkAction)
        if self.mode:
            menu.addSeparator()
            menu.addMenu(self.tag_menu)

        self.con.setChecked(False)
        self.emp.setChecked(False)
        self.nar.setChecked(False)
        self.thk.setChecked(False)
        self.bkg.setChecked(False)
        self.eff.setChecked(False)
        if self.attribute == 'conversation':
            self.con.setChecked(True)
        elif self.attribute == 'emphasis':
            self.emp.setChecked(True)
        elif self.attribute == 'narration':
            self.nar.setChecked(True)
        elif self.attribute == 'think':
            self.thk.setChecked(True)
        elif self.attribute == 'background':
            self.bkg.setChecked(True)
        elif self.attribute == 'effect':
            self.eff.setChecked(True)
        
        pos = self.mapToGlobal(pos)
        menu.move(pos)
        menu.show()

    def changeMode(self):
        """모드를 바꾸는 함수(주석, 버튼)"""
        if self.mode:
            self.mode = 0
        else:
            self.mode = 1
        self.setLine()

    def changeAttribute(self, attribute, action):
        """대사 태그를 바꾸는 함수"""
        if self.attribute != 'none':
            index = self.txt.index(']')
            self.txt = self.txt[index + 1:]
        if action.isChecked():
            self.txt = '[' + attribute + ']' + self.txt
        self.setLine()
        self.parent.recordChange()

    def setBookmark(self, boolean):
        """책갈피 설정하는 함수"""
        fname = self.parent.filepath + '.bmk'
        if boolean:
            back = self.parent.bookmark
            self.parent.bookmark = self.num
            self.parent.btn[back].setStyleOfLine('default')
            self.setStyleOfLine('default')
            self.parent.goBmkEdit.setEnabled(True)
            self.parent.goBookmarkAction.setEnabled(True)
            try:
                with open(fname, 'w') as f:
                    f.write(str(self.num))
            except Exception as e:
                QMessageBox.warning(self, "오류", "책갈피를 저장하지 못했습니다.\n" + str(e))
        else:
            self.parent.bookmark = -1
            self.setStyleOfLine('default')
            self.parent.goBmkEdit.setDisabled(True)
            self.parent.goBookmarkAction.setDisabled(True)
            try:
                if path.exists(fname):
                    remove(fname)
            except Exception as e:
                QMessageBox.warning(self, "오류", "책갈피를 삭제하지 못했습니다.\n" + str(e))

    def setActiveConnection(self, boolean):
        """연결 활성화하는 함수"""
        mode = 0
        i = self.head
        while True:
            self.parent.btn[i].act_connection = boolean
            self.parent.btn[i].setLine()
            if self.parent.btn[i].connected_mode == 2:
                break;
            i += 1

    def mouseDoubleClickEvent(self, a0):
        """버튼 더블 클릭 시 실행되는 함수"""
        self.setTextEditDialog()

    def setTextEditDialog(self):
        """텍스트 수정 창 생성하는 함수"""
        dialog = TextEditDialog(self)

    def copyText(self):
        """비연결 시 텍스트 라인 한 줄, 연결 시 여러 줄을 복사하는 함수"""
        if self.act_connection:
            self.copyConnectedLines()
        else:
            self.copyOneLine()

    def whatTxtForCopy(self) -> str:
        """실제 복사할 텍스트를 반환하는 함수\n
        소괄호, 중괄호, 대괄호, 큰따음표, 작은따음표 제외 복사 기능 포함"""
        temptxt = self.text()
        if self.parent.exceptbrackets:   # 괄호문을 인식하여 괄호만 빼고 복사
            if temptxt[0] == '(' and temptxt[len(temptxt) - 1] == ')':
                temptxt = temptxt[1:len(temptxt) - 1]

        if self.parent.exceptCurlybrackets:   # 괄호문을 인식하여 괄호만 빼고 복사
            if temptxt[0] == '{' and temptxt[len(temptxt) - 1] == '}':
                temptxt = temptxt[1:len(temptxt) - 1]

        if self.parent.exceptSquarebrackets:   # 괄호문을 인식하여 괄호만 빼고 복사
            if temptxt[0] == '[' and temptxt[len(temptxt) - 1] == ']':
                temptxt = temptxt[1:len(temptxt) - 1]

        if self.parent.exceptDQuotaion:   # 큰 따옴표 인식하여 괄호만 빼고 복사
            if temptxt[0] == '"' and temptxt[len(temptxt) - 1] == '"':
                temptxt = temptxt[1:len(temptxt) - 1]

        if self.parent.exceptSQuotaion:   # 작은 따옴표 인식하여 괄호만 빼고 복사
            if temptxt[0] == "'" and temptxt[len(temptxt) - 1] == "'":
                temptxt = temptxt[1:len(temptxt) - 1]
        
        return temptxt

    def copyOneLine(self):
        """한 줄만 복사하는 함수"""
        copy(self.whatTxtForCopy())

        self.parent.lineStatus.setText(' 줄 ' + str(self.num + 1) + '  ')
        self.parent.lineCnt.clear()
        self.parent.lineCnt.append(self.num)
        self.autoScroll(self.num)
        self.cleanToggle()
        if self.parent.ProgramSettingOn:
            self.parent.pasteEdit.setEnabled(True)

    def copyConnectedLines(self):
        """연결된 모든 줄을 한꺼번에 복사하는 함수"""
        temptxt = ''
        i = self.head
        self.parent.lineCnt.clear()
        while True:
            if self.parent.btn[i].mode:
                temptxt = temptxt + self.parent.btn[i].whatTxtForCopy()
                self.parent.btn[i].setChecked(True)
                self.parent.lineCnt.append(i)
                if self.parent.btn[i].connected_mode != 2:
                    temptxt = temptxt + '\r'  # \n 경우, 포토샵에 붙여넣기 할 때 개행으로 인식 안 됨

            if self.parent.btn[i].connected_mode == 2:
                break
            else:
                i += 1
        copy(temptxt)

        self.parent.lineStatus.setText(' 줄 ' + str(i + 1) + '  ')
        self.autoScroll(self.parent.lineCnt[-1])
        self.cleanToggle()
        if self.parent.ProgramSettingOn:
            self.parent.pasteEdit.setEnabled(True)

    def autoScroll(self, num):
        """텍스트 클릭, 혹은 텍스트 선택 변경 시 보기 편하게 자동으로 스크롤 해주는 함수"""
        if (num > 0 and num < 4) or (num >= len(self.parent.btn) - 4 and num < len(self.parent.btn) - 1):
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num - 1], 0, 0)
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num + 1], 0, 0)
        elif num >= 4 and num < len(self.parent.btn) - 4:
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num - 4], 0, 0)
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num + 4], 0, 0)
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num - 1], 0, 0)
            self.parent.scroll.ensureWidgetVisible(self.parent.btn[num + 1], 0, 0)
        self.parent.scroll.ensureWidgetVisible(self.parent.btn[num], 0, 50)

    def cleanToggle(self):
        """버튼 토글 정리해주는 함수"""
        if not self.isChecked():
            self.toggle()
        for i in range(len(self.parent.btn)):
            if self.parent.btn[i].mode:
                if i != self.num:
                    if self.parent.btn[i].isChecked():
                        if self.act_connection:
                            if self.head != self.parent.btn[i].head:
                                self.parent.btn[i].toggle()
                        else:
                            self.parent.btn[i].toggle()
        self.parent.hbar.setValue(self.parent.hbar.minimum())  # 이렇게 좌로 스크롤 안 해주면 수평 스크롤이 자꾸 중앙으로 간다

    def setUncheckedAfterPaste(self):
        """복사 후 버튼 체크 풀어주는 함수"""
        if self.act_connection:
            i = self.head
            while True:
                self.parent.btn[i].setChecked(False)
                if self.parent.btn[i].connected_mode == 2:
                    break
                i += 1
        else:
            self.setChecked(False)

    def pasteText(self):
        """기본 모드와 자동 모드 시 적용되는 붙여넣기 함수"""
        self.parent.windowFocus()
        hotkey('ctrl', 'v')
        self.setUncheckedAfterPaste()
        self.parent.pasteEdit.setDisabled(True)
        if self.parent.psAutoStartAction.isEnabled():
            if self.attribute != 'none' and self.parent.currentTextItemStyle != None:
                hotkey('ctrl', 'enter')
                while True:
                    try:
                        item = ps.Application().ActiveDocument.ActiveLayer.textItem
                        self.setStyleOfTextItem(item)
                        break
                    except:
                        pass
            else:
                if self.parent.pasteCtrlEnter:  # 포토샵 한정 자동 레이어 닫기 여부
                    hotkey('ctrl', 'enter')

        self.setTraceTextLine()
        if self.parent.psAutoStartAction.isChecked():  # PS 모드 동시 사용 시 다음 라인 자동 복사
            time.sleep(.05)  # 이렇게 안 해주면 PS 모드 동시 사용 시 다음 라인이 복붙되는 현상 발생
            self.parent.nextLineCopy()
        # self.parent.resetRecordAction.setEnabled(True)
        self.parent.resetRecord.setEnabled(True)

    def pasteTextPSMode(self):
        """PS 모드 시 적용되는 붙여넣기 함수"""
        while True:
            try:
                item = ps.Application().ActiveDocument.ActiveLayer.textItem
                item.contents = paste()  # 텍스트 레이어 내용물 변경
                if self.attribute != 'none' and self.parent.currentTextItemStyle != None:
                    self.setStyleOfTextItem(item)
                self.parent.psAutoThreadStart()
                break
            except:
                pass  # 텍스트 바뀌기도 전에 텍스트 레이어 옮길 때 생기는 충돌 현상 방지

        self.setTraceTextLine()
        self.parent.nextLineCopy()
        # self.parent.resetRecordAction.setEnabled(True)
        self.parent.resetRecord.setEnabled(True)

    def setStyleOfTextItem(self, item):
        """현재 지정된 포토샵 문자 설정을 반영하는 함수"""
        atr = self.parent.currentTextItemStyle.attributes
        if self.act_connection:
            attribute = self.parent.btn[self.parent.lineCnt[0]].attribute
        else:
            attribute = self.attribute
        if atr[attribute]['activate']:
            if atr[attribute]['font'] != 'none':
                item.font = atr[attribute]['font']
            if atr[attribute]['size'] != 'none':
                item.size = atr[attribute]['size']
            if atr[attribute]['leading'] != 'none':
                item.leading = atr[attribute]['leading']
            if atr[attribute]['tracking'] != 'none':
                item.tracking = atr[attribute]['tracking']
            if atr[attribute]['fauxBold'] != 'none':
                item.fauxBold = atr[attribute]['fauxBold']
            if atr[attribute]['fauxItalic'] != 'none':
                item.fauxItalic = atr[attribute]['fauxItalic']
            if atr[attribute]['horizontalScale'] != 'none':
                item.horizontalScale = atr[attribute]['horizontalScale']
            if atr[attribute]['verticalScale'] != 'none':
                item.verticalScale = atr[attribute]['verticalScale']
        # layer.textItem.height = 100
        # layer.textItem.width = 200
        # layer.textItem.position = [10, 10]

    def setTraceTextLine(self): 
        """텍스트 라인 색상 바꾸는 함수 (흔적 남기기)"""
        if len(self.parent.lineCntBack) != 0:
            for i in self.parent.lineCntBack:
                if self.parent.btn[i].mode:
                    self.parent.btn[i].pasted = 2
                    self.parent.btn[i].setStyleOfLine('default')

        for i in self.parent.lineCnt:
            if self.parent.btn[i].mode:
                self.parent.btn[i].pasted = 1
                self.parent.btn[i].setStyleOfLine('default')

        self.parent.lineCntBack = self.parent.lineCnt[:]

    def copyPasteEvent(self, parent):
        """텍스트 라인 클릭 시 실행되는 함수\n
        기본 모드 시 복사만, 자동 모드 시 붙여넣기까지"""
        if self.mode:
            if self.parent.autoStartAction.isChecked():  # 자동 모드일 때
                self.copyText()
                self.pasteText()
            else:  # 기본 모드일 때. 클릭 시 복사만 진행
                self.copyText()

