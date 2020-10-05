from pyautogui import hotkey, press
import keyboard
from threading import Thread


class MacroStartwithProcess:
    """매크로 멀티프로세스 클래스"""

    def __init__(self, macroList):
        macroListThread = []
        for i in range(len(macroList)):
            infolist = macroList[i].split('#&@&#')
            macroListThread.append(Thread(target=self.macroMultProc, args=(infolist, )))  # 프로세스 내에서 각 매크로 스레드 생성
            macroListThread[i].start()

    def macroMultProc(self, infolist):
        """매크로 실행 함수"""
        setKey = ''

        if infolist[1] != 'none':
            if infolist[2] != 'none':
                setKey = infolist[1] + '+' + infolist[2]
            else:
                setKey = infolist[1]

        if infolist[5] != '1':  # 활성화 여부 체크
            return

        while True:  # 조건 키 누를 때까지 대기
            try:
                if keyboard.is_pressed(setKey):
                    if infolist[3] != 'none':
                        if infolist[4] != 'none':
                            hotkey(infolist[3], infolist[4])
                        else:
                            press(infolist[3])
                    break
            except:
                pass

        while True:  # 조건 키 누른 후 뗄 때까지 대기
            try:
                if not keyboard.is_pressed(setKey):
                    break
            except:
                pass
        self.macroMultProc(infolist)    # 실행 후 다시 반복

