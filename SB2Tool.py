import sys
from multiprocessing import freeze_support
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from SB2T import MainApp


if __name__ == '__main__':  # 메인 실행 함수
    freeze_support()  # 이거 없으면 매크로 프로세스 실행 시 똑같은 메인 윈도우창이 나타나는 오류 발생

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # 이걸로 다이얼로그에서 ? 를 없앨 수 있음
    ex = MainApp()
    sys.exit(app.exec_())

