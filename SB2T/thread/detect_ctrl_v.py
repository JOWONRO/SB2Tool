import keyboard
from PyQt5.QtCore import QThread, pyqtSignal


class DetectCtrlV(QThread):
    """Ctrl+V 읽어들이기 스레드 클래스"""
    isCtrlDown = False
    detectCtrlVSignal = pyqtSignal(bool)

    def run(self):
        self.exec()

    def exec(self):
        keyboard.hook_key('ctrl', lambda e: self.checkCtrlDown(str(e)))
        keyboard.hook_key('v', lambda e: self.checkVDown(str(e)))
        keyboard.wait()

    def checkCtrlDown(self, event):
        """ctrl 키 down 이벤트 때 스위치 변경하는 함수"""
        if 'down' in event:
            self.isCtrlDown = True
        else:
            self.isCtrlDown = False

    def checkVDown(self, event):
        """ctrl 키가 down 상태인지 확인하여 이벤트 쏘는 함수"""
        if self.isCtrlDown and 'down' in event:
            self.detectCtrlVSignal.emit(True)

    def disconnect(self):
        keyboard.unhook_all()
