import time

from PyQt5.QtCore import QThread, pyqtSignal

from SB2T.ps_notify import log_size

# 알림 로그 파일 확인 간격(초). 파일 크기만 보므로 COM 호출이 없다.
POLL_INTERVAL = 0.05


class StartPsThread(QThread):
    """포토샵 알림을 지켜보는 스레드 클래스

    ----------------------------------------------------------------------
    Beta4.0에서 무엇이 바뀌었나
    ----------------------------------------------------------------------
    4.0은 COM으로 활성 레이어 이름을 쉬지 않고 폴링해서 새 텍스트 레이어를
    찾았다. 세 가지 문제가 있었다.

    1. 자리 표시자 텍스트 옵션을 끄면 이름이 매칭되지 않아 동작하지 않았다
       (전가의보도 님 제보)
    2. 쉬는 시간 없는 폴링이라 CPU를 계속 먹고 포토샵도 굼떠졌다
    3. 기존 텍스트 레이어를 수정하는 경우와 구분하지 못했다

    5.0은 포토샵이 보내주는 알림을 쓴다. 포토샵이 '새 텍스트 레이어를
    만들었다'고 직접 알려주므로 추론이 필요 없다. 기존 레이어 수정은
    다른 이벤트('set')로 오기 때문에 애초에 걸리지 않는다.

    이 스레드가 하는 일은 알림 스크립트가 남긴 로그 파일이 늘어났는지
    확인하는 것뿐이다. COM 호출이 전혀 없어서 포토샵에 부담을 주지 않는다.
    자세한 내용은 SB2T/ps_notify.py 참고.
    """
    psTextLayerCreated = pyqtSignal()  # 새 텍스트 레이어가 만들어짐

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    def run(self):
        self.exec()

    def exec(self):
        """알림 로그가 늘어나는지 지켜보는 함수"""
        lastSize = log_size()
        while not self._stop:
            size = log_size()
            if size > lastSize:
                lastSize = size
                self.psTextLayerCreated.emit()
            elif size < lastSize:
                lastSize = size  # 로그가 비워진 경우
            time.sleep(POLL_INTERVAL)

    def stop(self):
        """감시를 멈추는 함수"""
        self._stop = True
