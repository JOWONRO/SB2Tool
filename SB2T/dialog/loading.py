from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QProgressBar,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from SB2T.thread import LoadAndSaveFonts


class LoadingDialog(QDialog):
    """세부 문자 설정 창 생성 시 생성되는 로딩 창 클래스"""

    def __init__(self, parent, txt, icon):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # 닫기 버튼 비활성화
        self.parent = parent
        self.txt = txt
        self.icon = icon

        self.load_thread = LoadAndSaveFonts(self.parent)
        self.load_thread.start()
        self.load_thread.loadSignal.connect(self.finishLoading)

        lbl = QLabel(txt)
        pbar = QProgressBar()
        pbar.setMaximum(0)  # 맥시멈 미니멈 둘 다 0으로 해주면 무한 로딩 연출 가능
        pbar.setMinimum(0)
        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(pbar)

        self.setLayout(vbox)
        self.setWindowTitle('로딩 중...')
        self.setWindowIcon(QIcon(self.icon))
        x, y = self.parent.pos().x(), self.parent.pos().y()  # 창 위치 조정
        self.move(x + 50, y + 130)
        self.exec()

    @pyqtSlot(bool)
    def finishLoading(self, check):
        """로딩을 종료하는 함수"""
        if check:
            self.load_thread.wait()
            self.close()
        else:
            QMessageBox.warning(self, "오류", "글꼴을 저장하지 못했습니다.")
            self.load_thread.wait()
            self.close()