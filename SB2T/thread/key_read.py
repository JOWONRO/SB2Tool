from PyQt5.QtCore import pyqtSignal, QThread
import keyboard


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

