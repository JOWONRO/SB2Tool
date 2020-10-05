from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QProgressBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSlot

from SB2T.thread import LoadFonts


class LoadingDialog(QDialog):

    def __init__(self, parent, txt, icon):
        super().__init__(None, Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # 닫기 버튼 비활성화
        self.parent = parent
        self.txt = txt
        self.icon = icon

        load_thread = LoadFonts(self)
        load_thread.start()
        load_thread.loadSignal.connect(self.saveFontList)

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

    @pyqtSlot(list)
    def saveFontList(self, f_list):
        self.parent.font_list = f_list
        self.close()