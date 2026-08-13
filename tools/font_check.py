"""번들 글꼴 등록 확인 스크립트

fonts/ 폴더의 글꼴이 실제로 Qt에 등록되는지, 최종적으로 어떤 글꼴이
선택되는지 확인한다. 글꼴이 굴림으로 보일 때 원인을 좁히는 용도.

--------------------------------------------------------------------------
사용법
--------------------------------------------------------------------------
    .venv\\Scripts\\activate
    python tools\\font_check.py
"""

import os
import sys

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, '.')

from SB2T.ui_font import (FONT_DIR_NAME, UI_FONT_CANDIDATES, _base_dir,
                          apply_app_font, find_ui_font_family,
                          load_bundled_fonts)


def main():
    app = QApplication(sys.argv)

    print('=== fonts 폴더 ===')
    font_dir = os.path.join(_base_dir(), FONT_DIR_NAME)
    print('  경로: %s' % font_dir)
    if os.path.isdir(font_dir):
        total = 0
        for n in sorted(os.listdir(font_dir)):
            size = os.path.getsize(os.path.join(font_dir, n))
            total += size
            print('    %-32s %8.2f MB' % (n, size / 1024 / 1024))
        print('  합계 %.2f MB' % (total / 1024 / 1024))
    else:
        print('  !! 폴더가 없습니다')

    print()
    print('=== 등록된 글꼴 ===')
    families = load_bundled_fonts()
    if families:
        for f in families:
            print('    %s' % f)
    else:
        print('    없음 (파일이 없거나 Qt가 읽지 못함)')

    print()
    print('=== 후보 목록 검사 ===')
    from PyQt5.QtGui import QFontDatabase
    available = set(QFontDatabase().families())
    for name in UI_FONT_CANDIDATES:
        print('    %-18s %s' % (name, 'O' if name in available else '-'))

    print()
    chosen = find_ui_font_family()
    print('=== 선택된 글꼴: %s ===' % (chosen or '(Qt 기본값)'))

    applied = apply_app_font()
    print('앱 전체 적용: %s' % (applied or '적용 안 함'))
    print('실제 앱 글꼴: %s %dpt'
          % (QApplication.font().family(), QApplication.font().pointSize()))

    # 굵기가 실제로 있는지 (Bold 파일이 제대로 등록됐는지)
    if chosen:
        styles = QFontDatabase().styles(chosen)
        print('사용 가능한 굵기: %s' % (', '.join(styles) or '없음'))


if __name__ == '__main__':
    main()
