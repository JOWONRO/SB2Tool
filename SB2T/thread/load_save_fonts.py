import photoshop.api as ps
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
            self.font_list = ps.Application().fonts.getFontList()
            self.atr = self.parent.tempAtr
            self.savePostscriptName('conversation')
            self.savePostscriptName('emphasis')
            self.savePostscriptName('narration')
            self.savePostscriptName('think')
            self.savePostscriptName('background')
            self.savePostscriptName('effect')

            self.loadSignal.emit(True)
        except:
            self.loadSignal.emit(False)
        self.quit()

    def savePostscriptName(self, attribute):
        """postscript 이름을 태그별로 저장하는 함수"""
        if self.atr.attributes[attribute]['activate']:
            family = self.atr.attributes[attribute]['family']
            if family != 'none':
                self.atr.attributes[attribute]['font'] = self.getPostscriptName(family)

    def getPostscriptName(self, family) -> str:
        """family를 받아 postscript 이름을 반환하는 함수"""
        for f in self.font_list:
            try:
                if f.family == family:
                    return f.postScriptName
            except:
                print('pass')
                pass
        return 'none'
