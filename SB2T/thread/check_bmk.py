from PyQt5.QtCore import pyqtSignal, QThread


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

