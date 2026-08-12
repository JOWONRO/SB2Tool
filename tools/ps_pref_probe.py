"""포토샵 문자 환경설정 조회/변경 가능성 진단 스크립트

포토샵 모드는 '새 텍스트 레이어 생성' 알림에 의존한다. 그런데 자리 표시자
텍스트 옵션이 꺼져 있으면 빈 박스를 Esc로 닫을 때 포토샵이 그 레이어를
삭제해 버려서 알림이 오지 않는다.

그래서 이 옵션의 상태를 프로그램이 알 수 있는지, 나아가 켜줄 수 있는지
확인한다. 가능하면 꺼져 있을 때만 안내를 띄우고 바로 켜줄 수 있다.

이름을 추측하지 않고 **문자 환경설정 항목을 통째로 덤프**해서 실제 키를 찾는다.

--------------------------------------------------------------------------
사용법
--------------------------------------------------------------------------
    포토샵을 켠 상태에서 (관리자 권한 아님!)

        .venv\\Scripts\\activate
        python tools\\ps_pref_probe.py

    출력된 목록에서 자리 표시자(placeholder) 관련 항목을 찾는다.
    이름에 'placeholder'가 들어간 항목이 있으면 자동으로 표시해 준다.

    확인을 위해, 포토샵의
      [편집 > 환경 설정 > 문자] (또는 [Photoshop > 설정 > 문자])
    에서 '자리 표시자 텍스트로 새로운 유형 레이어 채우기'를 켰다 껐다 하며
    두 번 실행해서 값이 바뀌는 항목을 대조하면 확실하다.
"""

import sys

import pythoncom

sys.path.insert(0, '.')

from SB2T.ps_connect import connect_photoshop


DUMP_SCRIPT = '''
function dumpDesc(desc) {
    var out = "";
    for (var i = 0; i < desc.count; i++) {
        var k = desc.getKey(i);
        var name = typeIDToStringID(k);
        if (!name) { name = "(" + k + ")"; }
        var t = desc.getType(k);
        var v;
        try {
            if (t == DescValueType.BOOLEANTYPE) { v = desc.getBoolean(k); }
            else if (t == DescValueType.INTEGERTYPE) { v = desc.getInteger(k); }
            else if (t == DescValueType.LARGEINTEGERTYPE) { v = desc.getLargeInteger(k); }
            else if (t == DescValueType.DOUBLETYPE) { v = desc.getDouble(k); }
            else if (t == DescValueType.STRINGTYPE) { v = desc.getString(k); }
            else if (t == DescValueType.ENUMERATEDTYPE) { v = typeIDToStringID(desc.getEnumerationValue(k)); }
            else { v = "<" + t + ">"; }
        } catch (e) { v = "(읽기실패)"; }
        out = out + name + " = " + v + "\\n";
    }
    return out;
}

function getPref(propName) {
    var ref = new ActionReference();
    ref.putProperty(stringIDToTypeID("property"), stringIDToTypeID(propName));
    ref.putEnumerated(stringIDToTypeID("application"),
                      stringIDToTypeID("ordinal"),
                      stringIDToTypeID("targetEnum"));
    var d = executeActionGet(ref);
    return d.getObjectValue(stringIDToTypeID(propName));
}

var result = "";
var names = ["typePreferences", "generalPreferences"];
for (var n = 0; n < names.length; n++) {
    result = result + "===== " + names[n] + " =====\\n";
    try {
        result = result + dumpDesc(getPref(names[n]));
    } catch (e) {
        result = result + "(조회 실패: " + e + ")\\n";
    }
    result = result + "\\n";
}
result;
'''


def main():
    pythoncom.CoInitialize()
    app, method, err = connect_photoshop()
    if app is None:
        print('[연결 실패]')
        print(err)
        return
    print('연결 성공 - 방식: %s' % method)
    print()

    try:
        dump = app.doJavaScript(DUMP_SCRIPT)
    except Exception as e:
        print('환경설정 조회 실패: %s' % e)
        print()
        print('이 방법으로는 설정을 읽을 수 없습니다.')
        pythoncom.CoUninitialize()
        return

    print(dump)

    print('=' * 62)
    print('자리 표시자 관련으로 보이는 항목')
    print('=' * 62)
    hits = []
    for line in str(dump).splitlines():
        low = line.lower()
        if 'placeholder' in low or 'lorem' in low or 'filltype' in low:
            hits.append(line)
    if hits:
        for h in hits:
            print('  >>> %s' % h)
        print()
        print('위 이름을 쓰면 상태를 읽고 켜줄 수 있습니다.')
    else:
        print('  없음.')
        print()
        print('이 목록에 없다면 스크립트로 다룰 수 없는 설정입니다.')
        print('포토샵에서 옵션을 켰다 껐다 하며 두 번 돌려서,')
        print('값이 바뀌는 항목이 있는지 대조해 보세요.')

    pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
