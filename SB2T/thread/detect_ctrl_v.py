import keyboard
from PyQt5.QtCore import QThread, pyqtSignal


class DetectCtrlV(QThread):
    """붙여넣기 키(기본 Ctrl+V) 감지 스레드 클래스

    Beta4.0까지는 V 키를 '누른 순간'(key down) 신호를 쏘고 곧바로 클립보드를
    다음 대사로 덮어썼다. 대상 프로그램이 클립보드를 읽는 시점은 비동기라서,
    덮어쓰기가 먼저 끝나면 다음 대사가 붙고 현재 대사는 건너뛰는 문제가 있었다.
    (클립스튜디오처럼 클립보드 읽기가 느린 프로그램에서 특히 자주 발생)

    그래서 5.0부터는 키를 '뗀 시점'(key up)에 신호를 쏜다. 대상 프로그램이
    붙여넣기를 시작할 시간을 벌어주기 때문에 건너뛰기/중복이 크게 줄어든다.
    """
    detectCtrlVSignal = pyqtSignal(bool)

    def __init__(self, parent=None, key='v', modifier='ctrl'):
        super().__init__(parent)
        self._key = key
        self._modifier = modifier
        self._hook = None
        # 키를 누르고 있으면 OS가 down 이벤트를 계속 쏜다(auto-repeat).
        # 'down 한 번 -> up 한 번'을 한 쌍으로만 인정해서 중복 발사를 막는다.
        self._armed = False

    def run(self):
        self.exec()

    def exec(self):
        """붙여넣기 키 훅을 걸고 대기하는 함수"""
        self._armed = False
        self._hook = keyboard.hook_key(self._key, self._onKeyEvent)
        keyboard.wait()

    def _onKeyEvent(self, event):
        """붙여넣기 키 이벤트 처리 함수"""
        if event.event_type == keyboard.KEY_DOWN:
            if self._armed:
                return  # auto-repeat 무시
            # 좌/우 Ctrl 모두 인식된다.
            # (기존에는 'ctrl' 훅이 왼쪽 Ctrl만 잡아서 오른쪽 Ctrl+V가 씹혔다)
            if keyboard.is_pressed(self._modifier):
                self._armed = True
        elif event.event_type == keyboard.KEY_UP:
            if self._armed:
                self._armed = False
                self.detectCtrlVSignal.emit(True)

    def disconnect(self):
        """걸어둔 훅만 해제하는 함수

        기존에는 keyboard.unhook_all()로 전역 훅을 전부 날려서
        매크로 모드 등 다른 기능의 훅까지 같이 해제될 여지가 있었다.
        """
        self._armed = False
        if self._hook is not None:
            try:
                keyboard.unhook(self._hook)
            except (KeyError, ValueError):
                pass
            self._hook = None
