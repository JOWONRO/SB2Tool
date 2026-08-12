# 식붕이툴 5.0 작업 계획

작성일: 2026-08-11
대상: [버그 제보 시트](https://docs.google.com/spreadsheets/d/1L4ai00inqZpMqeJuhz7bOCdrWgMTYHEZKl7EXY-nHqM/edit) Beta4.0 탭

시트 판독 규칙: **회색 처리 = 이미 해결된 항목**, **제보자가 '고리성운' = 작성 예시라 무시**. 아래 표는 이 규칙으로 걸러낸 실제 처리 대상입니다.

---

## 0. 처리 대상 한눈에 보기

| # | 구분 | 제보자 | 내용 | 원인 | 난이도 |
|---|---|---|---|---|---|
| B3 | 버그 | 나나 | Ctrl+V 모드가 클립스튜디오에서 반반 확률로 씹힘 | 클립보드 경쟁 상태 | 중 |
| B4 | 버그 | ㅇㅇ | Ctrl+V 모드 건너뛰기 / 중복 붙여넣기 | B3과 동일 | 중 |
| B5 | 버그 | ㅇㅋ | 포토샵 CC2024 지정 시 멈춤·강제종료 (구버전 삭제하면 정상) | COM 블로킹 + 구버전 잔존 | 상 |
| F2 | 개선 | 전가의보도 | 포토샵 '자리 표시자 텍스트' 옵션 없이도 포토샵 모드 동작 | 레이어 감지 방식 | 상 |
| F3 | 개선 | 나나, ㅇㅇ | Ctrl+V 말고 다른 키로 단축키 변경 | 구조 변경 필요 | 중 |
| F4 | 개선 | 나나 | 다음/현재/이전 대사 각각 단축키 배정 | F3과 함께 처리 | 중 |
| F5 | 개선 | ㅇㅇ | 이전 스크립트로 돌아가기 / 건너뛰기 이동 | F3·F4에 포함 | 중 |
| F6 | 개선 | 라임 | 포토샵 지정 시 30초 멈춤, 포토샵 연동 끄기 옵션 | B5와 동일 원인 | 중 |

실제 작업은 **3개 덩어리**로 수렴합니다: Ctrl+V 모드 개편(B3·B4·F3·F4·F5) / 포토샵 연동(B5·F2·F6) / 배포 준비.

### 제외된 항목

| 항목 | 사유 |
|---|---|
| 매크로 이름 100자 크래시 (고리성운) | 작성 예시. 실제로도 `macro_add.py:27 setMaxLength(30)`으로 2020년에 이미 차단됨 |
| 드래그앤드롭 파일 열기 (고리성운) | 작성 예시. Beta3.3에 구현 완료 |
| 설치 시 `Tcl data directory not found` (라임) | 회색 처리 = 해결됨. 단 아래 3-(a) 빌드 주의사항 참고 |

---

## 1. Ctrl+V 모드 개편 (B3, B4, F3, F4, F5)

### 원인 분석

`SB2T/thread/detect_ctrl_v.py` + `main.py:1083 copyNextLineAtCtrlVMode()`

```python
keyboard.hook_key('v', lambda e: self.checkVDown(str(e)))   # ← key DOWN 시점에 발사
...
if currentCopiedText == paste():
    self.btn[...].setTraceTextLine()
    time.sleep(0.1)          # ← 고정 100ms
    self.nextLineCopy()      # ← 클립보드를 다음 대사로 덮어씀
```

1. **경쟁 상태 (B3·B4의 직접 원인)** — V 키가 *눌린 순간* 신호가 발사되고, 100ms 뒤 클립보드를 다음 대사로 덮어씁니다. 대상 프로그램이 클립보드를 읽는 시점은 비동기라서:
   - 우리가 덮어쓰기 **전**에 읽으면 → 정상
   - 덮어쓴 **후**에 읽으면 → 다음 대사가 붙고 현재 대사는 건너뜀 (**건너뛰기**)
   - 대상 앱이 붙여넣기를 못 받았는데 우리는 이미 넘어간 경우 → 같은 자리에 다시 Ctrl+V (**중복**)

   클립스튜디오는 말풍선 처리 때문에 클립보드 읽기가 느려서 확률이 특히 높습니다. 나나 님이 "오토핫키로 F1 키를 쓰면 정상"이라고 하신 것도 이 타이밍이 바뀌기 때문이지 Ctrl 키 자체 문제는 아닙니다.

2. **키 반복(auto-repeat)** — `hook_key`는 V를 누르고 있으면 down 이벤트를 계속 쏩니다. 디바운스가 없어 한 번의 붙여넣기에 여러 줄이 넘어갈 수 있습니다.

3. **오른쪽 Ctrl** — `hook_key('ctrl')`는 왼쪽 Ctrl 스캔코드만 잡습니다. 오른쪽 Ctrl로 붙여넣으면 인식 자체가 안 됩니다.

4. **`disconnect()`가 `keyboard.unhook_all()` 호출** — 전역 훅을 전부 날려서, 매크로 모드 등과 같이 쓰면 서로 간섭할 여지가 있습니다.

### 수정 방안

- **발사 시점을 key up으로 이동** + 반복 이벤트 디바운스. `keyboard.on_release_key('v', ...)` 사용, 수식 키는 `keyboard.is_pressed('ctrl')`로 실시간 확인 (좌/우 Ctrl 모두 해결).
- **대기 시간을 고급 설정으로 노출** — 기본 100ms, 50~500ms 조절. 클립스튜디오처럼 느린 앱은 사용자가 올려서 대응.
- **`unhook_all()` → 개별 핸들 unhook**으로 교체.
- **전역 단축키 3종 신설** (F3·F4·F5 일괄 해결):

  | 동작 | 기본값 | 설명 |
  |---|---|---|
  | 다음 대사 | 미지정 | 클립보드 비교 없이 다음 줄 복사 |
  | 이전 대사 | 미지정 | 실수했을 때 되돌아가기 |
  | 현재 대사 다시 복사 | 미지정 | 씹혔을 때 재시도 |

  `keyboard.add_hotkey()` 기반, 매크로 설정 창처럼 키 입력받는 UI 재사용 (`dialog/macro_key_read.py` 활용). Ctrl+V 자동 감지는 그대로 두고 이 단축키를 **병행** 가능하게 하면, "Ctrl+V를 다른 용도로 써야 한다"는 ㅇㅇ 님 요구까지 커버됩니다.
- 이전 줄 이동을 위해 `nextLineCopy()`의 짝인 `prevLineCopy()` + `prevNumOfBtnMode()` 추가 필요. 현재 `lineCnt` / `lineCntBack` 구조라 되돌리기 시 흔적(색상) 처리도 같이 손봐야 합니다.

### 건드릴 파일

`thread/detect_ctrl_v.py`(재작성), `main.py`(1046~1195 구간), `dialog/adv_settings.py`, 신규 단축키 설정 UI

---

## 2. 포토샵 연동 (B5, F2, F6)

### 원인 분석

**(a) 30초 멈춤 (F6) / CC2024 강제종료 (B5)** — `main.py:925 checkPhotoshop()`

```python
if check:
    try:
        self.ps_app = ps.Application()   # ← COM Dispatch, UI 스레드에서 동기 호출
```

`ps.Application()`은 포토샵 COM 서버에 붙는 호출인데, 포토샵이 바쁘거나 모달 상태면 COM이 RPC 타임아웃까지 블로킹합니다. 이게 라임 님이 겪은 "30초 먹통 → 오류 알람 → 그제서야 인식"의 정체입니다. UI 스레드에서 부르기 때문에 창 전체가 멈춥니다.

게다가 이 함수가 **프로그램 지정할 때마다**, 그리고 c3a46a6 커밋 이후로는 **Ctrl+V 모드를 끌 때도**(`main.py:1067`) 호출됩니다. 포토샵 모드를 안 쓰는 사람도 매번 이 비용을 냅니다.

CC2024(v25) 문제는 여기에 `photoshop_python_api`의 버전 매핑이 겹친 것으로 보입니다. 이 라이브러리는 버전별 ProgID를 표로 들고 있어서, 표에 없는 버전이면 실패하거나 매달립니다.
→ **검증 필요**: 현재 설치된 `photoshop_python_api` 버전과 25.x 지원 여부 확인. `requirements.txt`가 없어 버전이 고정돼 있지 않은 것도 문제.

"구버전을 삭제하면 정상 작동"은 별개 원인으로, 3번 인스톨러 항목입니다.

**(b) 자리 표시자 텍스트 의존 (F2)** — `thread/start_ps.py`

```python
while True:
    try:
        layername = app.ActiveDocument.ActiveLayer.name
        if ("Lorem Ipsum" in layername or ... match("^레이어 [0-9]+$", layername) ...):
```

새 텍스트 레이어를 **이름 문자열로** 판별합니다. 포토샵 `환경설정→문자→자리 표시자 텍스트로 새로운 유형 레이어 채우기`를 끄면 빈 텍스트 레이어가 생기고, 포토샵은 내용 없는 텍스트 레이어를 포커스 해제 시 삭제해버립니다 → 이름 매칭이 영영 안 됨. 전가의보도 님이 찾아낸 그대로입니다.

추가로 이 루프는 `try/except pass`로 쉬지 않고 도는 **busy-wait**이라 포토샵 모드 켜는 동안 CPU 코어 하나를 계속 먹습니다.

### 수정 방안

- **`checkPhotoshop()`을 UI 스레드에서 분리** — 워커 스레드 + 타임아웃(3~5초). 타임아웃 시 "포토샵 연동 실패, 자동 모드는 사용 가능" 안내 후 즉시 반환. 30초 멈춤이 사라집니다.
- **COM 프로브를 지연 실행** — 프로그램 지정 시엔 프로세스 이름만 확인해서 버튼을 활성화하고, 실제 `ps.Application()` 연결은 **포토샵 모드를 켜는 순간**에만. Ctrl+V 모드 끌 때 호출하는 것도 제거.
- **고급 설정에 '포토샵 연동 사용 안 함' 토글 추가** (라임 님 요청 직접 반영). 켜면 COM 관련 코드를 전부 우회.
- **CC2024 대응** — `ps.Application()` 실패 시 버전 독립 ProgID인 `win32com.client.Dispatch("Photoshop.Application")`로 폴백. `photoshop_python_api`를 최신으로 올리고 `requirements.txt`로 버전 고정.
- **레이어 감지 방식 교체 (F2)** — 이름 매칭 대신:
  1. 포토샵 모드 시작 시점의 레이어 상태를 스냅샷
  2. 폴링 루프에 `time.sleep(0.05)` 추가 (busy-wait 제거)
  3. `ActiveLayer.Kind == 2`(텍스트 레이어) 또는 레이어 ID 변화로 판별

  ⚠️ `Kind` 체크는 예전에 시도했다가 "포토샵에서 마우스 커서가 오락가락"하는 문제로 주석 처리된 이력이 있습니다(`start_ps.py:21`). 레이어 ID 스냅샷 비교가 더 안전한 대안이며, 실기 테스트가 반드시 필요합니다.
  ⚠️ 시트 답변에서 언급하신 "Ctrl+Enter로 닫기" 방향은 빈 레이어 삭제를 막아주긴 하지만 사용자가 직접 닫는 동작을 바꾸는 거라, 감지 방식 교체와 병행 검토가 낫습니다.

### 건드릴 파일

`thread/start_ps.py`(재작성), `main.py`(`checkPhotoshop`, `setToolMenuAfterSetPrgm`, `psAutoStart`), `dialog/adv_settings.py`

---

## 3. 인스톨러 (B5 후속)

### (a) 빌드 시 주의 — Tcl 땜빵 (버그 자체는 해결됨)

라임 님의 `Tcl data directory not found`는 해결 처리됐지만, 해결 방식이 "tcl/tk 폴더에 dummy.txt를 넣는" 수동 땜빵입니다(README에 기재). **5.0 빌드 때도 이 과정을 빼먹으면 같은 오류가 재발합니다.**

원인은 `SB2Tool.spec`:

```python
excludes=['PIL', 'pandas', 'numpy', 'tcl', 'scipy', 'opencv-python', 'cv2'],
```

`tcl`만 제외했는데 `tkinter` 자체는 여전히 번들에 포함됩니다(pyautogui → pymsgbox/pyscreeze 경유). PyInstaller의 `pyi_rth__tkinter` 런타임 훅이 살아남아 실행 시 tcl 디렉터리를 찾다 실패합니다.

→ **선택 사항**: `excludes`에 `'tkinter', '_tkinter'`를 추가하면 dummy.txt 수동 작업 자체가 없어집니다. 식붕이툴은 pyautogui의 메시지박스 기능을 안 쓰므로(`getAllTitles`, `getWindowsWithTitle`, `hotkey`, `press`만 사용) 안전할 것으로 보이나, 이미 동작하는 부분이라 5.0에서 건드릴지는 판단 필요.

### (b) 구버전 잔존 충돌 (B5 후속) — `SB2ToolBeta4.0.nsi`

HM NIS Edit이 생성한 스크립트라 파일이 전부 개별 나열돼 있고, 언인스톨도 `Delete` 나열 방식입니다. 그래서:
- 이전 버전을 지우지 않고 같은 `$PROGRAMFILES\SB2Tool`에 덮어쓰면 구버전 잔여 DLL/pyd가 남아 신버전 런타임과 섞임 → ㅇㅋ 님의 "구버전 삭제하면 정상" 증상과 정확히 일치
- 기존 설치 감지 로직이 아예 없음

→ 수정:
- `.onInit`에 기존 설치 감지 추가 (`PRODUCT_UNINST_KEY` 조회 → 발견 시 구버전 언인스톨러 실행 후 진행)
- `Section Uninstall`에 `RMDir /r "$INSTDIR"` 추가로 잔여 파일 일괄 제거
- 파일 나열을 `File /r "dist\SB2Tool\*.*"`로 단순화 (5.0에서 파일 목록이 바뀌므로 어차피 갱신 필요)
- 파일명을 `SB2Tool5.0.nsi`로, `PRODUCT_VERSION`을 `5.0`로

⚠️ 현재 `.nsi`는 `Unicode True`인데 파일 인코딩이 CP949로 보입니다. 실제 빌드에 문제가 없었다면 그대로 두되, 편집 시 인코딩이 깨지지 않게 주의해야 합니다.

---

## 4. 마무리 작업

- `SB2T/__init__.py`의 `__version__`이 `Beta3.2`로 방치돼 있음 → `5.0`. `main.py`의 `self.version`도 여기서 읽어오도록 통합
- **`advSettingsList` 하위 호환 처리 (중요)** — 고급 설정이 길이 9짜리 위치 기반 리스트라 새 옵션을 추가하면 4.0 사용자의 저장값(9개)을 읽을 때 `IndexError` → `except` 절에서 **전체 설정이 기본값으로 리셋**됩니다. 새 옵션은 반드시 뒤에 append 하고, 로더를 "없으면 기본값으로 채우기" 방식으로 바꿔야 합니다
- `requirements.txt` 신설 (특히 `photoshop_python_api` 버전 고정)
- `.gitattributes` 추가 — 지금 작업 트리는 CRLF/LF 차이만으로 전 파일이 modified 상태(4818 추가 / 4808 삭제, 실질 변경 없음). 5.0 커밋 전에 정리하지 않으면 리뷰가 불가능합니다
- README 5.0 변경사항 정리
- 시트 '진척 현황' 칸 회신 작성

---

## 5. 제안 작업 순서

1. **정지 작업** — `.gitattributes`로 CRLF 정리, `requirements.txt`, 버전 문자열 통일, `advSettingsList` 로더 하위 호환화
2. **Ctrl+V 모드 개편** — 요청이 가장 많이 몰린 영역, 단독 테스트 가능
3. **포토샵 연동** — 비동기화 + 연동 끄기 옵션(F6) 먼저, 레이어 감지 교체(F2)는 실기 테스트 병행
4. **인스톨러 + 빌드** — PyInstaller 빌드(tcl/tk dummy.txt 잊지 말 것) → nsi 갱신(구버전 감지 + `RMDir /r`) → 클린 환경/구버전 위 덮어쓰기 양쪽 설치 테스트
5. **배포** — README, 시트 회신, 블로그 공지

---

## 6. 테스트가 필요한 항목 (윈도우 실기 필수)

| 항목 | 확인 방법 |
|---|---|
| Ctrl+V 모드 씹힘 | 클립스튜디오 + 포토샵에서 50줄 연속 붙여넣기, 누락/중복 카운트 |
| 새 전역 단축키 | 다른 앱 단축키와 충돌 여부 |
| 포토샵 지정 속도 | 포토샵 켠 상태에서 프로그램 지정 → 3초 내 반응하는지 |
| 포토샵 CC2024 | 지정 시 멈춤 없는지 (제보자 ㅇㅋ 님께 검증 요청 고려) |
| 자리 표시자 옵션 OFF | 포토샵 모드 정상 동작 여부 (전가의보도 님 검증 요청 고려) |
| 빌드 후 실행 | tcl/tk dummy.txt 처리 여부 확인 (누락 시 Tcl 오류 재발) |
| 구버전 위 설치 | 3.3 / 4.0 설치된 상태에서 5.0 설치 |
