"""UI 기본 글꼴 모듈 (5.0 추가)

Beta4.0까지는 텍스트 라인에 패밀리를 지정하지 않은 `QFont()`를 그대로
적용했다. 이러면 한글이 시스템 폴백을 타면서 굴림으로 표시된다.
메뉴바나 제목은 멀쩡한데 내용물만 굴림으로 보이던 이유다.

5.0부터는 두 단계로 글꼴을 정한다.

1. `fonts/` 폴더에 들어 있는 글꼴 파일을 앱에 등록한다.
   설치하지 않아도 그 글꼴을 쓸 수 있다. 폴더가 비어 있으면 그냥 넘어간다.
2. 아래 후보 목록에서 (등록된 것 + 설치된 것 중) 첫 번째를 쓴다.

목록을 바꾸고 싶으면 UI_FONT_CANDIDATES만 고치면 된다.
"""

import os
import sys

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

# 앞에 있을수록 우선. 없으면 다음 것으로 넘어간다.
#   - Pretendard JP : fonts/ 폴더에 넣어 함께 배포한다. 설치가 필요 없다.
#                     일본어 글자도 들어 있어 원문을 같이 볼 때 유리하다.
#                     이름의 띄어쓰기까지 정확해야 한다 (글꼴 파일 내부 이름).
#   - Malgun Gothic : Windows Vista 이상 기본 탑재. 사실상의 보험
#   - 굴림은 일부러 넣지 않는다. 못 찾으면 Qt 기본값에 맡긴다.
UI_FONT_CANDIDATES = (
    'Pretendard JP',
    'Pretendard',
    'Noto Sans KR',
    'Malgun Gothic',
    '맑은 고딕',
)

FONT_DIR_NAME = 'fonts'
FONT_EXTENSIONS = ('.ttf', '.otf', '.ttc')

_loaded_families = None   # 한 번만 등록하도록 캐시


def _base_dir() -> str:
    """글꼴 폴더를 찾을 기준 경로를 반환하는 함수

    PyInstaller로 묶었을 때와 소스로 실행할 때의 위치가 다르다.
    """
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    # SB2T/ui_font.py -> 저장소 루트
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_bundled_fonts() -> list:
    """fonts/ 폴더의 글꼴 파일을 앱에 등록하는 함수

    사용자가 글꼴을 설치하지 않아도 쓸 수 있게 해준다.
    폴더가 없거나 비어 있으면 조용히 넘어간다.

    Returns:
        등록된 글꼴 이름 목록
    """
    global _loaded_families
    if _loaded_families is not None:
        return _loaded_families

    _loaded_families = []
    font_dir = os.path.join(_base_dir(), FONT_DIR_NAME)
    if not os.path.isdir(font_dir):
        return _loaded_families

    for name in sorted(os.listdir(font_dir)):
        if not name.lower().endswith(FONT_EXTENSIONS):
            continue
        try:
            font_id = QFontDatabase.addApplicationFont(
                os.path.join(font_dir, name))
        except Exception:
            continue
        if font_id == -1:
            continue  # 손상됐거나 Qt가 못 읽는 형식
        for family in QFontDatabase.applicationFontFamilies(font_id):
            if family not in _loaded_families:
                _loaded_families.append(family)
    return _loaded_families


def find_ui_font_family() -> str:
    """쓸 만한 글꼴을 찾아 이름을 반환하는 함수

    하나도 없으면 빈 문자열을 반환한다. (Qt 기본값을 그대로 쓴다는 뜻)
    QApplication이 만들어진 뒤에 불러야 한다.
    """
    load_bundled_fonts()
    try:
        available = set(QFontDatabase().families())
    except Exception:
        return ''
    for name in UI_FONT_CANDIDATES:
        if name in available:
            return name
    return ''


def make_ui_font(point_size=0) -> QFont:
    """UI 기본 글꼴을 만드는 함수

    Args:
        point_size: 0이면 현재 앱 글꼴 크기를 그대로 쓴다.
                    시스템 설정(배율 등)을 존중하기 위해 기본값을 0으로 둔다.
    """
    font = QFont(QApplication.font())
    family = find_ui_font_family()
    if family:
        font.setFamily(family)
    if point_size > 0:
        font.setPointSize(point_size)
    return font


def apply_app_font() -> str:
    """앱 전체 기본 글꼴을 적용하는 함수

    이걸 해두면 설정 창, 안내 창, 버튼 등 모든 위젯이 같은 글꼴을 쓴다.
    위젯마다 따로 지정할 필요가 없다.

    Returns:
        적용한 글꼴 이름 (못 찾았으면 빈 문자열)
    """
    family = find_ui_font_family()
    if not family:
        return ''
    font = QFont(QApplication.font())
    font.setFamily(family)
    QApplication.setFont(font)
    return family
