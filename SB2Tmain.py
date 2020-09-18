import sys
import win32com.client
from os.path import basename, exists

from PyQt5.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QFileDialog,
    QDialog,
    QApplication,
    QWidget,
    QPushButton,
    QToolBar,
    QMainWindow,
    QAction,
    QLabel,
    QVBoxLayout,
    QStatusBar,
    QFontDialog,
    QScrollArea,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSettings, pyqtSlot

from pyautogui import hotkey, getWindowsWithTitle, getAllTitles
from clipboard import copy
from win32gui import SetForegroundWindow
from multiprocessing import Process, freeze_support
from re import match

from SB2Tclass import (
    TextLine,
    AdvSettingsDialog,
    TextFindDialog,
    TextChangeDialog,
    StartPsThread,
    MacroSetDialog,
    MacroStartwithProcess,
    CheckBmkThread
)


# =====================================메인 시작===================================
class MainApp(QMainWindow):
    """식붕이툴 메인 윈도우 창 클래스"""

    def __init__(self):
        super().__init__()
        # QMainWindow.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.settings = QSettings("RingNebula", "SB2Tool")
        self.font = QFont()
        self.toolbar = QToolBar("기본 툴바")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setObjectName("DefaultToolbar")  # 이거 안 하면 설정 저장에서 오류 뜸
        self.macroList = []
        self.notFirstStart = True
        # ===============================고급 설정 목록==============================
        self.exceptbrackets = 1
        self.exceptCurlybrackets = 0
        self.exceptSquarebrackets = 0
        self.exceptDQuotaion = 0
        self.exceptSQuotaion = 0
        self.pasteCtrlEnter = 0
        self.commentWithNumber = 0
        self.commentWithP = 0
        self.advSettingsList = []
        # =========================================================================
        try:
            self.notFirstStart = self.settings.value("NotFirstStart")
        except:
            self.notFirstStart = False
        if not self.notFirstStart:
            self.advSettingsList = [1, 0, 0, 0, 0, 0, 0, 0]
            self.macroList = []
            self.resize(300, 560)
            self.notFirstStart = True
            # print('first!')
        else:
            try:
                self.resize(self.settings.value("WindowSize"))
                self.move(self.settings.value("WindowPosition"))
                self.restoreState(self.settings.value("State"))
            except Exception as e:
                QMessageBox.warning(self, "오류", "UI 설정에 실패했습니다.\n" + str(e))
                self.resize(300, 560)
            try:
                self.macroList = self.settings.value("MacroList", [], str)
            except Exception as e:
                QMessageBox.warning(self, "오류", "매크로 설정을 불러오지 못했습니다.\n" + str(e))
                self.macroList = []
            try:
                self.advSettingsList = self.settings.value("AdvSettings", [], int)
                self.exceptbrackets = self.advSettingsList[0]
                self.exceptCurlybrackets = self.advSettingsList[1]
                self.exceptSquarebrackets = self.advSettingsList[2]
                self.exceptDQuotaion = self.advSettingsList[3]
                self.exceptSQuotaion = self.advSettingsList[4]
                self.pasteCtrlEnter = self.advSettingsList[5]
                self.commentWithNumber = self.advSettingsList[6]
                self.commentWithP = self.advSettingsList[7]
            except Exception as e:
                QMessageBox.warning(self, "오류", "고급 설정을 불러오지 못했습니다.\n" + str(e))
                self.advSettingsList = [1, 0, 0, 0, 0, 0, 0, 0]
            try:
                self.font = self.settings.value("LastFont")
            except Exception as e:
                QMessageBox.warning(self, "오류", "폰트 설정에 실패했습니다.\n" + str(e))
                self.font.setFamily("Malgun Gothic")

        self.initUI()

    def initUI(self):
        """초기 UI 설정 및 생성 함수"""
        # Switch ###############################################
        self.ProgramSettingOn = False

        # var ###############################################
        self.filepath = ''
        self.allString = ''
        self.saveCheck = False
        self.btn = []
        self.lineCnt = 0
        self.lineCntBack = -1
        self.macroListThread = []
        self.selectedProgram = getWindowsWithTitle('식붕이툴')
        self.selectedProgramTitle = '선택 안 함'
        self.recordOfPaste = []
        self.recordOfPasteIndex = -1
        self.recordOfBtn = []
        self.recordOfBtnIndex = -1
        self.psThreadfunc = StartPsThread(self)
        self.bookmark = -1
        self.bmkThread = CheckBmkThread(self)

        # icons ##############################################
        SB2ToolLogo = "icons/sbticon.png"
        OpenFolderIcon = "icons/open.png"
        ProgrmaSetIcon = "icons/setpro.png"
        self.FindIcon = "icons/find.png"
        AutoIcon = "icons/auto.png"
        PsIcon = "icons/psmode.png"
        # RecordIcon = "icons/record.png"
        self.AdvSetIcon = "icons/advset.png"
        self.SetMacroIcon = 'icons/setmacro.png'
        self.ChangeIcon = 'icons/change.png'
        ChgThrPntIcon = 'icons/chgthrpnt.png'
        MacroIcon = 'icons/macromode.png'
        bookmarkIcon = 'icons/bookmark.png'

        # ================================UI================================
        # 메뉴바 ##############################################
        self.openFile = QAction('열기(&O)', self)
        self.openFile.triggered.connect(self.showFileDialog)
        self.openFile.setShortcut('Ctrl+O')

        self.saveFile = QAction('저장(&S)', self)
        self.saveFile.triggered.connect(lambda: self.saveTextFile(self.filepath))
        self.saveFile.setShortcut('Ctrl+S')
        self.saveFile.setDisabled(True)

        self.saveNewFile = QAction('다른 이름으로 저장(&A)', self)
        self.saveNewFile.triggered.connect(self.saveFileDialog)
        self.saveNewFile.setShortcut('Ctrl+Shift+S')
        self.saveNewFile.setDisabled(True)

        self.resetFile = QAction('전체 초기화(&R)', self)
        self.resetFile.triggered.connect(self.resetAllEvent)
        self.resetFile.setShortcut('Ctrl+R')

        self.closeTool = QAction('종료(&X)', self)
        self.closeTool.triggered.connect(self.close)
        self.closeTool.setShortcut('Alt+F4')

        self.setProgram = QAction('프로그램 지정(&P)', self)
        self.setProgram.triggered.connect(self.setProgramForPaste)
        self.setProgram.setShortcut('Ctrl+P')

        self.setMacro = QAction('매크로 설정(&M)', self)
        self.setMacro.triggered.connect(self.setMacroDialog)
        self.setMacro.setShortcut('Ctrl+M')
        self.macroSettingsWindow = QDialog(self)

        self.changeFont = QAction('글꼴(&F)', self)
        self.changeFont.triggered.connect(self.showFontDialog)
        self.changeFont.setDisabled(True)

        self.advSettings = QAction('고급 설정(&A)', self)
        self.advSettings.triggered.connect(self.advSettingsDialogShow)
        self.advSettings.setShortcut('F2')
        self.advSettingsWindow = QDialog(self)

        self.startMode = QAction('자동 모드(&S)', self)
        self.startMode.setCheckable(True)
        self.startMode.triggered.connect(self.autoStartByMenu)
        self.startMode.setShortcut('F5')
        self.startMode.setDisabled(True)

        self.psMode = QAction('포토샵 모드(&P)', self)
        self.psMode.setCheckable(True)
        self.psMode.triggered.connect(self.psAutoStartByMenu)
        self.psMode.setShortcut('F6')
        self.psMode.setDisabled(True)

        self.macroMode = QAction('매크로 모드(&M)', self)
        self.macroMode.setCheckable(True)
        self.macroMode.triggered.connect(self.macroStartByMenu)
        self.macroMode.setShortcut('F7')

        self.resetRecord = QAction('기록 초기화(&Q)', self)
        self.resetRecord.triggered.connect(self.resetAllRecord)
        self.resetRecord.setShortcut('Del')
        self.resetRecord.setDisabled(True)

        self.fiveUpEdit = QAction('다섯 줄 위로 건너뛰기(&Z)', self)
        self.fiveUpEdit.triggered.connect(self.selUpFiveLine)
        self.fiveUpEdit.setShortcut('Ctrl+A')
        self.fiveUpEdit.setDisabled(True)

        self.oneUpEdit = QAction('한 줄 위로 건너뛰기(&X)', self)
        self.oneUpEdit.triggered.connect(self.selUpOneLine)
        self.oneUpEdit.setShortcut('A')
        self.oneUpEdit.setDisabled(True)

        self.oneDownEdit = QAction('한 줄 아래로 건너뛰기(&V)', self)
        self.oneDownEdit.triggered.connect(self.selDownOneLine)
        self.oneDownEdit.setShortcut('D')
        self.oneDownEdit.setDisabled(True)

        self.fiveDownEdit = QAction('다섯 줄 아래로 건너뛰기(&B)', self)
        self.fiveDownEdit.triggered.connect(self.selDownFiveLine)
        self.fiveDownEdit.setShortcut('Ctrl+D')
        self.fiveDownEdit.setDisabled(True)

        self.pasteEdit = QAction('붙여넣기(&C)', self)
        self.pasteEdit.triggered.connect(self.pasteLine)
        self.pasteEdit.setShortcut('S')
        self.pasteEdit.setDisabled(True)

        self.findEdit = QAction('찾기(&F)', self)
        self.findEdit.triggered.connect(self.textFind)
        self.findEdit.setShortcut('Ctrl+F')
        self.findEdit.setDisabled(True)

        self.changeEdit = QAction('바꾸기(&H)', self)
        self.changeEdit.triggered.connect(self.textChange)
        self.changeEdit.setShortcut('Ctrl+H')
        self.changeEdit.setDisabled(True)

        self.chgTPEdit = QAction('아래점 바꾸기(&T)', self)
        self.chgTPEdit.triggered.connect(self.changeThreePoint)
        self.chgTPEdit.setDisabled(True)

        self.goBmkEdit = QAction('책갈피로 이동(&B)', self)
        self.goBmkEdit.triggered.connect(self.goToBookmark)
        self.goBmkEdit.setShortcut('Ctrl+B')
        self.goBmkEdit.setDisabled(True)

        self.undoEdit = QAction('바꾸기 취소(&U)')
        self.undoEdit.triggered.connect(self.undoChange)
        self.undoEdit.setShortcut('Ctrl+Z')
        self.undoEdit.setDisabled(True)

        self.redoEdit = QAction('바꾸기 다시 실행(&R)')
        self.redoEdit.triggered.connect(self.redoChange)
        self.redoEdit.setShortcut('Ctrl+X')
        self.redoEdit.setDisabled(True)

        self.thrpntEdit = QAction("줄임표 '…' 복사(&1)")
        self.thrpntEdit.triggered.connect(self.pasteThreePoint)

        self.hlineEdit = QAction("가로 줄표 '─' 복사(&2)")
        self.hlineEdit.triggered.connect(self.pasteLongHLine)

        self.vlineEdit = QAction("세로 줄표 '│' 복사(&3)")
        self.vlineEdit.triggered.connect(self.pasteLongVLine)

        self.litqtnEdit = QAction("홑낫표 '「」' 복사(&4)")
        self.litqtnEdit.triggered.connect(self.pasteLittleJPquotaions)

        self.bigqtnEdit = QAction("겹낫표 '『』' 복사(&5)")
        self.bigqtnEdit.triggered.connect(self.pasteBigJPquotaions)

        self.tutorial = QAction('매뉴얼(&M)', self)
        self.tutorial.setShortcut('F1')
        self.tutorial.triggered.connect(self.tutorialLink)

        self.information = QAction('정보(&I)', self)
        self.information.triggered.connect(self.informationCheck)

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        self.fileMenu = self.menubar.addMenu('파일(&F)')
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.saveFile)
        self.fileMenu.addAction(self.saveNewFile)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.resetFile)
        self.fileMenu.addAction(self.closeTool)

        self.configMenu = self.menubar.addMenu('설정(&S)')
        self.configMenu.addAction(self.setProgram)
        self.configMenu.addAction(self.setMacro)
        self.configMenu.addAction(self.changeFont)
        self.configMenu.addSeparator()
        self.configMenu.addAction(self.advSettings)

        self.modeMenu = self.menubar.addMenu('모드(&M)')
        self.modeMenu.addAction(self.startMode)
        self.modeMenu.addAction(self.psMode)
        self.modeMenu.addAction(self.macroMode)

        self.editMenu = self.menubar.addMenu('편집(&E)')
        self.editMenu.addAction(self.pasteEdit)
        self.editMenu.addAction(self.resetRecord)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.fiveUpEdit)
        self.editMenu.addAction(self.oneUpEdit)
        self.editMenu.addAction(self.oneDownEdit)
        self.editMenu.addAction(self.fiveDownEdit)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.goBmkEdit)
        self.editMenu.addAction(self.findEdit)
        self.editMenu.addAction(self.changeEdit)
        self.editMenu.addAction(self.chgTPEdit)
        self.editMenu.addAction(self.undoEdit)
        self.editMenu.addAction(self.redoEdit)
        self.editMenu.addSeparator()

        self.symbolMenu = self.editMenu.addMenu('특수 문자 복사(&P)')
        self.symbolMenu.addAction(self.thrpntEdit)
        self.symbolMenu.addAction(self.hlineEdit)
        self.symbolMenu.addAction(self.vlineEdit)
        self.symbolMenu.addAction(self.litqtnEdit)
        self.symbolMenu.addAction(self.bigqtnEdit)

        self.helpMenu = self.menubar.addMenu('도움말(&H)')
        self.helpMenu.addAction(self.tutorial)
        self.helpMenu.addAction(self.information)

        # 툴바 ##############################################
        self.fileOpenAction = QAction(QIcon(OpenFolderIcon), 'FileOpen', self)
        self.fileOpenAction.setToolTip(
            '파일 열기 ( Ctrl+O )\n복사를 진행할 텍스트 파일을 불러옵니다.')
        self.fileOpenAction.triggered.connect(self.showFileDialog)

        self.setProgramForPasteAction = QAction(
            QIcon(ProgrmaSetIcon), 'ProgramSetting', self)
        self.setProgramForPasteAction.setToolTip(
            '프로그램 세팅 ( Ctrl+P )\n붙여넣기를 진행할 프로그램을 지정합니다.')
        self.setProgramForPasteAction.triggered.connect(self.setProgramForPaste)

        self.setMacroAction = QAction(QIcon(self.SetMacroIcon), 'setMacro', self)
        self.setMacroAction.setToolTip('매크로 설정 ( Ctrl+M )\n키보드 매크로를 설정합니다.')
        self.setMacroAction.triggered.connect(self.setMacroDialog)

        self.autoStartAction = QAction(QIcon(AutoIcon), 'AutoMode', self)
        self.autoStartAction.setToolTip(
            '자동 모드 ( F5 )\n원하는 텍스트를 클릭 시 자동으로\n지정된 프로그램에 붙여넣는 모드입니다.')
        self.autoStartAction.triggered.connect(self.autoStartByToolbar)
        self.autoStartAction.setCheckable(True)
        self.autoStartAction.setDisabled(True)

        self.psAutoStartAction = QAction(QIcon(PsIcon), 'PSMode', self)
        self.psAutoStartAction.setToolTip(
            '포토샵 모드 (F6)\n포토샵 전용 붙여넣기 모드로,\n텍스트 레이어 생성 시 자동으로 붙여넣는 모드입니다.')
        self.psAutoStartAction.triggered.connect(self.psAutoStartByToolbar)
        self.psAutoStartAction.setCheckable(True)
        self.psAutoStartAction.setDisabled(True)

        self.macroStartAction = QAction(QIcon(MacroIcon), 'Macro', self)
        self.macroStartAction.setToolTip('매크로 모드 (F7)\n키보드 매크로 기능을 실행합니다.')
        self.macroStartAction.triggered.connect(self.macroStartByToolbar)
        self.macroStartAction.setCheckable(True)

        # self.resetRecordAction = QAction(QIcon(RecordIcon), 'ResetRecord', self)
        # self.resetRecordAction.setToolTip('기록 초기화 (Del)\n붙여넣기 기록을 모두 초기화합니다.')
        # self.resetRecordAction.triggered.connect(self.resetAllRecord)
        # self.resetRecordAction.setDisabled(True)

        self.textFindAction = QAction(QIcon(self.FindIcon), 'TextFind', self)
        self.textFindAction.setToolTip('찾기 ( Ctrl+F )\n특정 텍스트를 검색하여 복사합니다.')
        self.textFindAction.triggered.connect(self.textFind)
        self.textFindAction.setDisabled(True)
        self.textfindwindow = QDialog(self)

        self.textChangeAction = QAction(QIcon(self.ChangeIcon), 'TextChange', self)
        self.textChangeAction.setToolTip(
            '바꾸기 ( Ctrl+H )\n특정 텍스트를 찾아 원하는 텍스트로 바꿉니다.')
        self.textChangeAction.triggered.connect(self.textChange)
        self.textChangeAction.setDisabled(True)
        self.textchangewindow = QDialog(self)

        self.threePointChangeAction = QAction(
            QIcon(ChgThrPntIcon), 'ThreePointChange', self)
        self.threePointChangeAction.setToolTip(
            '아래점 바꾸기\n아래점 세 개를 줄임표로 전부 바꿉니다.')
        self.threePointChangeAction.triggered.connect(self.changeThreePoint)
        self.threePointChangeAction.setDisabled(True)

        self.goBookmarkAction = QAction(
            QIcon(bookmarkIcon), 'GotoBookmark', self)
        self.goBookmarkAction.setToolTip(
            '책갈피 이동 ( Ctrl+B )\n책갈피가 있는 줄로 이동합니다.')
        self.goBookmarkAction.triggered.connect(self.goToBookmark)
        self.goBookmarkAction.setDisabled(True)

        self.pasteThreePointAction = QPushButton("…", self)
        self.pasteThreePointAction.setToolTip(
            "줄임표 '…' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        self.pasteThreePointAction.clicked.connect(self.pasteThreePoint)
        self.pasteThreePointAction.setFixedSize(30, 30)

        self.pasteLongHLineAction = QPushButton('─', self)
        self.pasteLongHLineAction.setToolTip(
            "가로 줄표 '─' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        self.pasteLongHLineAction.clicked.connect(self.pasteLongHLine)
        self.pasteLongHLineAction.setFixedSize(30, 30)

        self.pasteLongVLineAction = QPushButton('│', self)
        self.pasteLongVLineAction.setToolTip(
            "세로 줄표 '│' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        self.pasteLongVLineAction.clicked.connect(self.pasteLongVLine)
        self.pasteLongVLineAction.setFixedSize(30, 30)

        self.pasteBigJPquotaionsAction = QPushButton('『』', self)
        self.pasteBigJPquotaionsAction.setToolTip(
            "겹낫표 '『』' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        self.pasteBigJPquotaionsAction.clicked.connect(self.pasteBigJPquotaions)
        self.pasteBigJPquotaionsAction.setFixedSize(30, 30)

        self.pasteLittleJPquotaionsAction = QPushButton('「」', self)
        self.pasteLittleJPquotaionsAction.setToolTip(
            "홑낫표 '「」' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        self.pasteLittleJPquotaionsAction.clicked.connect(self.pasteLittleJPquotaions)
        self.pasteLittleJPquotaionsAction.setFixedSize(30, 30)

        self.toolbar.addAction(self.fileOpenAction)
        self.toolbar.addAction(self.setProgramForPasteAction)
        self.toolbar.addAction(self.setMacroAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.autoStartAction)
        self.toolbar.addAction(self.psAutoStartAction)
        self.toolbar.addAction(self.macroStartAction)
        self.toolbar.addSeparator()
        # self.toolbar.addAction(self.resetRecordAction)
        self.toolbar.addAction(self.goBookmarkAction)
        self.toolbar.addAction(self.textFindAction)
        self.toolbar.addAction(self.textChangeAction)
        self.toolbar.addAction(self.threePointChangeAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.pasteThreePointAction)
        self.toolbar.addWidget(self.pasteLongHLineAction)
        self.toolbar.addWidget(self.pasteLongVLineAction)
        self.toolbar.addWidget(self.pasteLittleJPquotaionsAction)
        self.toolbar.addWidget(self.pasteBigJPquotaionsAction)

        self.setScrollArea()

        # 스테이터스 바 #####################################################
        self.forVLine = QLabel("")
        self.lineStatus = QLabel(" 줄  ")
        self.setProgramStatus = QLabel(" 지정: 선택 안 함 ")
        self.statusbarmain = QStatusBar(self)
        self.setStatusBar(self.statusbarmain)
        self.statusbarmain.addPermanentWidget(self.forVLine)
        self.statusbarmain.addPermanentWidget(self.lineStatus)
        self.statusbarmain.addPermanentWidget(self.setProgramStatus)

        # 프로그램 프로필 ###################################################
        self.setWindowTitle('식붕이툴 Beta')
        self.setWindowIcon(QIcon(SB2ToolLogo))
        self.show()

    # UI functions ######################################################
    def setScrollArea(self):
        """ScrollArea 영역 초기화하는 함수"""
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)  # 여백 없애기 1
        self.vbox.setSpacing(0)  # 여백 없애기 2
        self.widget.setLayout(self.vbox)

        self.scroll = QScrollArea()
        self.setStyleSheet(
            "QScrollArea {border: none;}")  # 스타일 이슈가 있음. 명확한 규명은 추후에...
        self.hbar = self.scroll.horizontalScrollBar()
        self.setCentralWidget(self.scroll)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """드래그 삽입 이벤트 관련 함수"""
        data = event.mimeData()
        urls = data.urls()
        if self.fileOpenAction.isEnabled():
            if urls and urls[0].scheme() == 'file':
                filepath = str(urls[0].path())[1:]
                fileext = filepath[-4:].upper()
                if fileext == ".txt" or fileext == ".TXT":
                    event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """드래그 이동 이벤트 관련 함수"""
        data = event.mimeData()
        urls = data.urls()
        if self.fileOpenAction.isEnabled():
            if urls and urls[0].scheme() == 'file':
                filepath = str(urls[0].path())[1:]
                fileext = filepath[-4:].upper()
                if fileext == ".txt" or fileext == ".TXT":
                    event.acceptProposedAction()

    def dropEvent(self, event):
        """드래그 이벤트 실행 함수"""
        data = event.mimeData()
        urls = data.urls()
        if self.fileOpenAction.isEnabled():
            if urls and urls[0].scheme() == 'file':
                filepath = str(urls[0].path())[1:]
                fileext = filepath[-4:].upper()
                if fileext == ".txt" or fileext == ".TXT":
                    self.openTextFile(filepath)

    def showFontDialog(self):
        """폰트 설정 창 생성 함수"""
        tempfont, ok = QFontDialog.getFont()
        if ok:
            self.font = tempfont
            for i in range(len(self.btn)):
                self.btn[i].setFont(self.font)

    def showFileDialog(self):
        """텍스트 파일 열기 창 생성 함수"""
        self.textfindwindow.close()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('텍스트 파일 열기')
        dialog.setNameFilter('텍스트 파일 (*.txt);;모든 파일 (*)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            fname = dialog.selectedFiles()
            self.openTextFile(fname[0])

    def saveFileDialog(self):
        """텍스트 파일 저장 창 생성 함수"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "다른 이름으로 저장", self.filepath,
            "텍스트 파일 (*.txt);;모든 파일 (*)", options=options)
        if fileName:
            self.saveTextFile(fileName)

    def saveTextFile(self, path):
        """텍스트 파일 저장하는 함수"""
        temp1 = self.allString.splitlines()
        temp2 = self.recordOfBtn[self.recordOfBtnIndex]

        idx = 0
        for i in range(len(temp1)):  # 수정된 텍스트로 교체
            if temp1[i] != '':
                temp1[i] = temp2[idx][1]
                idx += 1
            else:
                pass
        txt = '\n'.join(temp1)

        f = open(path, 'w', encoding='UTF8')    # 기본 UTF8로 저장
        f.write(txt)
        f.close()
        self.statusbarmain.showMessage('저장 완료', 5000)
        self.saveCheck = False
        self.saveFile.setDisabled(True)
        self.saveNewFile.setDisabled(True)
        self.filepath = path
        self.setWindowTitle(basename(path) + ' - 식붕이툴 1.0v')

    def openTextFile(self, path):
        """텍스트 파일 열기 관련 함수"""
        try:  # ANSI로 우선 불러오기
            with open(path, 'r') as f:
                data = f.read()
                filepath = f.name
            self.setStatusAfterOpenTxt(data, filepath)
        except:  # ANSI가 아니면 UTF-8로 불러오기
            try:
                with open(path, 'r', encoding='UTF8') as f:
                    data = f.read()
                    filepath = f.name
                self.setStatusAfterOpenTxt(data, filepath)
            except Exception as e:
                QMessageBox.warning(self, "파일 불러오기 오류",
                "파일을 불러오지 못했습니다.\n" + str(e))

    def setStatusAfterOpenTxt(self, data, path):
        """파일 불러온 뒤 임시 초기화하는 함수"""
        self.allString = data
        self.filepath = path
        self.psAutoStartAction.setDisabled(True)
        self.psMode.setDisabled(True)
        self.autoStartAction.setDisabled(True)
        self.startMode.setDisabled(True)
        self.textFindAction.setDisabled(True)
        self.textChangeAction.setDisabled(True)
        self.threePointChangeAction.setDisabled(True)
        self.findEdit.setDisabled(True)
        self.changeEdit.setDisabled(True)
        self.chgTPEdit.setDisabled(True)
        self.fiveUpEdit.setDisabled(True)
        self.oneUpEdit.setDisabled(True)
        self.oneDownEdit.setDisabled(True)
        self.fiveDownEdit.setDisabled(True)
        self.changeFont.setDisabled(True)
        self.textfindwindow.close()
        self.textchangewindow.close()
        self.setScrollArea()
        self.btn.clear()
        self.recordOfBtn.clear()
        self.recordOfBtnIndex = -1
        self.bookmark = -1
        self.goBmkEdit.setDisabled(True)
        self.goBookmarkAction.setDisabled(True)
        self.saveCheck = False
        self.saveFile.setDisabled(True)
        self.saveNewFile.setDisabled(True)
        self.resetAllRecord()

        self.setWindowTitle(basename(self.filepath) + ' - 식붕이툴 1.0v')
        self.linetext = data.splitlines()
        self.linelen = len(self.linetext)
        self.setBtnsForText()

    def setBtnsForText(self):
        """불러온 텍스트 파일을 기반으로 scroll area 채우는 함수"""
        backup = []
        # linenum = 0
        connectnum = -1  # -1:X, 0:머리, 1:중간, 2:꼬리
        head = -1
        for i in range(self.linelen):
            if self.linetext[i] != '':
                linenum = len(self.btn)
                if self.linetext[i][0] == "/" or self.linetext[i][0] == '`':
                    mode = 0    # 주석
                else:
                    mode = 1    # 기본 버튼

                if self.commentWithNumber:
                    if match("\d", self.linetext[i][0]):
                        mode = 0
                if self.commentWithP:
                    if match("[Pp]", self.linetext[i][0]):
                        mode = 0

                if i + 1 < self.linelen:
                    if connectnum == -1:
                        if self.linetext[i + 1] != '':
                            connectnum = 0
                            head = linenum
                    elif connectnum == 0:
                        if self.linetext[i + 1] != '':
                            connectnum = 1
                        else:
                            connectnum = 2
                    elif connectnum == 1:
                        if self.linetext[i + 1] != '':
                            connectnum == 1
                        else:
                            connectnum = 2
                else:
                    if connectnum != -1:
                        connectnum = 2

                self.btn.append(TextLine(self, linenum, mode, self.linetext[i], connectnum, head))
                backup.append((mode, self.linetext[i]))
                try:
                    self.btn[linenum].setFont(self.font)
                except:
                    pass
                self.vbox.addWidget(self.btn[linenum])
                # linenum += 1
            else:
                connectnum = -1
                head = -1

        self.recordOfBtn.append(backup)
        self.recordOfBtnIndex = 0
        self.setToolMenuAfterSetBtns()

    def setToolMenuAfterSetBtns(self):
        """버튼 배열로 scroll area 채우기 이후, 메뉴바와 툴바 세팅하는 함수"""
        if len(self.btn) > 0:
            self.fiveUpEdit.setEnabled(True)
            self.oneUpEdit.setEnabled(True)
            self.fiveDownEdit.setEnabled(True)
            self.oneDownEdit.setEnabled(True)
            self.textFindAction.setEnabled(True)
            self.textChangeAction.setEnabled(True)
            self.threePointChangeAction.setEnabled(True)
            self.findEdit.setEnabled(True)
            self.changeEdit.setEnabled(True)
            self.chgTPEdit.setEnabled(True)
            self.changeFont.setEnabled(True)
            self.statusbarmain.showMessage("")
            if self.ProgramSettingOn:
                self.autoStartAction.setEnabled(True)
                self.startMode.setEnabled(True)
                self.checkPhotoshop()
            self.checkBookmark()
        else:   # 버튼이 하나도 없을 때는 세팅 ㄴㄴ
            self.statusbarmain.showMessage("빈 텍스트입니다.")

    def checkBookmark(self):
        """책갈피 유무 체크하는 함수"""
        fname = self.filepath + '.bmk'
        if exists(fname):
            try:
                with open(fname, 'r') as f:
                    self.bookmark = int(f.readline())
                self.btn[self.bookmark].setIcon(QIcon('icons/bookmark.png'))
                self.goBmkEdit.setEnabled(True)
                self.goBookmarkAction.setEnabled(True)
                self.bmkThread.start()
                self.bmkThread.check_Bookmark.connect(self.goToBookmark)
            except Exception as e:
                QMessageBox.warning(self, "오류", "책갈피를 불러오지 못했습니다.\n" + str(e))

    def setProgramForPaste(self):
        """붙여넣기를 진행할 프로그램을 지정하는 함수"""
        titles = []
        filteredTitles = []
        temp = getAllTitles()

        temp = list(filter(lambda a: a != '', temp))  # 타이틀이 없는 정체불명인 것들이 많아서 일단 다 걸러줌

        for i in temp:    # 식붕이툴을 목록에서 지우기 위한 반복문
            if '식붕이툴' in i:
                pass
            else:
                titles.append(i)

        for j in titles:    # 이전에 지정해 놓은 프로그램 검사
            self.selectedProgramTitle = '선택 안 함'
            try:
                if getWindowsWithTitle(j)[0] == self.selectedProgram:
                    self.selectedProgramTitle = j
                    break
            except:
                QMessageBox.warning(self, "프로그램 지정 오류",
                "프로그램 목록 생성에 실패했습니다.\n다시 시도해 주세요.")
        filteredTitles.append(self.selectedProgramTitle)

        for k in titles:    # 이 부분에서 정제된 목록이 완성
            if self.selectedProgramTitle in k:
                pass
            else:
                filteredTitles.append(k)
        items = tuple(filteredTitles)
        item, ok = QInputDialog.getItem(
            self, "프로그램 지정", "아래 목록에서 붙여넣기를 진행할 프로그램을 선택하세요.",
            items, 0, False)

        if ok and item:
            self.selectedProgramTitle = item
            if len(item) > 15:  # 너무 길면 뒤에 ...으로 처리
                self.setProgramStatus.setText(" 지정: " + item[:15] + '... ')
            else:
                self.setProgramStatus.setText(" 지정: " + item + ' ')

            if item == '선택 안 함':
                self.ProgramSettingOn = False
                self.autoStartAction.setDisabled(True)
                self.startMode.setDisabled(True)
            else:
                self.ProgramSettingOn = True
                if len(self.btn) != 0:
                    self.autoStartAction.setEnabled(True)
                    self.startMode.setEnabled(True)
                    self.checkPhotoshop()
                try:
                    self.selectedProgram = getWindowsWithTitle(item)[0]
                except:
                    self.resetForProgramError()
                self.statusbarmain.showMessage("프로그램 지정 완료", 5000)

    def advSettingsDialogShow(self):
        """고급 설정 창 생성 함수"""
        self.advSettingsWindow = AdvSettingsDialog(self)

    def checkPhotoshop(self):
        """지정된 프로그램이 포토샵인지 확인하는 함수"""
        self.psAutoStartAction.setDisabled(True)
        self.psMode.setDisabled(True)

        # check = False
        try:
            temp = win32com.client.GetActiveObject("Photoshop.Application")  # 포토샵 앱 불러오기
            self.psAutoStartAction.setEnabled(True)
            self.psMode.setEnabled(True)
            # 여러 변수를 고려하여 포토샵이 실행만 되어 있으면 활성화되는 것으로 변경
            # if "Photoshop" in self.selectedProgramTitle:
            #     check = True
            # else:
            #     try:
            #         docname = temp.Application.ActiveDocument.name
            #         if docname in self.selectedProgramTitle:
            #             check = True
            #         else:
            #             try:
            #                 layername = temp.Application.ActiveDocument.ActiveLayer.name
            #                 if layername in self.selectedProgramTitle:
            #                     check = True
            #             except:
            #                 QMessageBox.warning(self, "포토샵 모드 오류",
            #                 "레이어를 닫은 다음에\n다시 지정해 주세요.")
            #     except:
            #         QMessageBox.warning(self, "포토샵 모드 오류",
            #         "레이어를 닫은 다음에\n다시 지정해 주세요.")
        except Exception as e:
            QMessageBox.warning(self, "포토샵 모드 오류", str(e))
            self.psAutoStartAction.setDisabled(True)
            self.psMode.setDisabled(True)

        # if check:
        #     self.psAutoStartAction.setEnabled(True)
        #     self.psMode.setEnabled(True)
        # else:
        #     self.psAutoStartAction.setDisabled(True)
        #     self.psMode.setDisabled(True)

    # main functions #########################################################
    def goToBookmark(self):
        """책갈피가 있는 줄로 스크롤되는 함수"""
        if self.btn[self.bookmark].mode:
            self.btn[self.bookmark].copyText()
        else:
            self.btn[self.bookmark].autoScroll(self.bookmark)
            self.hbar.setValue(self.hbar.minimum())
        self.statusbarmain.showMessage("책갈피로 이동합니다.", 5000)

        if self.bmkThread.isRunning():
            self.bmkThread.terminate()

    def autoStartByMenu(self):
        """메뉴에서 자동 모드를 켤 때 거쳐가는 함수"""
        self.autoStartAction.toggle()
        self.autoStart()

    def autoStartByToolbar(self):
        """툴바에서 자동 모드를 켤 때 거쳐가는 함수"""
        self.startMode.toggle()
        self.autoStart()

    def autoStart(self):
        """자동 모드 시작 함수"""
        if self.autoStartAction.isChecked():
            self.setProgramForPasteAction.setDisabled(True)
            self.setProgram.setDisabled(True)
            self.fileOpenAction.setDisabled(True)
            self.openFile.setDisabled(True)
            self.statusbarmain.showMessage("자동 모드 On")
        else:
            if not self.psAutoStartAction.isChecked():
                self.setProgramForPasteAction.setEnabled(True)
                self.setProgram.setEnabled(True)
                self.fileOpenAction.setEnabled(True)
                self.openFile.setEnabled(True)
            self.statusbarmain.showMessage("자동 모드 Off", 5000)

    def psAutoStartByMenu(self):
        """메뉴에서 포토샵 모드를 켤 때 거쳐가는 함수"""
        self.psAutoStartAction.toggle()
        self.psAutoStart()

    def psAutoStartByToolbar(self):
        """툴바에서 포토샵 모드를 켤 때 거쳐가는 함수"""
        self.psMode.toggle()
        self.psAutoStart()

    def psAutoStart(self):
        """포토샵 모드 시작 함수"""
        if self.psThreadfunc.isRunning():   # 스레드 체크
            self.psThreadfunc.terminate()
        if self.psAutoStartAction.isChecked():
            self.setProgramForPasteAction.setDisabled(True)
            self.setProgram.setDisabled(True)
            self.fileOpenAction.setDisabled(True)
            self.openFile.setDisabled(True)
            self.statusbarmain.showMessage("포토샵 모드 On")

            self.psAutoThreadStart()
        else:
            if not self.autoStartAction.isChecked():
                self.setProgramForPasteAction.setEnabled(True)
                self.setProgram.setEnabled(True)
                self.fileOpenAction.setEnabled(True)
                self.openFile.setEnabled(True)
            self.statusbarmain.showMessage("포토샵 모드 Off", 5000)

    def psAutoThreadStart(self):
        """포토샵 모드 스레드 시작 함수"""
        if self.psThreadfunc.isRunning():  # 스레드 체크
            self.psThreadfunc.terminate()
        self.psThreadfunc = StartPsThread(self)  # 스레드 클래스 생성
        self.psThreadfunc.start()
        self.psThreadfunc.psTextLayerSignal.connect(self.psPaste)

    @pyqtSlot(bool)
    def psPaste(self, boolean):
        """포토샵 모드 붙여넣기 실행 함수"""
        if self.lineCnt == 0:  # 첫 번째 텍스트 라인 모드 체크
            self.lineCnt = self.nextNumOfBtnMode(0)

        try:
            if boolean:
                self.btn[self.lineCnt].copyText()
                self.btn[self.lineCnt].pasteTextPSMode()
            else:
                self.resetForProgramError()
        except:
            self.psAutoStartAction.toggle()
            self.psMode.toggle()
            self.psAutoStart()
            self.statusbarmain.showMessage("마지막 텍스트를 붙여넣었습니다!", 5000)

    def nextNumOfBtnMode(self, n) -> int:
        """다음 기본 모드 텍스트 라인의 인덱스를 반환하는 함수"""
        try: 
            if self.btn[n].mode:
                return n
            else:
                return self.nextNumOfBtnMode(n + 1)
        except:
            return -1  # 마지막 줄이었단 뜻

    def nextLineCopy(self):
        """다음 텍스트 라인 복사하기 (기본 버튼 모드만 적용)"""
        temp = self.nextNumOfBtnMode(self.lineCnt + 1)
        if temp == -1:  # 마지막 텍스트 라인 복붙했을 때 자동으로 PS 모드 종료
            self.psAutoStartAction.toggle()
            self.psMode.toggle()
            self.psAutoStart()
            self.statusbarmain.showMessage("마지막 텍스트를 붙여넣었습니다!", 5000)
        else:
            self.btn[temp].copyText()

    def setMacroDialog(self):
        """매크로 설정 창 생성 함수"""
        self.macroSettingsWindow = MacroSetDialog(self)

    def macroStartByToolbar(self):
        """툴바에서 매크로 모드를 켤 때 거쳐가는 함수"""
        self.macroMode.toggle()
        self.macroStart()

    def macroStartByMenu(self):
        """메뉴에서 매크로 모드를 켤 때 거쳐가는 함수"""
        self.macroStartAction.toggle()
        self.macroStart()

    def macroStart(self):
        """매크로 모드 시작 함수"""
        if len(self.macroListThread) > 0:
            for i in self.macroListThread:
                i.terminate()
                i.join()

        self.macroListThread.clear()
        if self.macroStartAction.isChecked():
            self.setMacro.setDisabled(True)
            self.setMacroAction.setDisabled(True)
            self.statusbarmain.showMessage("매크로 기능 On", 5000)
            self.macroThreadStart()
        else:
            self.setMacro.setEnabled(True)
            self.setMacroAction.setEnabled(True)
            self.statusbarmain.showMessage("매크로 기능 Off", 5000)

    def macroThreadStart(self):
        """매크로 프로세싱 시작 함수"""
        self.macroListThread.append(
            Process(target=MacroStartwithProcess, args=(self.macroList, )))
        self.macroListThread[0].start()

    def resetAllRecord(self):
        """붙여넣기 흔적을 초기화하는 함수"""
        self.lineCnt = 0
        self.lineCntBack = -1
        self.lineStatus.setText(" 줄  ")
        self.pasteEdit.setDisabled(True)
        # self.resetRecordAction.setDisabled(True)
        self.resetRecord.setDisabled(True)

        for i in self.btn:  # 버튼 토글 초기화
            i.pasted = 0
            i.setLine()

    def changeBackup(self) -> list:
        """현재 텍스트 상태를 백업하는 함수"""
        temp = []
        for i in self.btn:
            temp.append((i.mode, i.txt))
        return temp

    def recordChange(self):
        """텍스트 변경을 기록하는 함수"""
        backup = self.changeBackup()
        if self.recordOfBtnIndex < len(self.recordOfBtn) - 1:
            self.recordOfBtn[self.recordOfBtnIndex + 1] = backup
            del self.recordOfBtn[self.recordOfBtnIndex + 2:]
        else:
            self.recordOfBtn.append(backup)
        self.recordOfBtnIndex += 1
        self.redoEdit.setDisabled(True)
        self.undoEdit.setEnabled(True)
        if len(self.recordOfBtn) > 100:  # 최대 기록 개수는 100개
            self.recordOfBtn.pop(0)
            self.recordOfBtnIndex -= 1

        self.checkSameOfAllString()

    def checkSameOfAllString(self):
        """텍스트 수정 여부 체크하는 함수"""
        temp1 = self.allString.splitlines()
        temp1 = list(filter(lambda a: a != '', temp1))
        temp2 = self.recordOfBtn[self.recordOfBtnIndex]

        self.saveCheck = False
        for i in range(len(temp1)):
            if temp1[i] != temp2[i][1]:
                self.saveCheck = True
                break
        if self.saveCheck:
            self.setWindowTitle('*' + basename(self.filepath) + ' - 식붕이툴 1.0v')
            self.saveFile.setEnabled(True)
            self.saveNewFile.setEnabled(True)
        else:
            self.setWindowTitle(basename(self.filepath) + ' - 식붕이툴 1.0v')
            self.saveFile.setDisabled(True)
            self.saveNewFile.setDisabled(True)

    def undoChange(self):
        """바꾸기 되돌리기 함수"""
        self.recordOfBtnIndex -= 1
        temp = self.recordOfBtn[self.recordOfBtnIndex]
        for i in range(len(self.btn)):
            self.btn[i].mode = temp[i][0]
            self.btn[i].txt = temp[i][1]
            self.btn[i].setLine()

        self.redoEdit.setEnabled(True)
        if self.recordOfBtnIndex < 1:
            self.undoEdit.setDisabled(True)

        self.checkSameOfAllString()

    def redoChange(self):
        """바꾸기 다시 실행하기 함수"""
        self.recordOfBtnIndex += 1
        temp = self.recordOfBtn[self.recordOfBtnIndex]
        for i in range(len(self.btn)):
            self.btn[i].mode = temp[i][0]
            self.btn[i].txt = temp[i][1]
            self.btn[i].setLine()

        self.undoEdit.setEnabled(True)
        if self.recordOfBtnIndex == len(self.recordOfBtn) - 1:
            self.redoEdit.setDisabled(True)

        self.checkSameOfAllString()

    def selUpFiveLine(self):
        """다섯 줄 위 텍스트 선택하는 함수"""
        temp = self.lineCnt - 5
        if temp < 0:
            self.btn[len(self.btn) + temp].copyText()
        else:
            self.btn[temp].copyText()

    def selUpOneLine(self):
        """한 줄 위 텍스트 선택하는 함수"""
        temp = self.lineCnt - 1
        if temp < 0:
            self.btn[len(self.btn) + temp].copyText()
        else:
            self.btn[temp].copyText()

    def pasteLine(self):
        """붙여넣기 함수"""
        self.btn[self.lineCnt].pasteText()

    def selDownOneLine(self):
        """한 줄 아래 텍스트 선택하는 함수"""
        self.btn[(self.lineCnt + 1) % len(self.btn)].copyText()

    def selDownFiveLine(self):
        """다섯 줄 아래 텍스트 선택하는 함수"""
        self.btn[(self.lineCnt + 5) % len(self.btn)].copyText()

    def textFind(self):
        """찾기 창 생성 함수"""
        self.textfindwindow = TextFindDialog(self)

    def textChange(self):
        """텍스트 바꾸기 창 생성 함수"""
        self.textchangewindow = TextChangeDialog(self)

    def changeThreePoint(self):
        """아래점 세 개 줄임표로 바꾸는 함수"""
        check = 0
        for i in range(len(self.btn)):
            txt = self.btn[i].text()
            if '...' in txt:
                self.btn[i].setText(txt.replace('...', '…'))
                check = 1
        if check:
            self.recordChange()
            self.statusbarmain.showMessage('변환 완료', 5000)

    def pasteThreePoint(self):
        """줄임표를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy('…')
        self.statusbarmain.showMessage("'…'를 복사했습니다.", 5000)
        if self.autoStartAction.isChecked():
            self.windowFocus()
            hotkey('ctrl', 'v')

    def pasteLongHLine(self):
        """줄표(가로)를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy('─')
        self.statusbarmain.showMessage("'─'를 복사했습니다.", 5000)
        if self.autoStartAction.isChecked():
            self.windowFocus()
            hotkey('ctrl', 'v')

    def pasteLongVLine(self):
        """줄표(세로)를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy('│')
        self.statusbarmain.showMessage("'│'를 복사했습니다.", 5000)
        if self.autoStartAction.isChecked():
            self.windowFocus()
            hotkey('ctrl', 'v')

    def pasteLittleJPquotaions(self):
        """홑낫표(세로)를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy('「」')
        self.statusbarmain.showMessage("'「」'를 복사했습니다.", 5000)
        if self.autoStartAction.isChecked():
            self.windowFocus()
            hotkey('ctrl', 'v')

    def pasteBigJPquotaions(self):
        """겹낫표(세로)를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy('『』')
        self.statusbarmain.showMessage("'『』'를 복사했습니다.", 5000)
        if self.autoStartAction.isChecked():
            self.windowFocus()
            hotkey('ctrl', 'v')

    def resetAllEvent(self):
        """모든 요소를 초기화하는 함수"""
        reply = QMessageBox.question(
            self, '초기화', '정말로 초기화하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.psThreadfunc.isRunning():
                self.psThreadfunc.terminate()
            if self.psAutoStartAction.isChecked():
                self.psAutoStartAction.toggle()
                self.psMode.toggle()
            if self.autoStartAction.isChecked():
                self.autoStartAction.toggle()
                self.startMode.toggle()
            self.psAutoStartAction.setDisabled(True)
            self.psMode.setDisabled(True)
            self.autoStartAction.setDisabled(True)
            self.startMode.setDisabled(True)
            self.ProgramSettingOn = False
            self.allString = ''
            self.filepath = ''
            self.selectedProgramTitle = '선택 안 함'
            self.setProgramStatus.setText(' 지정: 선택 안 함 ')
            self.textFindAction.setDisabled(True)
            self.textChangeAction.setDisabled(True)
            self.threePointChangeAction.setDisabled(True)
            self.findEdit.setDisabled(True)
            self.changeEdit.setDisabled(True)
            self.chgTPEdit.setDisabled(True)
            self.fiveUpEdit.setDisabled(True)
            self.oneUpEdit.setDisabled(True)
            self.oneDownEdit.setDisabled(True)
            self.fiveDownEdit.setDisabled(True)
            self.changeFont.setDisabled(True)
            self.textfindwindow.close()
            self.textchangewindow.close()
            self.setScrollArea()
            self.btn.clear()
            self.resetAllRecord()
            self.recordOfBtn.clear()
            self.recordOfBtnIndex = -1
            self.bookmark = -1
            self.goBmkEdit.setDisabled(True)
            self.goBookmarkAction.setDisabled(True)
            self.saveCheck = False
            self.undoEdit.setDisabled(True)
            self.redoEdit.setDisabled(True)
            self.saveFile.setDisabled(True)
            self.saveNewFile.setDisabled(True)
            self.statusbarmain.showMessage("초기화했습니다.", 5000)
            self.setWindowTitle('식붕이툴 Beta')
        else:
            pass

    def resetForProgramError(self):
        """지정된 프로그램에 문제가 생겼을 시 실행되는 함수"""
        if self.psThreadfunc.isRunning():
            self.psThreadfunc.terminate()
        if self.psAutoStartAction.isChecked():
            self.psAutoStartAction.toggle()
            self.psMode.toggle()
        if self.autoStartAction.isChecked():
            self.autoStartAction.toggle()
            self.startMode.toggle()
        self.psAutoStartAction.setDisabled(True)
        self.psMode.setDisabled(True)
        self.autoStartAction.setDisabled(True)
        self.startMode.setDisabled(True)
        self.ProgramSettingOn = False
        self.selectedProgramTitle = '선택 안 함'
        self.setProgramStatus.setText(' 지정: 선택 안 함 ')
        self.fileOpenAction.setEnabled(True)
        self.setProgramForPasteAction.setEnabled(True)
        self.fileMenu.setEnabled(True)
        self.setProgram.setEnabled(True)
        self.textfindwindow.close()
        self.textchangewindow.close()
        self.resetAllRecord()

        QMessageBox.warning(self, "프로그램 오류",
                            "지정한 프로그램에 문제가 생겼습니다.\n프로그램을 다시 지정해 주세요.")
        self.statusbarmain.showMessage("오류: 지정한 프로그램에 문제가 생겼습니다.", 5000)

    def tutorialLink(self):
        """매뉴얼 창 생성 함수"""
        QMessageBox.information(
            self, "매뉴얼", "자세한 사항은 아래 링크를 참고하세요.<br>"
            "<a href='https://docs.google.com/document/d/1JzMC_iyi265wXQv3zo2yEuC0qF0_NcdVGzgWb15UWig/edit?usp=sharing'>매뉴얼 링크</a>")

    def informationCheck(self):
        """정보 창 생성 함수"""
        QMessageBox.about(
            self, "정보",
            "<span style='font-weight: bold; font-size: 20px;'>식붕이툴 Beta3.0</span>&nbsp;&nbsp;&nbsp;&nbsp;"
            "<br><br>제작: <span style='font-weight: bold;'>고리성운</span><br>"
            "문의: <a href='https://docs.google.com/spreadsheets/d/1L4ai00inqZpMqeJuhz7bOCdrWgMTYHEZKl7EXY-nHqM/edit?usp=sharing'>구글 시트 링크</a>"
            "<br>제작자 블로그: <a href='https://blog.naver.com/dnjsfh611'>블로그 링크</a>"
            "<br><br>Special Thanks to : <br>함정, 공포투성이의 너" )

    def windowFocus(self):
        """지정한 프로그램을 최상위로 옮겨 focus 하는 함수"""
        try:
            if self.selectedProgram.isMinimized:
                self.selectedProgram.restore()
            else:
                SetForegroundWindow(self.selectedProgram._hWnd)
        except:  # 초기화나 마찬가지
            self.resetForProgramError()

    def setToolbarVisible(self):
        """툴바를 숨기거나 표시하는 함수"""
        if self.toolbar.isVisible():
            self.toolbar.setVisible(False)
        else:
            self.toolbar.setVisible(True)

    def closeEvent(self, event):
        """종료 시 이벤트 함수"""
        # reply = QMessageBox.question(
        #     self, '종료', '정말로 종료하시겠습니까?',
        #     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if reply == QMessageBox.Yes:
        self.textfindwindow.close()
        self.textchangewindow.close()

        if self.psThreadfunc.isRunning():  # PS 모드 스레드 체크
            self.psThreadfunc.terminate()
            self.psThreadfunc.wait()
        
        if self.bmkThread.isRunning():  # 북마크 스레드 체크
            self.bmkThread.terminate()
            self.bmkThread.wait()

        if len(self.macroListThread) > 0:  # 매크로 프로세스 체크
            for i in self.macroListThread:
                i.terminate()
                i.join()

        self.lastSettings()

        if self.saveCheck:  # 저장 여부 확인
            saveReply = QMessageBox.question(
                self, '저장 확인', '수정된 텍스트를 저장하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if saveReply == QMessageBox.Yes:
                self.saveTextFile(self.filepath)
            else:
                pass
        #     event.accept()
        # else:
        #     event.ignore()

    def lastSettings(self):
        """(종료 이벤트 시) 설정을 저장하는 함수"""
        self.settings.setValue("NotFirstStart", self.notFirstStart)
        self.settings.setValue("WindowSize", self.size())
        self.settings.setValue("windowPosition", self.pos())
        self.settings.setValue("LastFont", self.font)
        self.settings.setValue("State", self.saveState())
        self.settings.setValue("AdvSettings", self.advSettingsList)
        self.settings.setValue("MacroList", self.macroList)

# ================================메인 끝=====================================


if __name__ == '__main__':  # 메인 실행 함수
    freeze_support()  # 이거 없으면 매크로 프로세스 실행 시 똑같은 메인 윈도우창이 나타나는 오류 발생

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # 이걸로 다이얼로그에서 ? 를 없앨 수 있음
    ex = MainApp()
    sys.exit(app.exec_())

