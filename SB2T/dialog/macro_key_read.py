from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QProgressBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from SB2T.thread import KeyRead


class KeyReadDialog(QDialog):
    """키 읽어들이기 창 클래스"""

    def __init__(self, parent, i):
        super().__init__(None, Qt.WindowStaysOnTopHint)
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

        self.setWindowIcon(QIcon('icons/setmacro.png'))
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