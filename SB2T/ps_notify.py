"""포토샵 알림(Notifier) 등록/해제 모듈 (5.0)

포토샵 모드가 '새 텍스트 레이어가 만들어졌다'를 알아내는 방법.

----------------------------------------------------------------------
왜 알림인가 (실측 기록)
----------------------------------------------------------------------
Beta4.0은 레이어 '이름'을 폴링해서 새 텍스트 레이어를 찾았다.
자리 표시자 텍스트 옵션을 끄면 이름이 안 맞아 동작하지 않았다.

5.0 개발 중에 마우스 동작으로 추론하는 방식도 시도했지만 실패했다.
드래그 길이, 기기 성능, 창 영역, 포커스 상태마다 예외가 끝없이 생겼고
기존 텍스트를 클릭해 수정하는 경우와 새로 만드는 경우를 구분할 수 없었다.

포토샵은 이걸 이미 구분해서 알려준다. 실측으로 확인한 이벤트:

    'Mk  ' + 'TxLr'  : 새 텍스트 레이어가 만들어짐   <- 우리가 쓰는 것
    'setd' / 'set'   : 기존 텍스트 레이어를 수정함   <- 무시해야 하는 것

참고로 아래는 확인해 봤지만 쓸 수 없었다.
  - createTextLayer / deleteTextLayer : 어도비 Design Space 내부 이벤트라
    스크립트 알림으로는 등록만 되고 전달되지 않는다
  - toolModalStateChanged : 마찬가지로 전달되지 않는다

----------------------------------------------------------------------
동작 방식
----------------------------------------------------------------------
1. 포토샵 모드를 켤 때 알림을 등록한다. 이벤트가 오면 포토샵이 우리가
   만들어 둔 .jsx를 실행하고, 그 스크립트는 로그 파일에 한 줄 남긴다.
2. 식붕이툴은 그 파일만 지켜본다. (COM 폴링이 없다)
3. 줄이 늘어나면 = 새 텍스트 레이어가 생겼으면, COM으로 내용을 채운다.

빈 텍스트 레이어는 Esc로 닫으면 포토샵이 삭제해 버리므로 이벤트가 오지
않는다. Ctrl+Enter로 닫거나, 자리 표시자 텍스트 옵션을 켜두면 된다.
"""

import os
import tempfile

# 새 텍스트 레이어 생성 이벤트
EVENT_MAKE = 'Mk  '
CLASS_TEXT_LAYER = 'TxLr'

WORK_DIR = os.path.join(tempfile.gettempdir(), 'sb2tool_ps')
LOG_PATH = os.path.join(WORK_DIR, 'textlayer.log')
JSX_PATH = os.path.join(WORK_DIR, 'sb2tool_notify.jsx')

# 이벤트가 오면 실행될 스크립트.
# 포토샵 안에서 도는 코드이므로 편집 중 COM 차단과 무관하다.
JSX_TEMPLATE = '''
var logFile = new File("%s");
logFile.encoding = "UTF-8";
logFile.open("a");
logFile.writeln("" + new Date().getTime());
logFile.close();
'''


def _to_jsx_path(path: str) -> str:
    """윈도우 경로를 ExtendScript가 알아듣는 형태로 바꾸는 함수"""
    return path.replace('\\', '/')


def prepare() -> None:
    """작업 폴더와 알림 스크립트를 준비하는 함수"""
    os.makedirs(WORK_DIR, exist_ok=True)
    with open(JSX_PATH, 'w', encoding='utf-8') as f:
        f.write(JSX_TEMPLATE % _to_jsx_path(LOG_PATH))


def clear_log() -> None:
    """이전에 쌓인 로그를 비우는 함수"""
    try:
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)
    except OSError:
        pass


def log_size() -> int:
    """로그 파일 크기를 얻는 함수 (변화 감지용)"""
    try:
        return os.path.getsize(LOG_PATH)
    except OSError:
        return 0


def install_notifier(app) -> str:
    """알림을 등록하는 함수. 실패 시 오류 메시지를 반환한다."""
    prepare()
    clear_log()
    script = '''
app.notifiersEnabled = true;
var target = new File("%s");
%s
app.notifiers.add("%s", target, "%s");
"ok";
''' % (_to_jsx_path(JSX_PATH), _REMOVE_OURS, EVENT_MAKE, CLASS_TEXT_LAYER)
    try:
        app.doJavaScript(script)
        return ''
    except Exception as e:
        return '포토샵 알림을 등록하지 못했습니다.\n' + str(e)


def uninstall_notifier(app) -> str:
    """등록했던 알림만 해제하는 함수

    removeAll()을 쓰지 않는다. 사용자가 직접 등록해 둔 알림까지
    지워버리면 안 되기 때문이다.
    """
    script = '''
var target = new File("%s");
%s
"ok";
''' % (_to_jsx_path(JSX_PATH), _REMOVE_OURS)
    try:
        app.doJavaScript(script)
        return ''
    except Exception as e:
        return str(e)


PLACEHOLDER_PREF = 'enablePlaceHolderText'


def read_placeholder_pref(app):
    """'자리 표시자 텍스트' 옵션이 켜져 있는지 확인하는 함수

    포토샵 모드는 이 옵션에 크게 의존한다. 꺼져 있으면 두 가지가 깨진다.

    1. 빈 텍스트 박스를 Esc로 닫으면 포토샵이 그 레이어를 삭제해 버린다.
       레이어가 없으니 생성 알림도 오지 않는다.
    2. 글자가 하나도 없는 레이어에는 문자 서식이 실리지 않는다. 나중에
       내용만 채워 넣으면 작업 중이던 글꼴/크기가 아니라 기본값이 적용된다.

    옵션을 켜두면 새 박스에 자리 표시자 글자가 먼저 들어가면서 현재 문자
    설정이 실리고, 레이어도 살아남는다. 내용만 갈아끼우면 서식이 유지된다.

    Returns:
        True / False / None (조회 실패)
    """
    script = '''
var ref = new ActionReference();
ref.putProperty(stringIDToTypeID("property"),
                stringIDToTypeID("typePreferences"));
ref.putEnumerated(stringIDToTypeID("application"),
                  stringIDToTypeID("ordinal"),
                  stringIDToTypeID("targetEnum"));
var d = executeActionGet(ref).getObjectValue(
    stringIDToTypeID("typePreferences"));
d.getBoolean(stringIDToTypeID("%s")) ? "1" : "0";
''' % PLACEHOLDER_PREF
    try:
        return str(app.doJavaScript(script)).strip() == '1'
    except Exception:
        return None


def set_placeholder_pref(app, enabled=True) -> str:
    """'자리 표시자 텍스트' 옵션을 켜거나 끄는 함수

    실패 시 오류 메시지를 반환한다.
    """
    script = '''
var desc = new ActionDescriptor();
var ref = new ActionReference();
ref.putProperty(stringIDToTypeID("property"),
                stringIDToTypeID("typePreferences"));
ref.putEnumerated(stringIDToTypeID("application"),
                  stringIDToTypeID("ordinal"),
                  stringIDToTypeID("targetEnum"));
desc.putReference(stringIDToTypeID("null"), ref);
var pref = new ActionDescriptor();
pref.putBoolean(stringIDToTypeID("%s"), %s);
desc.putObject(stringIDToTypeID("to"),
               stringIDToTypeID("typePreferences"), pref);
executeAction(stringIDToTypeID("set"), desc, DialogModes.NO);
"ok";
''' % (PLACEHOLDER_PREF, 'true' if enabled else 'false')
    try:
        app.doJavaScript(script)
    except Exception as e:
        return str(e)

    # 실제로 반영됐는지 되읽어서 확인한다
    if read_placeholder_pref(app) != enabled:
        return '설정은 실행됐지만 값이 바뀌지 않았습니다.'
    return ''


# 우리가 등록한 알림만 골라 지우는 자바스크립트 조각.
# 등록 전에도 한 번 돌려서, 비정상 종료로 남은 찌꺼기를 정리한다.
_REMOVE_OURS = '''
for (var i = app.notifiers.length - 1; i >= 0; i--) {
    try {
        var n = app.notifiers[i];
        var p = "";
        try { p = n.eventFile.fsName; } catch (e1) { p = "" + n.eventFile; }
        if (p == target.fsName || p == ("" + target)) {
            n.remove();
        }
    } catch (e2) {}
}
'''
