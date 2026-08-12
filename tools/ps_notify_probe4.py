"""포토샵 알림 - 이벤트 ID 표기법 검증 스크립트

probe2, probe3에서 등록은 성공했는데 이벤트가 하나도 오지 않았다.
그런데 probe1은 잘 왔다. 둘의 차이는 넘긴 값의 형태다.

    probe1 : app.notifiers.add("Mk  ", f, "TxLr")        <- 문자열. 동작함
    probe2 : app.notifiers.add(stringIDToTypeID("..."), f)  <- 정수. 안 옴
    probe3 : app.notifiers.add(stringIDToTypeID("..."), f)  <- 정수. 안 옴

stringIDToTypeID()는 정수를 돌려준다. notifiers.add()가 정수를 받고도
등록 개수는 올렸지만 실제로는 매칭되지 않는 값이 들어갔을 수 있다.
'등록은 되는데 이벤트가 안 온다'는 증상이 딱 그 모양이다.

그래서 이번엔
  1. 전부 **문자열**로 넘긴다
  2. **대조군('Mk  ')**을 같이 넣는다.
     대조군이 오고 나머지가 안 오면 그 이벤트 이름이 지원되지 않는 것이고,
     대조군마저 안 오면 등록 방식 자체가 잘못된 것이다
  3. 등록 후 실제로 무엇이 등록됐는지 목록을 뽑아서 확인한다

--------------------------------------------------------------------------
사용법
--------------------------------------------------------------------------
    포토샵을 켜고 문서를 하나 연 상태에서 (관리자 권한 아님!)

        .venv\\Scripts\\activate
        python tools\\ps_notify_probe4.py

    등록 결과와 등록 목록이 먼저 나온다. 그다음:

      1. 캔버스에 드래그해서 박스 생성 (Esc 금지)  <- 만들기가 오는가
      2. 빈 채로 Esc                              <- 삭제가 오는가
      3. 다시 만들고 글자 쓰고 Esc                  <- 대조군이 오는가
      4. 기존 텍스트 레이어를 클릭해서 수정 후 Esc    <- 만들기가 오면 안 됨
      5. 레이어 패널 클릭 / 붓 도구                 <- 아무것도 오면 안 됨

    Ctrl+C로 종료하면 등록한 알림을 정리한다.
"""

import os
import sys
import tempfile
import time

import pythoncom

sys.path.insert(0, '.')

from SB2T.ps_connect import connect_photoshop


WORK_DIR = os.path.join(tempfile.gettempdir(), 'sb2tool_notify_probe4')
LOG_PATH = os.path.join(WORK_DIR, 'events.log')

# (이름표, 이벤트 문자열, 클래스 문자열 또는 None)
CANDIDATES = [
    ('대조군 Mk  /TxLr', 'Mk  ', 'TxLr'),
    ('createTextLayer', 'createTextLayer', None),
    ('deleteTextLayer', 'deleteTextLayer', None),
    ('setd(4자)', 'setd', None),
    ('set(문자열)', 'set', None),
]


def to_jsx_path(path: str) -> str:
    """윈도우 경로를 ExtendScript가 알아듣는 형태로 바꾸는 함수"""
    return path.replace('\\', '/')


def write_jsx(tag: str, idx: int) -> str:
    """이벤트가 오면 로그에 한 줄 남기는 스크립트를 만드는 함수"""
    path = os.path.join(WORK_DIR, 'notify_%d.jsx' % idx)
    jsx = '''
var logFile = new File("%s");
logFile.encoding = "UTF-8";
logFile.open("a");
var msg = "%s";
try { msg = msg + "\\ttool=" + app.currentTool; }
catch (e) { msg = msg + "\\ttool=(읽기실패)"; }
try {
    var layer = app.activeDocument.activeLayer;
    msg = msg + "\\tlayer=" + layer.name + "\\tkind=" + layer.kind;
} catch (e2) {
    msg = msg + "\\tlayer=(읽기실패)";
}
logFile.writeln(msg);
logFile.close();
''' % (to_jsx_path(LOG_PATH), tag)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(jsx)
    return path


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)

    pythoncom.CoInitialize()
    app, method, err = connect_photoshop()
    if app is None:
        print('[연결 실패]')
        print(err)
        return
    print('연결 성공 - 방식: %s' % method)

    # 이전 프로브 찌꺼기가 남아 있을 수 있으니 먼저 비운다
    try:
        app.doJavaScript('app.notifiers.removeAll();')
    except Exception:
        pass

    print()
    print('알림 등록 결과')
    print('-' * 62)

    registered = 0
    for idx, (tag, event, klass) in enumerate(CANDIDATES):
        jsx_path = write_jsx(tag, idx)
        if klass:
            add = 'app.notifiers.add("%s", f, "%s");' % (event, klass)
        else:
            add = 'app.notifiers.add("%s", f);' % event
        script = '''
app.notifiersEnabled = true;
var f = new File("%s");
%s
"ok:" + app.notifiers.length;
''' % (to_jsx_path(jsx_path), add)
        try:
            result = app.doJavaScript(script)
            print('  [성공] %-20s %s' % (tag, result))
            registered += 1
        except Exception as e:
            print('  [실패] %-20s %s' % (tag, str(e).replace('\n', ' ')[:36]))

    # 실제로 무엇이 등록됐는지 확인 (등록은 됐다는데 안 올 때 단서가 된다)
    print()
    print('등록된 알림 목록')
    print('-' * 62)
    try:
        dump = app.doJavaScript('''
var out = "";
for (var i = 0; i < app.notifiers.length; i++) {
    var n = app.notifiers[i];
    out = out + i + ") event=[" + n.event + "]";
    try { out = out + " class=[" + n.eventClass + "]"; } catch (e) {}
    out = out + "\\n";
}
out;
''')
        print(dump)
    except Exception as e:
        print('  목록 조회 실패: %s' % e)

    if not registered:
        try:
            app.doJavaScript('app.notifiers.removeAll();')
        except Exception:
            pass
        pythoncom.CoUninitialize()
        return

    print('아래를 순서대로 해보세요. (Ctrl+C 로 종료)')
    print('  1.박스 드래그 생성(Esc 금지)  2.빈 채로 Esc  3.글자 쓰고 Esc')
    print('  4.기존 텍스트 레이어 수정      5.레이어 패널/붓 도구')
    print('-' * 78)

    t0 = time.time()
    seen = 0
    try:
        while True:
            if os.path.exists(LOG_PATH):
                try:
                    with open(LOG_PATH, encoding='utf-8',
                              errors='replace') as f:
                        lines = f.read().splitlines()
                except Exception:
                    lines = []
                while seen < len(lines):
                    print('%7.2f  %s' % (time.time() - t0, lines[seen]))
                    seen += 1
            time.sleep(0.05)
    except KeyboardInterrupt:
        print('\n종료 중...')
    finally:
        try:
            app.doJavaScript('app.notifiers.removeAll(); "ok";')
            print('알림 정리 완료.')
        except Exception as e:
            print('알림 정리 실패: %s' % e)
            print('포토샵의 [파일 > 스크립트 > 스크립트 이벤트 관리자]에서 지워주세요.')
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
