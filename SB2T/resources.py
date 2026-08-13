"""번들 리소스 경로 모듈 (5.0 추가)

아이콘과 글꼴처럼 프로그램과 함께 배포되는 파일의 위치를 찾는다.

Beta4.0까지는 `QIcon('icons/setmacro.png')`처럼 상대경로를 그대로 썼다.
상대경로는 '현재 작업 폴더' 기준이라, 실행 위치가 설치 폴더가 아니면
아이콘을 하나도 못 찾는다. 바로가기의 시작 위치가 비어 있거나 다른
폴더에서 실행하면 그렇게 된다.

그래서 실행 파일(또는 저장소 루트) 기준으로 경로를 만든다.
"""

import os
import sys

from PyQt5.QtGui import QIcon

ICON_DIR_NAME = 'icons'


def base_dir() -> str:
    """리소스를 찾을 기준 경로를 반환하는 함수

    PyInstaller로 묶었을 때와 소스로 실행할 때의 위치가 다르다.
    """
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    # SB2T/resources.py -> 저장소 루트
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def res_path(*parts) -> str:
    """번들 리소스의 전체 경로를 만드는 함수"""
    return os.path.join(base_dir(), *parts)


def icon(name: str) -> QIcon:
    """icons 폴더의 아이콘을 불러오는 함수

    Args:
        name: 파일 이름만. 예) 'setmacro.png'
    """
    return QIcon(res_path(ICON_DIR_NAME, name))
