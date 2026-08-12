import keyboard
from PyQt5.QtCore import QThread, pyqtSignal


def build_hotkey(keys) -> str:
    """지정된 키 목록을 keyboard 모듈이 알아듣는 문자열로 합치는 함수

    예) ['ctrl', 'f1'] -> 'ctrl+f1'  /  ['f1', ''] -> 'f1'
    '+' 키는 구분자와 헷갈리므로 'plus'라는 이름으로 바꿔준다.
    """
    parts = []
    for key in keys:
        if not key or key == 'none':
            continue
        parts.append('plus' if key == '+' else key)
    return '+'.join(parts)


class GlobalHotkey(QThread):
    """대사 이동 전역 단축키 스레드 클래스 (5.0 추가)

    Ctrl+V 자동 감지와 별개로, 사용자가 지정한 키로 대사를 직접 옮길 수 있게 한다.
    - 붙여넣기가 씹혔을 때 현재 대사를 다시 복사
    - 실수로 넘어갔을 때 이전 대사로 복귀
    - 효과음/손글씨처럼 건너뛸 줄을 지나칠 때 다음 대사로 이동

    Ctrl+V를 다른 용도로 써야 하는 경우에도 이 단축키만으로 작업할 수 있다.
    """
    nextLineSignal = pyqtSignal()
    prevLineSignal = pyqtSignal()
    recopyLineSignal = pyqtSignal()

    def __init__(self, parent=None, nextKey='', prevKey='', recopyKey=''):
        super().__init__(parent)
        self._keys = {
            nextKey: self.nextLineSignal,
            prevKey: self.prevLineSignal,
            recopyKey: self.recopyLineSignal,
        }
        self._handles = []

    def run(self):
        self.exec()

    def exec(self):
        """지정된 단축키를 등록하고 대기하는 함수"""
        for key, signal in self._keys.items():
            if not key or key == 'none':
                continue
            try:
                # 콜백에서 곧바로 UI를 건드리면 스레드 문제가 생기므로
                # 시그널만 쏘고 처리는 메인 스레드에 맡긴다.
                self._handles.append(
                    keyboard.add_hotkey(key, signal.emit, suppress=False))
            except Exception:
                pass  # 인식할 수 없는 키 조합은 건너뛴다
        keyboard.wait()

    def disconnect(self):
        """등록한 단축키만 해제하는 함수"""
        for handle in self._handles:
            try:
                keyboard.remove_hotkey(handle)
            except (KeyError, ValueError):
                pass
        self._handles.clear()
