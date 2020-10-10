from os import name
import photoshop.api as ps
import pythoncom
from PyQt5.QtCore import pyqtSignal, QThread

"""
photoshop > api > _text_fonts.py > TextFonts
맨 아래줄에 자체 코드 삽입
    def getFontList(self):
        return [TextFont(font) for font in self.app]
"""

class LoadAndSaveFonts(QThread):
    """폰트를 로드하는 스레드 클래스"""
    loadSignal = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        self.exec()

    def exec(self):
        try:
            pythoncom.CoInitialize()
            self.font_list = ps.Application().fonts.getFontList()
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
                self.atr.attributes[attribute]['font'] = self.getPostscriptName(family)

    def getPostscriptName(self, family) -> str:
        """family를 받아 postscript 이름을 반환하는 함수"""
        # ff = open('test for fonts.txt', 'a', encoding='UTF8')
        for f in self.font_list:
            try:
                # ff.write(f.name + '\n')
                if f.family in family:  # 추후 세 단계로 수정, strict 체크 -> in 체크 + 마지막 글자 대조 -> in 체크 only
                    # ff.close()
                    return f.postScriptName
            except Exception as e:
                # ff.close()
                # print(str(e))
                pass
        # ff.close()
        return 'none'
