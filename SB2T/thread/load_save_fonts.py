import photoshop.api as ps
import pythoncom
from PyQt5.QtCore import QThread, pyqtSignal


class LoadAndSaveFonts(QThread):
    """폰트를 로드하는 스레드 클래스"""
    loadSignal = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.exec()

    def exec(self):
        pythoncom.CoInitialize()
        try:
            self.font_list = ps.Application().fonts._fonts
            self.atr = self.parent.tempAtr
            if self.parent.selectedTIS == 'none':
                self.savePostscriptName('conversation')
                self.savePostscriptName('emphasis')
                self.savePostscriptName('narration')
                self.savePostscriptName('think')
                self.savePostscriptName('background')
                self.savePostscriptName('effect')
            else:
                for i in self.parent.f_list:
                    self.savePostscriptName(i)
            self.loadSignal.emit(True)
        except:
            self.loadSignal.emit(False)
        pythoncom.CoUninitialize()
        self.quit()

    def savePostscriptName(self, attribute):
        """postscript 이름을 태그별로 저장하는 함수"""
        if self.atr.attributes[attribute]['activate']:
            family = self.atr.attributes[attribute]['family']
            if family != 'none':
                self.atr.attributes[attribute]['font'] = self.getPostscriptName(
                    family)

    def getPostscriptName(self, family) -> str:
        """family를 받아 postscript 이름을 반환하는 함수"""
        # ff = open('test for fonts.txt', 'a', encoding='UTF8')
        try:  # strict하게 폰트 검사
            for f in self.font_list:
                # ff.write(f.name + '\n')
                if f.family == family:
                    print(f.family)
                    # ff.close()
                    return f.postScriptName
        except Exception as e:
            # ff.close()
            # print(str(e))
            pass
        try:  # in으로 검사 및 name의 마지막 문자 비교 (M, B 등의 구분)
            for f in self.font_list:
                if f.family in family:
                    if f.name[-1] == family[-1]:
                        print(f.family)
                        return f.postScriptName
        except:
            pass
        try:  # in으로만 검사
            for f in self.font_list:
                if f.family in family:
                    print(f.family)
                    return f.postScriptName
        except:
            pass
        # ff.close()
        return 'none'
