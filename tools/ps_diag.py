"""포토샵 COM 연결 진단 스크립트

'포토샵 연동에 실패했습니다 / Please check if you have Photoshop installed
correctly.' 가 뜰 때 원인을 좁히기 위한 도구.

어느 방식으로 연결이 되는지, 레지스트리에 어떤 버전이 등록돼 있는지,
권한이 어긋나 있는지를 한 번에 찍어준다.

--------------------------------------------------------------------------
사용법
--------------------------------------------------------------------------
    포토샵을 먼저 실행해 둔 상태에서

        .venv\\Scripts\\activate
        python tools\\ps_diag.py

    시간이 좀 걸릴 수 있다. CreateObject 계열은 실패할 때
    포토샵을 새로 띄우려다 몇 분씩 멎기도 한다. 그대로 두고 기다릴 것.

    관리자 권한 콘솔에서도 한 번 더 돌려서 결과를 비교하면 좋다.
    포토샵과 식붕이툴의 권한이 다르면 COM으로 붙지 못한다.
"""

import ctypes
import os
import sys
import time
import winreg


def line(title=''):
    print('\n' + '=' * 70)
    if title:
        print(title)
        print('=' * 70)


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def check_env():
    line('1. 실행 환경')
    print('  파이썬     :', sys.version.split()[0], '(%d bit)' % (8 * 8 if sys.maxsize > 2**32 else 32))
    print('  관리자 권한 :', '예' if is_admin() else '아니오')
    print('  실행 파일   :', sys.executable)


def check_process():
    line('2. 포토샵 프로세스')
    try:
        import psutil
    except ImportError:
        print('  psutil 없음 - 건너뜀')
        return
    found = []
    for p in psutil.process_iter(['name', 'pid', 'exe']):
        try:
            if 'photoshop' in (p.info['name'] or '').lower():
                found.append(p.info)
        except Exception:
            pass
    if not found:
        print('  !! 실행 중인 포토샵 프로세스가 없습니다.')
        print('     포토샵을 먼저 켜고 다시 실행하세요.')
    for f in found:
        print('  pid %-8s %s' % (f['pid'], f['name']))
        print('           %s' % (f.get('exe') or ''))


def check_registry():
    line('3. 레지스트리 등록 버전 (HKLM\\SOFTWARE\\Adobe\\Photoshop)')
    print('  photoshop_python_api가 이 목록을 읽어 ProgID를 만든다.')
    access = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
    versions = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             'SOFTWARE\\Adobe\\Photoshop', access=access)
        count = winreg.QueryInfoKey(key)[0]
        for i in range(count):
            name = winreg.EnumKey(key, i)
            versions.append(name)
            path = ''
            try:
                sub = winreg.OpenKey(key, name, access=access)
                path = winreg.QueryValueEx(sub, 'ApplicationPath')[0]
            except Exception:
                pass
            print('  %-10s %s' % (name, path))
    except FileNotFoundError:
        print('  !! 키가 없습니다. 포토샵이 이 PC에 등록돼 있지 않습니다.')
    except Exception as e:
        print('  읽기 실패:', e)
    return [v.split('.')[0] for v in versions]


def try_connect(label, fn):
    """연결 시도 하나를 재보는 함수"""
    started = time.time()
    try:
        obj = fn()
        elapsed = time.time() - started
        ver = ''
        try:
            ver = ' / version=%s' % obj.Version
        except Exception:
            pass
        print('  [성공] %-45s %5.1f초%s' % (label, elapsed, ver))
        return obj
    except Exception as e:
        elapsed = time.time() - started
        msg = str(e).replace('\n', ' ')[:60]
        print('  [실패] %-45s %5.1f초  %s' % (label, elapsed, msg))
        return None


def check_com(versions):
    line('4. COM 연결 시도')
    import win32com.client

    print('  -- GetActiveObject (실행 중인 인스턴스에 붙기, 빠름) --')
    try_connect('GetActiveObject("Photoshop.Application")',
                lambda: win32com.client.GetActiveObject('Photoshop.Application'))
    for v in versions:
        progid = 'Photoshop.Application.%s' % v
        try_connect('GetActiveObject("%s")' % progid,
                    lambda p=progid: win32com.client.GetActiveObject(p))

    print('\n  -- Dispatch (없으면 새로 띄움, 느릴 수 있음) --')
    try_connect('Dispatch("Photoshop.Application")',
                lambda: win32com.client.Dispatch('Photoshop.Application'))

    print('\n  -- photoshop_python_api --')
    import photoshop.api as ps
    try_connect('ps.Application()', lambda: ps.Application())


def main():
    os.environ.setdefault('PS_DEBUG', 'true')  # 라이브러리 내부 로그 켜기
    import pythoncom
    pythoncom.CoInitialize()
    try:
        check_env()
        check_process()
        versions = check_registry()
        check_com(versions)
    finally:
        pythoncom.CoUninitialize()
    line('끝. 위 내용을 그대로 복사해서 전달해 주세요.')


if __name__ == '__main__':
    main()
