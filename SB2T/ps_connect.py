"""포토샵 COM 연결 공통 모듈 (5.0 추가)

photoshop_python_api의 `ps.Application()`은 내부적으로 comtypes의
`CreateObject`를 쓴다. 이건 '실행 중인 인스턴스에 붙기'가 아니라
'COM 서버를 띄우기'라서, 붙는 데 실패하면 포토샵을 새로 실행하려고 든다.
포토샵은 그게 몇 분 걸리고, 그동안 호출한 쪽은 통째로 멎는다.
게다가 레지스트리에 등록된 버전마다 이 시도를 반복한다.

그래서 순서를 뒤집는다.

1. `GetActiveObject` - 이미 떠 있는 포토샵에만 붙는다. 즉시 성공하거나
   즉시 실패하므로 오래 멎는 일이 없다. 정상적인 사용 상황(포토샵을 켜놓고
   식자 작업)에서는 거의 항상 이쪽에서 끝난다.
2. `ps.Application()` - 1번이 안 될 때만. 기존 동작.
"""

import ctypes

import photoshop.api as ps
import win32com.client


PROG_ID = "Photoshop.Application"


def is_elevated() -> bool:
    """현재 프로세스가 관리자 권한으로 실행 중인지 확인하는 함수"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def is_photoshop_running() -> bool:
    """포토샵 프로세스가 떠 있는지 확인하는 함수"""
    try:
        from psutil import process_iter
        for p in process_iter(['name']):
            if 'photoshop' in (p.info['name'] or '').lower():
                return True
    except Exception:
        pass
    return False


def diagnose() -> str:
    """연결 실패 원인을 짚어주는 안내 문구를 만드는 함수

    COM은 무결성 수준(관리자/일반)별로 격리돼 있어서, 포토샵과 식붕이툴의
    권한이 다르면 서로를 아예 찾지 못한다. 이때 나오는 오류 메시지가
    '포토샵이 제대로 설치됐는지 확인하세요'라서 원인을 짐작하기 어렵다.
    그래서 상황을 판별해 구체적으로 알려준다.
    """
    if not is_photoshop_running():
        return ('포토샵이 실행되고 있지 않습니다.\n'
                '포토샵을 먼저 켠 뒤 다시 시도해 주세요.')

    if is_elevated():
        return ('포토샵은 실행 중인데 연결하지 못했습니다.\n'
                '식붕이툴이 "관리자 권한"으로 실행 중입니다.\n\n'
                '포토샵과 권한이 다르면 서로를 찾지 못합니다.\n'
                '식붕이툴을 일반 권한으로 다시 실행해 보세요.')

    return ('포토샵은 실행 중인데 연결하지 못했습니다.\n'
            '포토샵이 "관리자 권한"으로 실행 중일 수 있습니다.\n\n'
            '포토샵과 권한이 다르면 서로를 찾지 못합니다.\n'
            '포토샵을 일반 권한으로 다시 켜거나,\n'
            '식붕이툴도 관리자 권한으로 실행해 보세요.')


def connect_photoshop():
    """포토샵 COM 객체를 얻는 함수

    Returns:
        (app, method, error)
        app이 None이면 실패이며 error에 시도별 사유가 담긴다.
    """
    # 1) 붙을 수 있는지 먼저 빠르게 확인한다.
    #    GetActiveObject는 실행 중인 인스턴스만 찾으므로 즉시 성공/실패한다.
    #    여기서 실패하는데도 ps.Application()을 부르면, 포토샵을 새로 띄우려다
    #    수십 초씩 멎는다. 그래서 아예 시도하지 않고 바로 원인을 알려준다.
    try:
        probe = win32com.client.GetActiveObject(PROG_ID)
    except Exception:
        return None, '', diagnose()

    # 2) 실제로 사용할 객체는 photoshop_python_api 쪽으로 만든다.
    #    나머지 코드(app.currentTool 등)가 이 래퍼를 전제로 쓰여 있어서,
    #    생짜 COM 객체를 넘기면 속성 이름이 통하지 않는다.
    #    1번이 성공한 뒤라 이 호출도 즉시 끝난다.
    try:
        return ps.Application(), 'photoshop_python_api', ''
    except Exception:
        return probe, 'GetActiveObject', ''
