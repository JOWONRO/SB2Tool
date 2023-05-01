import time
from multiprocessing import Process
from os.path import basename, exists
from re import match

import photoshop.api as ps
import pythoncom
import win32com.client
from clipboard import copy, paste
from psutil import Process as Prcss
from pyautogui import getAllTitles, getWindowsWithTitle, hotkey
from PyQt5.QtCore import QSettings, Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QAction, QDialog, QFileDialog, QFontDialog,
                             QInputDialog, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QScrollArea, QStatusBar, QToolBar,
                             QVBoxLayout, QWidget)
from win32gui import SetForegroundWindow
from win32process import GetWindowThreadProcessId

from SB2T.dialog import (AdvSettingsDialog, MacroSetDialog, SymbolSetDialog,
                         TextChangeDialog, TextFindDialog, TextItemStyleDialog)
from SB2T.obj import MacroStartwithProcess, TextLine
from SB2T.thread import CheckBmkThread, DetectCtrlV, StartPsThread


# =====================================메인 시작===================================
class MainApp(QMainWindow):
    """식붕이툴 메인 윈도우 창 클래스"""

    def __init__(self):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.settings = QSettings("RingNebula", "SB2Tool")
        self.version = 'Beta3.3'
        self.font = QFont()
        self.toolbar = QToolBar("기본 툴바")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        # 이거 안 하면 설정 저장에서 오류 뜸
        self.toolbar.setObjectName("DefaultToolbar")
        self.toolbarSym = QToolBar('기호 툴바')
        self.addToolBar(Qt.BottomToolBarArea, self.toolbarSym)
        self.toolbarSym.setObjectName('SymbolToolbar')
        self.macroList = []
        self.symbolList = []
        self.textItemStyleList = []
        self.currentTextItemStyle = None
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
        self.onTopDefault = 1
        self.advSettingsList = []
        # =========================================================================
        self.checkLastSettings()
        self.initUI()

    def checkLastSettings(self):
        """마지막으로 저장된 설정을 불러오는 함수"""
        try:
            self.notFirstStart = self.settings.value(
                "NotFirstStart", False, bool)
        except:
            self.notFirstStart = False
        if not self.notFirstStart:  # 초기화
            self.advSettingsList = [1, 0, 0, 0, 0, 0, 1, 1, 1]
            self.macroList = []
            self.symbolList = ['…', '―', '│', '「」', '『』', '♡', '♥', '♪']
            self.resize(291, 618)
            self.notFirstStart = True
            self.textItemStyleList = []
            self.currentTextItemStyle = None
        else:
            try:
                self.resize(self.settings.value("WindowSize"))
                self.move(self.settings.value("WindowPosition"))
                self.restoreState(self.settings.value("State"))
            except Exception as e:
                QMessageBox.warning(self, "오류", "UI 설정에 실패했습니다.\n" + str(e))
                self.resize(291, 618)
            try:
                self.macroList = self.settings.value("MacroList", [], str)
            except Exception as e:
                QMessageBox.warning(
                    self, "오류", "매크로 설정을 불러오지 못했습니다.\n" + str(e))
                self.macroList = []
            try:
                self.symbolList = self.settings.value("SymbolList", [], str)
            except Exception as e:
                QMessageBox.warning(
                    self, "오류", "특수기호 설정을 불러오지 못했습니다.\n" + str(e))
                self.symbolList = ['…', '―', '│', '「」', '『』', '♡', '♥', '♪']
            try:
                self.textItemStyleList = []
                self.currentTextItemStyle = None
                # self.textItemStyleList = self.settings.value(
                #     "TextItemsSettings", [])
                # self.currentTextItemStyle = self.settings.value(
                #     "CurrentTextItem")
            except Exception as e:
                QMessageBox.warning(
                    self, "오류", "대사별 문자 설정을 불러오지 못했습니다.\n" + str(e))
                self.textItemStyleList = []
                self.currentTextItemStyle = None
            try:
                self.advSettingsList = self.settings.value(
                    "AdvSettings", [], int)
                self.exceptbrackets = self.advSettingsList[0]
                self.exceptCurlybrackets = self.advSettingsList[1]
                self.exceptSquarebrackets = self.advSettingsList[2]
                self.exceptDQuotaion = self.advSettingsList[3]
                self.exceptSQuotaion = self.advSettingsList[4]
                self.pasteCtrlEnter = self.advSettingsList[5]
                self.commentWithNumber = self.advSettingsList[6]
                self.commentWithP = self.advSettingsList[7]
                self.onTopDefault = self.advSettingsList[8]
            except Exception as e:
                QMessageBox.warning(
                    self, "오류", "고급 설정을 불러오지 못했습니다.\n" + str(e))
                self.advSettingsList = [1, 0, 0, 0, 0, 0, 1, 1, 1]
            try:
                self.font = self.settings.value("LastFont")
            except Exception as e:
                QMessageBox.warning(self, "오류", "폰트 설정에 실패했습니다.\n" + str(e))
                self.font.setFamily("Malgun Gothic")
            if not self.onTopDefault:
                self.setWindowFlag(Qt.WindowStaysOnTopHint, False)

    def initUI(self):
        """초기 UI 설정 및 생성 함수"""
        # Switch ###############################################
        self.ProgramSettingOn = False

        # var ###############################################
        self.filepath = ''
        self.allString = ''
        self.saveCheck = False
        self.btn = []
        self.lineCnt = []
        self.lineCntBack = []
        self.macroListThread = []
        self.selectedProgram = getWindowsWithTitle('식붕이툴')
        self.selectedProgramTitle = '선택 안 함'
        self.recordOfPaste = []
        self.recordOfPasteIndex = -1
        self.recordOfBtn = []
        self.recordOfBtnIndex = -1
        self.psThreadfunc = StartPsThread(self)
        self.ctrlVThread = DetectCtrlV(self)
        self.bookmark = -1
        self.bmkThread = CheckBmkThread(self)

        # ================================UI================================
        self.setMainMenubar()
        self.setSymbolMenubar()
        self.setMainToolbar()
        self.setSymbolToolbar()
        self.setMainStatusbar()

        self.setWindowTitle('식붕이툴 ' + self.version)
        self.setWindowIcon(QIcon('icons/sbticon.png'))
        self.setAcceptDrops(True)
        self.show()

    # UI functions ######################################################
    def setMainMenubar(self):
        """메인 메뉴바 생성하는 함수"""
        self.openFile = QAction('열기(&O)', self)
        self.openFile.triggered.connect(self.showFileDialog)
        self.openFile.setShortcut('Ctrl+O')

        self.saveFile = QAction('저장(&S)', self)
        self.saveFile.triggered.connect(
            lambda: self.saveTextFile(self.filepath))
        self.saveFile.setShortcut('Y')
        self.saveFile.setDisabled(True)

        self.saveNewFile = QAction('다른 이름으로 저장(&A)', self)
        self.saveNewFile.triggered.connect(self.saveFileDialog)
        self.saveNewFile.setShortcut('Ctrl+Shift+S')
        self.saveNewFile.setDisabled(True)

        self.stayOnTop = QAction('창을 항상 위에 고정(&T)', self)
        self.stayOnTop.triggered.connect(self.setStayOnTop)
        self.stayOnTop.setShortcut('Ctrl+W')
        self.stayOnTop.setCheckable(True)
        if self.onTopDefault:
            self.stayOnTop.setChecked(True)

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

        self.setSymbol = QAction('특수문자 설정(&S)', self)
        self.setSymbol.triggered.connect(self.setSymbolDialog)
        self.setSymbol.setShortcut('Ctrl+Y')

        self.changeFont = QAction('글꼴(&F)', self)
        self.changeFont.triggered.connect(self.showFontDialog)
        self.changeFont.setDisabled(True)

        self.advSettings = QAction('고급 설정(&A)', self)
        self.advSettings.triggered.connect(self.advSettingsDialogShow)
        self.advSettings.setShortcut('F2')

        # self.psTISsettings = QAction('대사별 문자 설정(&B)', self)
        # self.psTISsettings.setIcon(QIcon('icons/setpsmode.png'))
        # self.psTISsettings.triggered.connect(self.psTISsettingsDialogShow)
        # self.psTISsettings.setShortcut('Ctrl+T')
        # self.psTISsettings.setDisabled(True)

        self.startMode = QAction('자동 모드(&S)', self)
        self.startMode.setCheckable(True)
        self.startMode.triggered.connect(self.autoStartByMenu)
        self.startMode.setShortcut('F5')
        self.startMode.setDisabled(True)

        self.ctrlVMode = QAction('Ctrl+V 모드(&V)', self)
        self.ctrlVMode.setCheckable(True)
        self.ctrlVMode.triggered.connect(self.ctrlVStartByMenu)
        self.ctrlVMode.setShortcut('F6')
        self.ctrlVMode.setDisabled(True)

        self.psMode = QAction('포토샵 모드(&P)', self)
        self.psMode.setCheckable(True)
        self.psMode.triggered.connect(self.psAutoStartByMenu)
        self.psMode.setShortcut('F7')
        self.psMode.setDisabled(True)

        self.macroMode = QAction('매크로 모드(&M)', self)
        self.macroMode.setCheckable(True)
        self.macroMode.triggered.connect(self.macroStartByMenu)
        self.macroMode.setShortcut('F8')

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

        self.linkEdit = QAction('모든 묶음 활성화(&L)', self)
        self.linkEdit.triggered.connect(self.setLinkAll)
        self.linkEdit.setShortcut('Ctrl+L')
        self.linkEdit.setDisabled(True)

        self.unlinkEdit = QAction('모든 묶음 비활성화(&K)', self)
        self.unlinkEdit.triggered.connect(self.setUnlinkAll)
        self.unlinkEdit.setShortcut('Ctrl+U')
        self.unlinkEdit.setDisabled(True)

        self.goBmkEdit = QAction('책갈피로 이동(&B)', self)
        self.goBmkEdit.triggered.connect(self.goToBookmark)
        self.goBmkEdit.setShortcut('Ctrl+B')
        self.goBmkEdit.setDisabled(True)

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

        self.undoEdit = QAction('바꾸기 취소(&U)', self)
        self.undoEdit.triggered.connect(self.undoChange)
        self.undoEdit.setShortcut('Ctrl+Z')
        self.undoEdit.setDisabled(True)

        self.redoEdit = QAction('바꾸기 다시 실행(&R)', self)
        self.redoEdit.triggered.connect(self.redoChange)
        self.redoEdit.setShortcut('Ctrl+X')
        self.redoEdit.setDisabled(True)

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
        self.fileMenu.addAction(self.stayOnTop)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.resetFile)
        self.fileMenu.addAction(self.closeTool)

        self.configMenu = self.menubar.addMenu('설정(&S)')
        self.configMenu.addAction(self.setProgram)
        self.configMenu.addAction(self.setMacro)
        self.configMenu.addAction(self.setSymbol)
        # self.configMenu.addAction(self.psTISsettings)
        self.configMenu.addSeparator()
        self.configMenu.addAction(self.changeFont)
        self.configMenu.addAction(self.advSettings)

        self.modeMenu = self.menubar.addMenu('모드(&M)')
        self.modeMenu.addAction(self.startMode)
        self.modeMenu.addAction(self.ctrlVMode)
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
        self.editMenu.addAction(self.linkEdit)
        self.editMenu.addAction(self.unlinkEdit)
        self.editMenu.addAction(self.goBmkEdit)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.findEdit)
        self.editMenu.addAction(self.changeEdit)
        self.editMenu.addAction(self.chgTPEdit)
        self.editMenu.addAction(self.undoEdit)
        self.editMenu.addAction(self.redoEdit)
        self.editMenu.addSeparator()

        self.symbolMenu = self.editMenu.addMenu('특수 문자 복사(&P)')

        self.helpMenu = self.menubar.addMenu('도움말(&H)')
        self.helpMenu.addAction(self.tutorial)
        self.helpMenu.addAction(self.information)

    def setSymbolMenubar(self):
        """특수문자 메뉴 생성하는 함수"""
        self.symbolMenu.clear()
        for symbol in self.symbolList:
            self.symbolMenu.addAction(self.getMenuActionOfSymbol(symbol))

    def getMenuActionOfSymbol(self, symbol):
        """메뉴 액션 가져오는 함수"""
        action = QAction(f"'{symbol}' 복사", self)
        action.triggered.connect(lambda: self.pasteSymbol(symbol))
        return action

    def setMainToolbar(self):
        """메인 툴바 생성하는 함수"""
        self.fileOpenAction = QAction(
            QIcon('icons/open.png'), 'FileOpen', self)
        self.fileOpenAction.setToolTip(
            '파일 열기 ( Ctrl+O )\n복사를 진행할 텍스트 파일을 불러옵니다.\n자동 모드나 포토샵 모드가 켜져 있으면 비활성화됩니다.')
        self.fileOpenAction.triggered.connect(self.showFileDialog)

        self.setProgramForPasteAction = QAction(
            QIcon("icons/setpro.png"), 'ProgramSetting', self)
        self.setProgramForPasteAction.setToolTip(
            '프로그램 세팅 ( Ctrl+P )\n붙여넣기를 진행할 프로그램을 지정합니다.')
        self.setProgramForPasteAction.triggered.connect(
            self.setProgramForPaste)

        self.setMacroAction = QAction(
            QIcon('icons/setmacro.png'), 'setMacro', self)
        self.setMacroAction.setToolTip('매크로 설정 ( Ctrl+M )\n키보드 매크로를 설정합니다.')
        self.setMacroAction.triggered.connect(self.setMacroDialog)

        # self.psTISsettingsAction = QAction(
        #     QIcon('icons/setpsmode.png'), 'setPSmode', self)
        # self.psTISsettingsAction.setToolTip(
        #     '대사별 문자 설정 (Ctrl+T)\n포토샵 모드 전용 설정으로,\n대사 태그별로 문자 설정을 지정합니다.')
        # self.psTISsettingsAction.triggered.connect(
        #     self.psTISsettingsDialogShow)
        # self.psTISsettingsAction.setDisabled(True)

        self.autoStartAction = QAction(
            QIcon("icons/auto.png"), 'AutoMode', self)
        self.autoStartAction.setToolTip(
            '자동 모드 ( F5 )\n원하는 텍스트를 클릭 시 자동으로\n지정된 프로그램에 붙여넣는 모드입니다.')
        self.autoStartAction.triggered.connect(self.autoStartByToolbar)
        self.autoStartAction.setCheckable(True)
        self.autoStartAction.setDisabled(True)

        self.ctrlVStartAction = QAction(
            QIcon("icons/ctrlv.png"), 'CtrlVMode', self)
        self.ctrlVStartAction.setToolTip(
            'Ctrl+V 모드 ( F6 )\nCtrl+V로 붙여넣기 시 자동으로\n다음 문장이 복사되는 모드입니다.')
        self.ctrlVStartAction.triggered.connect(self.ctrlVStartByToolbar)
        self.ctrlVStartAction.setCheckable(True)
        self.ctrlVStartAction.setDisabled(True)

        self.psAutoStartAction = QAction(
            QIcon("icons/psmode.png"), 'PSMode', self)
        self.psAutoStartAction.setToolTip(
            '포토샵 모드 (F7)\n포토샵 전용 붙여넣기 모드로,\n텍스트 레이어 생성 시 자동으로 붙여넣는 모드입니다.')
        self.psAutoStartAction.triggered.connect(self.psAutoStartByToolbar)
        self.psAutoStartAction.setCheckable(True)
        self.psAutoStartAction.setDisabled(True)

        self.macroStartAction = QAction(
            QIcon('icons/macromode.png'), 'Macro', self)
        self.macroStartAction.setToolTip('매크로 모드 (F8)\n키보드 매크로 기능을 실행합니다.')
        self.macroStartAction.triggered.connect(self.macroStartByToolbar)
        self.macroStartAction.setCheckable(True)

        # self.resetRecordAction = QAction(QIcon("icons/record.png"), 'ResetRecord', self)
        # self.resetRecordAction.setToolTip('기록 초기화 (Del)\n붙여넣기 기록을 모두 초기화합니다.')
        # self.resetRecordAction.triggered.connect(self.resetAllRecord)
        # self.resetRecordAction.setDisabled(True)

        self.linkAction = QAction(QIcon('icons/link.png'), 'SetLink', self)
        self.linkAction.setToolTip('모든 묶음 활성화 ( Ctrl+L )\n모든 텍스트 묶음을 활성화합니다.')
        self.linkAction.triggered.connect(self.setLinkAll)
        self.linkAction.setDisabled(True)

        self.unlinkAction = QAction(
            QIcon('icons/unlink.png'), 'SetUnlink', self)
        self.unlinkAction.setToolTip(
            '모든 묶음 비활성화 ( Ctrl+U )\n모든 텍스트 묶음을 비활성화합니다.')
        self.unlinkAction.triggered.connect(self.setUnlinkAll)
        self.unlinkAction.setDisabled(True)

        self.textFindAction = QAction(
            QIcon('icons/find.png'), 'TextFind', self)
        self.textFindAction.setToolTip('찾기 ( Ctrl+F )\n특정 텍스트를 검색하여 복사합니다.')
        self.textFindAction.triggered.connect(self.textFind)
        self.textFindAction.setDisabled(True)
        self.textfindwindow = QDialog(self)

        self.textChangeAction = QAction(
            QIcon('icons/change.png'), 'TextChange', self)
        self.textChangeAction.setToolTip(
            '바꾸기 ( Ctrl+H )\n특정 텍스트를 찾아 원하는 텍스트로 바꿉니다.')
        self.textChangeAction.triggered.connect(self.textChange)
        self.textChangeAction.setDisabled(True)
        self.textchangewindow = QDialog(self)

        self.threePointChangeAction = QAction(
            QIcon('icons/chgthrpnt.png'), 'ThreePointChange', self)
        self.threePointChangeAction.setToolTip(
            '아래점 바꾸기\n아래점 세 개를 줄임표로 전부 바꿉니다.')
        self.threePointChangeAction.triggered.connect(self.changeThreePoint)
        self.threePointChangeAction.setDisabled(True)

        self.goBookmarkAction = QAction(
            QIcon('icons/bookmark.png'), 'GotoBookmark', self)
        self.goBookmarkAction.setToolTip(
            '책갈피 이동 ( Ctrl+B )\n책갈피가 있는 줄로 이동합니다.')
        self.goBookmarkAction.triggered.connect(self.goToBookmark)
        self.goBookmarkAction.setDisabled(True)

        self.toolbar.addAction(self.fileOpenAction)
        self.toolbar.addAction(self.setProgramForPasteAction)
        # self.toolbar.addAction(self.psTISsettingsAction)
        self.toolbar.addAction(self.setMacroAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.autoStartAction)
        self.toolbar.addAction(self.ctrlVStartAction)
        self.toolbar.addAction(self.psAutoStartAction)
        self.toolbar.addAction(self.macroStartAction)
        self.toolbar.addSeparator()
        # self.toolbar.addAction(self.resetRecordAction)
        self.toolbar.addAction(self.linkAction)
        self.toolbar.addAction(self.unlinkAction)
        self.toolbar.addAction(self.goBookmarkAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.textFindAction)
        self.toolbar.addAction(self.textChangeAction)
        self.toolbar.addAction(self.threePointChangeAction)
        # self.toolbar.addSeparator()

    def setSymbolToolbar(self):
        """특수문자 툴바 생성하는 함수"""
        self.toolbarSym.clear()
        for symbol in self.symbolList:
            self.toolbarSym.addWidget(self.getActionOfSymbol(symbol))

    def getActionOfSymbol(self, symbol):
        """툴바 액션 가져오는 함수"""
        action = QPushButton(symbol, self)
        action.setToolTip(
            f"'{symbol}' 복사\n기본 모드 시 복사만, 자동 모드 시 붙여넣습니다.")
        action.clicked.connect(lambda: self.pasteSymbol(symbol))
        action.setFixedSize(30, 30)
        return action

    def setMainStatusbar(self):
        """메인 스테이터스 바 생성하는 함수"""
        self.forVLine = QLabel("")
        self.lineStatus = QLabel(" 줄  ")
        self.setProgramStatus = QLabel(" 지정: 선택 안 함 ")
        self.statusbarmain = QStatusBar(self)
        self.setStatusBar(self.statusbarmain)
        self.statusbarmain.addPermanentWidget(self.forVLine)
        self.statusbarmain.addPermanentWidget(self.lineStatus)
        self.statusbarmain.addPermanentWidget(self.setProgramStatus)

    def setScrollArea(self):
        """ScrollArea 영역 초기화하는 함수"""
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)  # 여백 없애기 1
        self.vbox.setSpacing(0)  # 여백 없애기 2
        self.vbox.setAlignment(Qt.AlignTop)
        self.widget.setLayout(self.vbox)

        self.scroll = QScrollArea()
        self.setStyleSheet(
            "QScrollArea {border: none;}")
        self.hbar = self.scroll.horizontalScrollBar()
        self.setCentralWidget(self.scroll)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        # self.setAcceptDrops(True)

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
        font_dialog = QFontDialog(self)
        font_dialog.setCurrentFont(self.font)
        if font_dialog.exec_() == QDialog.Accepted:
            self.font = font_dialog.selectedFont()
            for i in range(len(self.btn)):
                self.btn[i].setFont(self.font)

    def showFileDialog(self):
        """텍스트 파일 열기 창 생성 함수"""
        self.textfindwindow.close()
        self.textchangewindow.close()
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
                temp1[i] = temp2[idx]
                idx += 1
        txt = '\n'.join(temp1)

        try:
            f = open(path, 'w', encoding='UTF8')  # 기본 UTF8로 저장
            f.write(txt)
            f.close()
            self.statusbarmain.showMessage('저장 완료', 5000)
            self.saveCheck = False
            self.saveFile.setDisabled(True)
            self.saveNewFile.setDisabled(True)
            self.filepath = path
            self.setWindowTitle(basename(path) + ' - 식붕이툴 ' + self.version)
        except Exception as e:
            QMessageBox.warning(self, "오류", "파일을 저장하지 못했습니다.\n" + str(e))

    def openTextFile(self, path):
        """텍스트 파일 열기 관련 함수"""
        try:  # UTF-8로 우선 불러오기
            with open(path, 'r', encoding='UTF8') as f:
                data = f.read()
                filepath = f.name
            self.setStatusAfterOpenTxt(data, filepath)
        except:
            try:
                with open(path, 'r') as f:
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
        self.ctrlVStartAction.setDisabled(True)
        self.ctrlVMode.setDisabled(True)
        # self.psTISsettings.setDisabled(True)
        # self.psTISsettingsAction.setDisabled(True)
        self.autoStartAction.setDisabled(True)
        self.startMode.setDisabled(True)
        self.textFindAction.setDisabled(True)
        self.textChangeAction.setDisabled(True)
        self.threePointChangeAction.setDisabled(True)
        self.linkAction.setDisabled(True)
        self.unlinkAction.setDisabled(True)
        self.linkEdit.setDisabled(True)
        self.unlinkEdit.setDisabled(True)
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

        self.setWindowTitle(basename(self.filepath) +
                            ' - 식붕이툴 ' + self.version)
        self.linetext = data.splitlines()
        self.linelen = len(self.linetext)
        self.setBtnsForText()

    def setBtnsForText(self):
        """불러온 텍스트 파일을 기반으로 scroll area 채우는 함수"""
        backup = []
        connect_num = -1  # -1:X, 0:머리, 1:중간, 2:꼬리
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
                    if connect_num == -1:
                        if self.linetext[i + 1] != '':
                            connect_num = 0
                            head = linenum
                    elif connect_num == 0:
                        if self.linetext[i + 1] != '':
                            connect_num = 1
                        else:
                            connect_num = 2
                    elif connect_num == 1:
                        if self.linetext[i + 1] != '':
                            connect_num = 1
                        else:
                            connect_num = 2
                else:
                    if connect_num != -1:
                        connect_num = 2

                self.btn.append(TextLine(self, linenum, mode,
                                self.linetext[i], connect_num, head))
                backup.append(self.linetext[i])
                try:
                    self.btn[linenum].setFont(self.font)
                except:
                    pass
                self.vbox.addWidget(self.btn[linenum])
            else:
                connect_num = -1
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
            self.linkAction.setEnabled(True)
            self.unlinkAction.setEnabled(True)
            self.linkEdit.setEnabled(True)
            self.unlinkEdit.setEnabled(True)
            self.findEdit.setEnabled(True)
            self.changeEdit.setEnabled(True)
            self.chgTPEdit.setEnabled(True)
            self.changeFont.setEnabled(True)
            self.statusbarmain.showMessage("")
            if self.ProgramSettingOn:
                self.autoStartAction.setEnabled(True)
                self.startMode.setEnabled(True)
                if self.checkPhotoshop():
                    self.psAutoStartAction.setEnabled(True)
                    self.psMode.setEnabled(True)
                    # self.psTISsettings.setEnabled(True)
                    # self.psTISsettingsAction.setEnabled(True)
                else:
                    # self.psTISsettings.setDisabled(True)
                    # self.psTISsettingsAction.setDisabled(True)
                    self.psAutoStartAction.setDisabled(True)
                    self.psMode.setDisabled(True)
            else:
                self.autoStartAction.setDisabled(True)
                self.startMode.setDisabled(True)
                # self.psTISsettings.setDisabled(True)
                # self.psTISsettingsAction.setDisabled(True)
                self.psAutoStartAction.setDisabled(True)
                self.psMode.setDisabled(True)
            self.ctrlVStartAction.setEnabled(True)
            self.ctrlVMode.setEnabled(True)
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
                self.btn[self.bookmark].setStyleOfLine('default')
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
        # 타이틀이 없는 정체불명인 것들이 많아서 일단 다 걸러줌
        temp = list(filter(lambda a: a != '', temp))

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
            except Exception as e:
                QMessageBox.warning(self, "프로그램 지정 오류",
                                    "프로그램 목록 생성에 실패했습니다.\n다시 시도해 주세요.\n" + str(e))
        filteredTitles.append(self.selectedProgramTitle)

        for k in titles:  # 이 부분에서 정제된 목록이 완성
            if self.selectedProgramTitle not in k:
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
        self.setToolMenuAfterSetPrgm(item)

    def setToolMenuAfterSetPrgm(self, item):
        """프로그램 지정 이후, 메뉴바와 툴바 세팅하는 함수"""
        check = False
        if item == '선택 안 함':
            self.ProgramSettingOn = False
            self.autoStartAction.setDisabled(True)
            self.startMode.setDisabled(True)
            # self.psTISsettings.setDisabled(True)
            # self.psTISsettingsAction.setDisabled(True)
            self.psAutoStartAction.setDisabled(True)
            self.psMode.setDisabled(True)
        else:
            try:
                self.selectedProgram = getWindowsWithTitle(item)[0]
                check = True
            except Exception as e:
                self.resetForProgramError(str(e))
            self.ProgramSettingOn = check
            if check:
                if self.checkPhotoshop():
                    # self.psTISsettings.setEnabled(True)
                    # self.psTISsettingsAction.setEnabled(True)
                    if len(self.btn) != 0:
                        self.autoStartAction.setEnabled(True)
                        self.startMode.setEnabled(True)
                        self.psAutoStartAction.setEnabled(True)
                        self.psMode.setEnabled(True)
                    else:
                        self.autoStartAction.setDisabled(True)
                        self.startMode.setDisabled(True)
                        self.psAutoStartAction.setDisabled(True)
                        self.psMode.setDisabled(True)
                else:
                    if len(self.btn) != 0:
                        self.autoStartAction.setEnabled(True)
                        self.startMode.setEnabled(True)
                    else:
                        self.autoStartAction.setDisabled(True)
                        self.startMode.setDisabled(True)
                    # self.psTISsettings.setDisabled(True)
                    # self.psTISsettingsAction.setDisabled(True)
                    self.psAutoStartAction.setDisabled(True)
                    self.psMode.setDisabled(True)
                self.statusbarmain.showMessage("프로그램 지정 완료", 5000)

    def advSettingsDialogShow(self):
        """고급 설정 창 생성 함수"""
        dialog = AdvSettingsDialog(self)

    # def psTISsettingsDialogShow(self):
    #     """대사별 포토샵 문자 설정 창 생성 함수"""
    #     dialog = TextItemStyleDialog(self)

    def checkPhotoshop(self) -> bool:
        """지정된 프로그램이 포토샵인지 확인하는 함수"""
        # check = False
        pythoncom.CoInitialize()
        check = False
        test = True
        try:
            threadid, pid = GetWindowThreadProcessId(
                self.selectedProgram._hWnd)
            if 'Photoshop' in Prcss(pid).name():
                check = True
            test = False
            # temp = win32com.client.GetActiveObject("Photoshop.Application")  # 포토샵 앱 불러오기
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
            QMessageBox.warning(self, "오류",
                                "프로세스 체크 오류!\n" + str(e))

        if test:
            try:
                temp = win32com.client.GetActiveObject("Photoshop.Application")
                check = True
            except Exception as e:
                QMessageBox.warning(self, "오류",
                                    "포토샵 체크 오류!\n자동 모드는 가능합니다.\n" + str(e))

        if check:
            try:
                self.ps_app = ps.Application()
            except Exception as e:
                check = False
                QMessageBox.warning(self, "오류",
                                    "포토샵 연동에 실패했습니다!\n자동 모드는 가능합니다.\n" + str(e))
        pythoncom.CoUninitialize()
        return check
        # if check:
        #     self.psAutoStartAction.setEnabled(True)
        #     self.psMode.setEnabled(True)
        # else:
        #     self.psAutoStartAction.setDisabled(True)
        #     self.psMode.setDisabled(True)

    # main functions #########################################################
    def setStayOnTop(self):
        """항상 위에 고정 설정 함수"""
        if self.stayOnTop.isChecked():
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.show()  # 소름 돋게도 show 다시 안 해주면 메인 윈도우창이 사라짐 ㄷㄷ

    def setLinkAll(self):
        """모든 텍스트라인 묶음을 활성화하는 함수"""
        for i in self.btn:
            if i.act_connection == 0 and i.connected_mode != -1:
                i.setActiveConnection(True)
        self.statusbarmain.showMessage('모든 텍스트라인 묶음 활성화', 5000)

    def setUnlinkAll(self):
        """모든 텍스트라인 묶음을 비활성화하는 함수"""
        for i in self.btn:
            if i.act_connection == 1 and i.connected_mode != -1:
                i.setActiveConnection(False)
        self.statusbarmain.showMessage('모든 텍스트라인 묶음 비활성화', 5000)

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
            # self.psTISsettings.setDisabled(True)
            # self.psTISsettingsAction.setDisabled(True)
            self.statusbarmain.showMessage("자동 모드 On")
        else:
            if not self.psAutoStartAction.isChecked():
                self.setProgramForPasteAction.setEnabled(True)
                self.setProgram.setEnabled(True)
                # self.psTISsettings.setEnabled(True)
                # self.psTISsettingsAction.setEnabled(True)
            self.statusbarmain.showMessage("자동 모드 Off", 5000)

    def ctrlVStartByMenu(self):
        """메뉴에서 Ctrl+V 모드를 켤 때 거쳐가는 함수"""
        self.ctrlVStartAction.toggle()
        self.ctrlVStart()

    def ctrlVStartByToolbar(self):
        """툴바에서 Ctrl+V 모드를 켤 때 거쳐가는 함수"""
        self.ctrlVMode.toggle()
        self.ctrlVStart()

    def ctrlVStart(self):
        """Ctrl+V 모드 시작 함수"""
        if self.ctrlVThread.isRunning():
            self.ctrlVThread.disconnect()   # 스레드 체크
            self.ctrlVThread.terminate()
        if self.ctrlVStartAction.isChecked():
            self.psAutoStartAction.setDisabled(True)
            self.psMode.setDisabled(True)
            self.statusbarmain.showMessage("Ctrl+V 모드 On")
            self.startCtrlVMode()
        else:
            self.psAutoStartAction.setEnabled(True)
            self.psMode.setEnabled(True)
            self.statusbarmain.showMessage("Ctrl+V 모드 Off", 5000)

    def startCtrlVMode(self):
        """Ctrl+V 모드 스레드 시작 함수"""
        if self.ctrlVThread.isRunning():
            self.ctrlVThread.disconnect()  # 스레드 체크
            self.ctrlVThread.terminate()
        self.ctrlVThread = DetectCtrlV(self)  # 스레드 클래스 생성
        self.ctrlVThread.start()
        self.ctrlVThread.detectCtrlVSignal.connect(
            self.copyNextLineAtCtrlVMode)

    @pyqtSlot(bool)
    def copyNextLineAtCtrlVMode(self, isValid):
        """Ctrl+V 모드 붙여넣기 실행 함수"""
        if not isValid or len(self.lineCnt) == 0:
            return
        currentCopiedText = self.btn[self.lineCnt[0]].whatTxtForCopy()
        if currentCopiedText == paste():
            self.btn[self.lineCnt[0]].setTraceTextLine()
            time.sleep(0.1)
            self.nextLineCopy()

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
            self.ctrlVStartAction.setDisabled(True)
            self.ctrlVMode.setDisabled(True)
            # self.psTISsettings.setDisabled(True)
            # self.psTISsettingsAction.setDisabled(True)
            self.statusbarmain.showMessage("포토샵 모드 On")
            self.psAutoThreadStart()
        else:
            if not self.autoStartAction.isChecked():
                self.setProgramForPasteAction.setEnabled(True)
                self.setProgram.setEnabled(True)
                self.ctrlVStartAction.setEnabled(True)
                self.ctrlVMode.setEnabled(True)
                # self.psTISsettings.setEnabled(True)
                # self.psTISsettingsAction.setEnabled(True)
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
        if len(self.lineCnt) == 0:  # 첫 번째 텍스트 라인 모드 체크
            self.lineCnt.append(self.nextNumOfBtnMode(0))

        try:
            if boolean:
                self.btn[self.lineCnt[0]].copyText()
                self.btn[self.lineCnt[0]].pasteTextPSMode()
            else:
                self.resetForProgramError('')
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
        temp = self.nextNumOfBtnMode(self.lineCnt[-1] + 1)
        if temp == -1:  # 마지막 텍스트 라인 복붙했을 때 자동으로 PS, Ctrl+V 모드 종료
            if self.psAutoStartAction.isChecked():
                self.psAutoStartAction.toggle()
                self.psMode.toggle()
                self.psAutoStart()
            if self.ctrlVStartAction.isChecked():
                self.ctrlVStartAction.toggle()
                self.ctrlVMode.toggle()
                self.ctrlVStart()
            self.statusbarmain.showMessage("마지막 텍스트를 붙여넣었습니다!", 5000)
        else:
            self.btn[temp].copyText()

    def setMacroDialog(self):
        """매크로 설정 창 생성 함수"""
        dialog = MacroSetDialog(self)

    def setSymbolDialog(self):
        """특수문자 설정 창 생성 함수"""
        dialog = SymbolSetDialog(self)
        self.setSymbolToolbar()
        self.setSymbolMenubar()

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
        self.lineCnt.clear()
        self.lineCntBack.clear()
        self.lineStatus.setText(" 줄  ")
        self.pasteEdit.setDisabled(True)
        self.fiveUpEdit.setDisabled(True)
        self.oneUpEdit.setDisabled(True)
        self.oneDownEdit.setDisabled(True)
        self.fiveDownEdit.setDisabled(True)
        # self.resetRecordAction.setDisabled(True)
        self.resetRecord.setDisabled(True)

        for i in self.btn:  # 버튼 토글 초기화
            if i.isChecked():
                i.toggle()
            i.pasted = 0
            i.setStyleOfLine('default')

    def changeBackup(self) -> list:
        """현재 텍스트 상태를 백업하는 함수"""
        temp = []
        for i in self.btn:
            temp.append(i.txt)
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
            if temp1[i] != temp2[i]:
                self.saveCheck = True
                break
        if self.saveCheck:
            self.setWindowTitle(
                '*' + basename(self.filepath) + ' - 식붕이툴 ' + self.version)
            self.saveFile.setEnabled(True)
            self.saveNewFile.setEnabled(True)
        else:
            self.setWindowTitle(basename(self.filepath) +
                                ' - 식붕이툴 ' + self.version)
            self.saveFile.setDisabled(True)
            self.saveNewFile.setDisabled(True)

    def undoChange(self):
        """바꾸기 되돌리기 함수"""
        self.recordOfBtnIndex -= 1
        temp = self.recordOfBtn[self.recordOfBtnIndex]
        for i in range(len(self.btn)):
            if self.btn[i].txt != temp[i]:
                self.btn[i].txt = temp[i]
                self.btn[i].setLine()
                self.scroll.ensureWidgetVisible(self.btn[i], 0, 0)
                self.hbar.setValue(self.hbar.minimum())

        self.redoEdit.setEnabled(True)
        if self.recordOfBtnIndex < 1:
            self.undoEdit.setDisabled(True)

        self.checkSameOfAllString()

    def redoChange(self):
        """바꾸기 다시 실행하기 함수"""
        self.recordOfBtnIndex += 1
        temp = self.recordOfBtn[self.recordOfBtnIndex]
        for i in range(len(self.btn)):
            if self.btn[i].txt != temp[i]:
                self.btn[i].txt = temp[i]
                self.btn[i].setLine()
                self.scroll.ensureWidgetVisible(self.btn[i], 0, 0)
                self.hbar.setValue(self.hbar.minimum())

        self.undoEdit.setEnabled(True)
        if self.recordOfBtnIndex == len(self.recordOfBtn) - 1:
            self.redoEdit.setDisabled(True)

        self.checkSameOfAllString()

    def selUpFiveLine(self):
        """다섯 줄 위 텍스트 선택하는 함수"""
        num = self.lineCnt[0]
        i = 0
        while i < 5:
            num -= 1
            if self.btn[num].mode == 1:
                i += 1
                if self.btn[num].act_connection == 1:
                    num = self.btn[num].head
        self.btn[num].copyText()

    def selUpOneLine(self):
        """한 줄 위 텍스트 선택하는 함수"""
        num = self.lineCnt[0]
        num -= 1
        while self.btn[num].mode != 1:
            num -= 1
        self.btn[num].copyText()

    def pasteLine(self):
        """붙여넣기 함수"""
        self.btn[self.lineCnt[0]].pasteText()

    def selDownOneLine(self):
        """한 줄 아래 텍스트 선택하는 함수"""
        num = self.lineCnt[-1]
        num = (num + 1) % len(self.btn)
        while self.btn[num].mode != 1:
            num = (num + 1) % len(self.btn)
        self.btn[num].copyText()

    def selDownFiveLine(self):
        """다섯 줄 아래 텍스트 선택하는 함수"""
        num = self.lineCnt[-1]
        i = 0
        while i < 5:
            num = (num + 1) % len(self.btn)
            if self.btn[num].mode == 1:
                i += 1
                if self.btn[num].act_connection == 1:
                    while self.btn[num].connected_mode != 2:
                        num = (num + 1) % len(self.btn)
        self.btn[num].copyText()

    def textFind(self):
        """찾기 창 생성 함수"""
        self.textfindwindow = TextFindDialog(self)
        # show()로 실행하는 다이얼로그는 self 변수로 해서 close() 실행을 용이하게.

    def textChange(self):
        """텍스트 바꾸기 창 생성 함수"""
        self.textchangewindow = TextChangeDialog(self)
        # show()로 실행하는 다이얼로그는 self 변수로 해서 close() 실행을 용이하게.

    def changeThreePoint(self):
        """아래점 세 개 줄임표로 바꾸는 함수"""
        check = 0
        for i in self.btn:
            if '...' in i.txt:
                i.txt = i.txt.replace('...', '…')
                check = 1
        if check:
            self.recordChange()
            self.statusbarmain.showMessage('변환 완료', 5000)

    def pasteSymbol(self, symbol):
        """특수문자를 복사 및 자동 모드 시 붙여넣는 함수"""
        copy(symbol)
        self.statusbarmain.showMessage(f"'{symbol}'를 복사했습니다.", 5000)
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
            if self.ctrlVThread.isRunning():
                self.ctrlVThread.disconnect()
                self.ctrlVThread.terminate()
            if self.psAutoStartAction.isChecked():
                self.psAutoStartAction.toggle()
                self.psMode.toggle()
            if self.autoStartAction.isChecked():
                self.autoStartAction.toggle()
                self.startMode.toggle()
            self.psAutoStartAction.setDisabled(True)
            self.psMode.setDisabled(True)
            self.ctrlVStartAction.setDisabled(True)
            self.ctrlVMode.setDisabled(True)
            # self.psTISsettings.setDisabled(True)
            # self.psTISsettingsAction.setDisabled(True)
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
            self.linkAction.setDisabled(True)
            self.unlinkAction.setDisabled(True)
            self.linkEdit.setDisabled(True)
            self.unlinkEdit.setDisabled(True)
            self.findEdit.setDisabled(True)
            self.changeEdit.setDisabled(True)
            self.chgTPEdit.setDisabled(True)
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
            self.setWindowTitle('식붕이툴 ' + self.version)
        else:
            pass

    def resetForProgramError(self, e):
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
        # self.psTISsettings.setDisabled(True)
        # self.psTISsettingsAction.setDisabled(True)
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
                            "지정한 프로그램에 문제가 생겼습니다.\n프로그램을 다시 지정해 주세요.\n" + e)
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
            "<span style='font-weight: bold; font-size: 20px;'>식붕이툴 " +
            self.version + "</span>&nbsp;&nbsp;&nbsp;&nbsp;"
            "<br><br>제작: <span style='font-weight: bold;'>고리성운</span><br>"
            "문의: <a href='https://docs.google.com/spreadsheets/d/1L4ai00inqZpMqeJuhz7bOCdrWgMTYHEZKl7EXY-nHqM/edit?usp=sharing'>구글 시트 링크</a>"
            "<br>제작자 블로그: <a href='https://blog.naver.com/dnjsfh611'>블로그 링크</a>"
            "<br><br>Special Thanks to : <br>함정, 공포투성이의 너, ENE")

    def windowFocus(self):
        """지정한 프로그램을 최상위로 옮겨 focus 하는 함수"""
        try:
            if self.selectedProgram.isMinimized:
                self.selectedProgram.restore()
            else:
                SetForegroundWindow(self.selectedProgram._hWnd)
        except Exception as e:
            self.resetForProgramError(str(e))

    def setToolbarVisible(self):
        """툴바를 숨기거나 표시하는 함수"""
        if self.toolbar.isVisible():
            self.toolbar.setVisible(False)
        else:
            self.toolbar.setVisible(True)

    def closeEvent(self, event):
        """종료 시 이벤트 함수"""
        # print(str(self.size()))

        # reply = QMessageBox.question(
        #     self, '종료', '정말로 종료하시겠습니까?',
        #     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if reply == QMessageBox.Yes:
        self.textfindwindow.close()
        self.textchangewindow.close()

        if self.psThreadfunc.isRunning():  # PS 모드 스레드 체크
            self.psThreadfunc.terminate()
            self.psThreadfunc.wait()

        if self.ctrlVThread.isRunning():
            self.ctrlVThread.disconnect()  # Ctrl+V 모드 스레드 체크
            self.ctrlVThread.terminate()
            self.ctrlVThread.wait()

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
        self.settings.setValue("SymbolList", self.symbolList)
        self.settings.setValue("TextItemsSettings", self.textItemStyleList)
        self.settings.setValue("CurrentTextItem", self.currentTextItemStyle)
