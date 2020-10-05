import photoshop.api as ps
import pythoncom
from re import match
from PyQt5.QtCore import pyqtSignal, QThread


class StartPsThread(QThread):
    """PS 모드 스레드 클래스"""
    psTextLayerSignal = pyqtSignal(bool)    # 포토샵 모드에서 필요한 시그널

    def run(self):
        self.exec()

    def exec(self):
        """레이어 생성될 때까지 기다리는 반복하는 함수"""
        pythoncom.CoInitialize()  # 이거 안 하면 스레딩 오류나는 경우가 생김.
        while True:
            try:
                app = ps.Application()
                # tempApp = win32com.client.GetActiveObject("Photoshop.Application")
                try:
                    layername = app.Application.ActiveDocument.ActiveLayer.name
                    # if layer.kind == 2:  # 이 조건문 다는 순간 포토샵에서 마우스 커서가 오락가락하는 버그 같은 게....
                        # if (layername == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do"
                        # or ("레이어" in layername) or ("Layer" in layername)):
                        #     self.psTextLayerSignal.emit(True)
                        #     break
                    if (layername == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do" 
                    or match("^레이어 [0-9]+$", layername) or match("^Layer [0-9]+$", layername)):
                        self.psTextLayerSignal.emit(True)
                        break
                except:
                    pass
            except:
                self.psTextLayerSignal.emit(False)
                break
        pythoncom.CoUninitialize()
        # self.exit()
        self.quit()

