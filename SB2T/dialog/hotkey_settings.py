from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QProgressBar,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from SB2T.thread import KeyRead, build_hotkey


NONE_TEXT = '선택 안 함'

# (내부 키, 화면에 보일 이름)
ACTIONS = (
    ('next', '다음 대사로 이동'),
    ('prev', '이전 대사로 이동'),
    ('recopy', '현재 대사 다시 복사'),
)


class HotkeyKeyReadDialog(QDialog):
    """대사 이동 단축키용 키 입력 창 클래스"""

    def __init__(self, parent, target, idx):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # 닫기 버튼 비활성화
        self.parent = parent
        self.target = target  # 'next' | 'prev' | 'recopy'
        self.idx = idx        # 0: 첫 번째 키, 1: 두 번째 키
        self.check = False

        lbl = QLabel('원하는 키를 누르세요...')
        pbar = QProgressBar()
        pbar.setMaximum(0)  # 무한 로딩 연출
        pbar.setMinimum(0)
        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(pbar)

        self.setLayout(vbox)
        self.setWindowTitle('키 입력')

        self.keyThread = KeyRead(self)
        self.keyThread.start()
        self.keyThread.keyReadSignal.connect(self.keyRead)

        self.setWindowIcon(QIcon('icons/setmacro.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 80, y + 50)
        self.exec()

    @pyqtSlot(str)
    def keyRead(self, key):
        """키 입력을 받아 표시하는 함수"""
        self.parent.setKey(self.target, self.idx, key)
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


class HotkeySetDialog(QDialog):
    """대사 이동 단축키 설정 창 클래스 (5.0 추가)

    Ctrl+V 자동 감지와 별개로 동작하는 전역 단축키를 지정한다.
    Ctrl+V를 다른 용도로 써야 하거나, 붙여넣기가 씹혔을 때 직접 대사를
    옮기고 싶은 경우를 위한 기능이다.

    매크로 설정과 동일하게 최대 두 키까지 조합할 수 있다.
    """

    def __init__(self, parent):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.parent = parent

        # 현재 저장된 값을 임시로 들고 있다가 확인을 눌러야 반영한다
        self.keys = {
            'next': list(parent.hotkeyNext),
            'prev': list(parent.hotkeyPrev),
            'recopy': list(parent.hotkeyRecopy),
        }
        self.buttons = {}

        desc = QLabel(
            '식붕이툴 창이 아닌 다른 프로그램에서도 동작하는 단축키입니다.\n'
            '두 키까지 조합할 수 있습니다. (예: Ctrl + F1)\n'
            '작업 중인 프로그램의 단축키와 겹치지 않는 키를 지정하세요.')

        btnOK = QPushButton('확인')
        btnOK.clicked.connect(self.saveKeys)
        btnCancel = QPushButton('취소')
        btnCancel.clicked.connect(self.close)

        btnBox = QHBoxLayout()
        btnBox.addStretch(2)
        btnBox.addWidget(btnOK)
        btnBox.addWidget(btnCancel)

        grid = QGridLayout()
        grid.addWidget(desc, 0, 0)
        grid.addWidget(self.createKeyGroup(), 1, 0)
        grid.addLayout(btnBox, 2, 0)

        self.setLayout(grid)
        self.setWindowTitle('대사 이동 단축키 설정')
        self.setWindowIcon(QIcon('icons/setmacro.png'))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 50, y + 70)
        self.exec()

    def createKeyGroup(self) -> QGroupBox:
        """단축키 지정 그룹 생성 함수"""
        groupbox = QGroupBox('단축키')
        grid = QGridLayout()

        for row, (target, label) in enumerate(ACTIONS):
            btn1 = QPushButton(self.keys[target][0] or NONE_TEXT)
            btn1.clicked.connect(
                lambda _, t=target: self.keyReadStart(t, 0))
            btn2 = QPushButton(self.keys[target][1] or NONE_TEXT)
            btn2.clicked.connect(
                lambda _, t=target: self.keyReadStart(t, 1))
            # 첫 번째 키를 정해야 두 번째 키를 지정할 수 있다 (매크로 설정과 동일)
            btn2.setEnabled(bool(self.keys[target][0]))
            self.buttons[target] = (btn1, btn2)

            reset = QPushButton('해제')
            reset.clicked.connect(lambda _, t=target: self.resetKeys(t))

            grid.addWidget(QLabel(label), row, 0)
            grid.addWidget(btn1, row, 1)
            grid.addWidget(QLabel(' + '), row, 2)
            grid.addWidget(btn2, row, 3)
            grid.addWidget(reset, row, 4)

        groupbox.setLayout(grid)
        return groupbox

    def keyReadStart(self, target, idx):
        """키 읽어들이기 창 생성 함수"""
        dialog = HotkeyKeyReadDialog(self, target, idx)

    def setKey(self, target, idx, key):
        """지정된 키를 임시 저장하고 버튼에 표시하는 함수"""
        if idx == 1 and key == self.keys[target][0]:
            QMessageBox.warning(self, "오류", "동일한 키로 설정할 수 없습니다!")
            return
        self.keys[target][idx] = key
        self.buttons[target][idx].setText(key or NONE_TEXT)
        if idx == 0:
            self.buttons[target][1].setEnabled(True)

    def resetKeys(self, target):
        """해당 동작의 단축키를 초기화하는 함수"""
        self.keys[target] = ['', '']
        btn1, btn2 = self.buttons[target]
        btn1.setText(NONE_TEXT)
        btn2.setText(NONE_TEXT)
        btn2.setDisabled(True)

    def checkDoubled(self) -> bool:
        """중복 조합 체크하는 함수"""
        used = [build_hotkey(v) for v in self.keys.values()]
        used = [u for u in used if u]
        if len(used) != len(set(used)):
            QMessageBox.warning(self, "오류", "같은 조합을 여러 동작에 지정할 수 없습니다!")
            return True
        return False

    def saveKeys(self):
        """지정한 단축키를 저장하고 적용하는 함수"""
        if self.checkDoubled():
            return
        self.parent.hotkeyNext = self.keys['next']
        self.parent.hotkeyPrev = self.keys['prev']
        self.parent.hotkeyRecopy = self.keys['recopy']
        self.parent.startHotkeyThread()
        self.parent.statusbarmain.showMessage("대사 이동 단축키를 적용했습니다.", 5000)
        self.close()
