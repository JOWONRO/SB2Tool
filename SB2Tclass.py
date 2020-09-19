import win32com.client
import pythoncom
from os import remove, path

from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QListWidget,
    QProgressBar,
    QMenu
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QThread

from pyautogui import hotkey, press, position
from clipboard import copy, paste
import time
import keyboard
from re import match
from threading import Thread


class TextLine(QPushButton):
    """메인 텍스트 라인을 담당하는 버튼 클래스"""

    def __init__(self, parent, num, mode, txt, connected_mode, head):
        super().__init__()
        self.num = num  # 텍스트 라인 인덱스
        self.parent = parent
        self.mode = mode    # 주석인지 기본 버튼인지 구분
        self.txt = txt
        self.pasted = 0  # 붙여넣기 흔적용 플래그 (0:X, 1:최근, 2:흔적)
        self.connected_mode = connected_mode
        self.head = head
        self.act_connection = 0
        if self.connected_mode != -1:
            self.act_connection = 1

        self.clicked.connect(self.copyPasteEvent)
        self.setLine()

    def setLine(self):
        """모드에 따라 텍스트 라인을 세팅하는 함수"""
        self.setTextOfLine()
        self.setStyleOfLine('default')
        self.setCheckableOfLine()

    def setTextOfLine(self):
        """버튼에 표시되는 텍스트 설정 함수"""
        if self.mode:   # 기본 버튼 모드
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
        if status == 'default':
            if self.pasted == 0:
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
            padding = 'padding: 10px;'
            border_left = ''
        else:
            if self.connected_mode == 0:
                margin = 'margin-top: 2px;'
                padding = 'padding: 10px 10px 5px 10px;'
            elif self.connected_mode == 1:
                margin = ''
                padding = 'padding: 5px 10px;'
            elif self.connected_mode == 2:
                margin = 'margin-bottom: 2px;'
                padding = 'padding: 5px 10px 10px 10px;'
            if self.act_connection:
                border_left = 'border-left: 3px solid #ff3d00;'
            else:
                border_left = 'border-left: 3px solid #969696;'
                padding = 'padding: 10px;'

        self.setStyleSheet(self.makeStyleStr(
            chk_bg_color, background_color, border_left, margin, padding))

    def makeStyleStr(
    self, chk_bg_color, background_color, border_left, margin, padding) -> str:
        """설정된 속성을 스타일 텍스트에 적용시켜 리턴하는 함수"""
        if self.mode:
            return (
                " QPushButton {border: none; text-align: left;"
                + padding + margin + background_color + border_left + "}"
                " QPushButton:checked {" + chk_bg_color + "}"
                " QPushButton:hover {background-color: #ffffa8;} ")
        else:
            return (
                " QPushButton {border: none; text-align: left; font-style: italic;"
                " background-color: #E2E2E2; padding: 5px 10px; "
                + margin + border_left + "}")

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

    def contextMenuEvent(self, event):
        """해당 텍스트 라인 우클릭 시 나타나는 메뉴 이벤트"""
        menu = QMenu(self)
        textEditAction = menu.addAction("텍스트 수정(&E)")
        menu.addSeparator()
        changeToCommentAction = menu.addAction("주석 적용(&C)")
        changeToButtonAction = menu.addAction("주석 해제(&C)")
        deactivateConnection = menu.addAction("연결 비활성화(&A)")
        activateConnection = menu.addAction("연결 활성화(&A)")
        menu.addSeparator()
        makeBookmark = menu.addAction("책갈피 생성(&B)")
        deleteBookmark = menu.addAction("책갈피 삭제(&B)")

        if self.mode:
            changeToCommentAction.setVisible(True)
            changeToButtonAction.setVisible(False)
        else:
            changeToCommentAction.setVisible(False)
            changeToButtonAction.setVisible(True)
        if self.connected_mode == -1:
            deactivateConnection.setVisible(False)
            activateConnection.setVisible(False)
        else:
            if self.act_connection:
                deactivateConnection.setVisible(True)
                activateConnection.setVisible(False)
            else:
                deactivateConnection.setVisible(False)
                activateConnection.setVisible(True)
        if self.parent.bookmark == self.num:
            makeBookmark.setVisible(False)
            deleteBookmark.setVisible(True)
        else:
            makeBookmark.setVisible(True)
            deleteBookmark.setVisible(False)

        action = menu.exec_(self.mapToGlobal(event.pos()))  # 우클릭한 지점에서 메뉴 생성
        if action == changeToCommentAction:
            self.mode = 0
            self.setLine()
            self.parent.recordChange()
        elif action == changeToButtonAction:
            self.mode = 1
            self.setLine()
            self.parent.recordChange()
        elif action == deactivateConnection:
            self.setActiveConnection(False)
        elif action == activateConnection:
            self.setActiveConnection(True)
        elif action == textEditAction:
            self.setTextEditDialog()
        elif action == makeBookmark:
            self.setBookmark(True)
        elif action == deleteBookmark:
            self.setBookmark(False)

    def setBookmark(self, boolean):
        """책갈피 설정하는 함수"""
        fname = self.parent.filepath + '.bmk'
        if boolean:
            self.setIcon(QIcon('icons/bookmark.png'))
            self.parent.btn[self.parent.bookmark].setIcon(QIcon(''))
            self.parent.bookmark = self.num
            self.parent.goBmkEdit.setEnabled(True)
            self.parent.goBookmarkAction.setEnabled(True)
            try:
                with open(fname, 'w') as f:
                    f.write(str(self.num))
            except Exception as e:
                QMessageBox.warning(self, "오류", "책갈피를 저장하지 못했습니다.\n" + str(e))
        else:
            self.setIcon(QIcon(''))
            self.parent.bookmark = -1
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
            self.parent.btn[i].setStyleOfLine('default')
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
        temptxt = self.txt
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
                    temptxt = temptxt + '\n'

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
        time.sleep(.1)  # 이렇게 안 해주면 PS 모드 동시 사용 시 다음 라인이 복붙되는 현상 발생

        if self.parent.pasteCtrlEnter:  # 포토샵 한정 자동 레이어 닫기 여부
            try:
                psApp = win32com.client.GetActiveObject("Photoshop.Application")
                hotkey('ctrl', 'enter')
            except:
                pass

        self.setTraceTextLine()
        if self.parent.psAutoStartAction.isChecked():  # PS 모드 동시 사용 시 다음 라인 자동 복사
            self.parent.nextLineCopy()
        # self.parent.resetRecordAction.setEnabled(True)
        self.parent.resetRecord.setEnabled(True)

    def pasteTextPSMode(self):
        """PS 모드 시 적용되는 붙여넣기 함수"""
        while True:
            try:
                psApp = win32com.client.GetActiveObject("Photoshop.Application")
                layer = psApp.Application.ActiveDocument.ActiveLayer
                layer.TextItem.Contents = paste()  # 텍스트 레이어 내용물 변경
                self.parent.psAutoThreadStart()
                break
            except:
                pass  # 텍스트 바뀌기도 전에 텍스트 레이어 옮길 때 생기는 충돌 현상 방지

        self.setTraceTextLine()
        self.parent.nextLineCopy()
        # self.parent.resetRecordAction.setEnabled(True)
        self.parent.resetRecord.setEnabled(True)

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


class TextEditDialog(QDialog):
    """텍스트 라인의 텍스트 수정 창 생성 함수"""

    def __init__(self, parent):
        super().__init__()
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


class AdvSettingsDialog(QDialog):
    """
    고급 설정창 클래스\n
    복사 기능, 붙여넣기 기능, UI 기능 조정 가능
    """

    def __init__(self, parent):
        super().__init__()
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
        self.setWindowIcon(QIcon(self.parent.AdvSetIcon))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 50, y + 150)
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

        vbox = QVBoxLayout()
        vbox.addWidget(self.subtitle1)
        vbox.addWidget(self.uicheckbox1)
        vbox.addStretch(1)
        vbox.addWidget(self.space)
        vbox.addWidget(self.subtitle2)
        vbox.addWidget(self.uicheckbox2)
        vbox.addWidget(self.uicheckbox3)
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


class TextFindDialog(QDialog):
    """특정 텍스트 찾기 창 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)  # 항상 최상위 고정
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
        self.setWindowIcon(QIcon(self.parent.FindIcon))
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


class TextChangeDialog(QDialog):
    """텍스트 바꾸기 창 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        QDialog.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        self.index = 0
        self.findlist = []
        self.listlen = 0
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
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
        self.setWindowIcon(QIcon(self.parent.ChangeIcon))
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


class StartPsThread(QThread):
    """PS 모드 스레드 클래스"""
    psTextLayerSignal = pyqtSignal(bool)    # 포토샵 모드에서 필요한 시그널

    def run(self):
        self.exec()

    def exec(self):
        """레이어 생성될 때까지 기다리는 반복하는 함수"""
        pythoncom.CoInitialize()  # 이거 안 하면 스레딩 오류나는 경우가 생김.
        while True:
            try:
                tempApp = win32com.client.GetActiveObject("Photoshop.Application")
                try:
                    layername = tempApp.Application.ActiveDocument.ActiveLayer.name
                    # if layer.kind == 2:  # 이 조건문 다는 순간 포토샵에서 마우스 커서가 오락가락하는 버그 같은 게....
                        # if (layername == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do"
                        # or ("레이어" in layername) or ("Layer" in layername)):
                        #     self.psTextLayerSignal.emit(True)
                        #     break
                    if (layername == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do" 
                    or match("^레이어 [0-9]+$", layername) or match("^Layer [0-9]+$", layername)):
                        self.psTextLayerSignal.emit(True)
                        break
                except:
                    pass
            except:
                self.psTextLayerSignal.emit(False)
                break
        pythoncom.CoUninitialize()
        # self.exit()
        self.quit()


class CheckBmkThread(QThread):
    """파일 불러오고 UI 적용 중 책갈피 체크 후 자동 스크롤 하는 스레드"""
    #  스레드로 안 돌려주면 버튼이 다 불러오기도 전에 책갈피 이동이 실행됨
    check_Bookmark = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.exec()

    def exec(self):
        while True:
            if self.parent.goBmkEdit.isEnabled():
                self.check_Bookmark.emit()
                break
        self.quit()


# 매크로 관련 클래스 모음 #########################################################
class MacroStartwithProcess:
    """매크로 멀티프로세스 클래스"""

    def __init__(self, macroList):
        macroListThread = []
        for i in range(len(macroList)):
            infolist = macroList[i].split('#&@&#')
            macroListThread.append(Thread(target=self.macroMultProc, args=(infolist, )))  # 프로세스 내에서 각 매크로 스레드 생성
            macroListThread[i].start()

    def macroMultProc(self, infolist):
        """매크로 실행 함수"""
        setKey = ''

        if infolist[1] != 'none':
            if infolist[2] != 'none':
                setKey = infolist[1] + '+' + infolist[2]
            else:
                setKey = infolist[1]

        if infolist[5] != '1':  # 활성화 여부 체크
            return

        while True:  # 조건 키 누를 때까지 대기
            try:
                if keyboard.is_pressed(setKey):
                    if infolist[3] != 'none':
                        if infolist[4] != 'none':
                            hotkey(infolist[3], infolist[4])
                        else:
                            press(infolist[3])
                    break
            except:
                pass

        while True:  # 조건 키 누른 후 뗄 때까지 대기
            try:
                if not keyboard.is_pressed(setKey):
                    break
            except:
                pass
        self.macroMultProc(infolist)    # 실행 후 다시 반복


class MacroSetDialog(QDialog):
    """매크로 설정 창 클래스"""

    def __init__(self, parent):
        super().__init__()
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
        self.setWindowIcon(QIcon(self.parent.SetMacroIcon))
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


class MacroAddDialog(QDialog):
    """매크로 추가 및 수정 창 클래스"""
    
    def __init__(self, parent, info):
        super().__init__()
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

        self.setWindowIcon(QIcon(self.parent.parent.SetMacroIcon))
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


class KeyReadDialog(QDialog):
    """키 읽어들이기 창 클래스"""

    def __init__(self, parent, i):
        super().__init__()
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # 닫기 버튼 비활성화
        self.parent = parent
        self.i = i
        self.check = False

        lbl = QLabel('원하는 키를 누르세요...')
        pbar = QProgressBar()
        pbar.setMaximum(0)  # 맥시멈 미니멈 둘 다 0으로 해주면 무한 로딩 연출 가능
        pbar.setMinimum(0)
        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(pbar)

        self.setLayout(vbox)
        self.setWindowTitle('키 입력')

        self.keyThread = KeyRead(self)
        self.keyThread.start()
        self.keyThread.keyReadSignal.connect(self.keyRead)

        self.setWindowIcon(QIcon(self.parent.parent.parent.SetMacroIcon))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 80, y + 50)
        self.exec()

    @pyqtSlot(str)
    def keyRead(self, key):
        """키 입력을 받아 표시하는 함수"""
        if self.i == 1:
            self.parent.btnC1.setText(key)
            self.parent.btnC2.setEnabled(True)
        if self.i == 2:
            self.parent.btnC2.setText(key)
        if self.i == 3:
            self.parent.btnA1.setText(key)
            self.parent.btnA2.setEnabled(True)
        if self.i == 4:
            self.parent.btnA2.setText(key)
        self.check = True
        self.close()

    def closeEvent(self, event):
        """키 읽어들이기 창 닫기 이벤트"""
        if self.check:
            if self.keyThread.isRunning():
                self.keyThread.terminate()
            event.accept()
        else:   # ESC키 버그 방지용
            event.ignore()


class KeyRead(QThread):
    """키 읽어들이기 스레드 클래스"""
    keyReadSignal = pyqtSignal(str)

    def run(self):
        self.exec()

    def exec(self):
        """입력된 키 받아오는 함수"""
        key = keyboard.read_key()
        self.keyReadSignal.emit(key)
        self.exit()
