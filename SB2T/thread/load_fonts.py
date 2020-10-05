import photoshop.api as ps
from PyQt5.QtCore import pyqtSignal, QThread

"""
photoshop > api > _text_fonts.py > TextFonts
맨 아래줄에 자체 코드 삽입
    def getFontList(self):
        return [TextFont(font) for font in self.app]
"""

class LoadFonts(QThread):
    loadSignal = pyqtSignal(list)

    def run(self):
        self.exec()

    def exec(self):
        font_list = ps.Application().fonts.getFontList()
        self.loadSignal.emit(font_list)
        self.quit()

