# 개발 환경 설정 (새 PC 기준)

Beta4.0 배포 빌드가 Python 3.8로 만들어졌고, 5.0도 동일하게 간다.
(설치 폴더의 `python38.dll`, `*.cp38-win_amd64.pyd`가 근거)

---

## 1. Python 3.8.10 설치

3.8은 2024년 10월에 EOL이라 python.org에서 **설치 파일이 제공되는 마지막 버전이 3.8.10(2021-05)** 이다.

- 받는 곳: <https://www.python.org/downloads/release/python-3810/>
- 파일: **Windows installer (64-bit)** — `python-3.8.10-amd64.exe`

설치 시 체크할 것:

- [x] **Install launcher for all users** (`py` 런처. 여러 버전 섞어 쓸 때 필수)
- [ ] Add Python 3.8 to PATH — **체크하지 말 것**. 이 PC에 다른 파이썬이 있으면 꼬인다. 대신 `py -3.8`로 호출한다.

설치 확인:

```cmd
py -0
py -3.8 --version
```

`py -0`에 `-3.8-64`가 보이면 성공.

---

## 2. 가상환경 + 의존성

저장소 루트에서:

```cmd
cd C:\Users\M57JNEE\Documents\dev\SB2Tool

py -3.8 -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-build.txt
```

메모:

- 3.8.10 기본 pip는 21.1.1로 낡아서 휠 해석이 어긋날 수 있다. 위처럼 먼저 올릴 것.
  pip 25부터는 3.9 이상만 지원하므로 `--upgrade`를 해도 3.8용 마지막 버전에서 멈춘다. 정상이다.
- `pyautogui`가 `pyscreeze` → `Pillow`를 딸려 온다. 실행에는 안 쓰이고
  `SB2Tool.spec`의 `excludes`에 `PIL`이 있어 배포본에는 안 들어가니 그냥 두면 된다.
- `photoshop_python_api` 0.22.x부터 `comtypes`가 같이 설치된다. 정상이다.

`.venv`는 `.gitignore`에 없으므로 추가하거나, 저장소 밖에 만들어도 된다.

---

## 3. 소스로 실행

```cmd
.venv\Scripts\activate
python SB2Tool.py
```

주의:

- **관리자 권한으로 실행하지 말 것.** 포토샵과 권한(무결성 수준)이 다르면
  COM으로 서로를 찾지 못한다. 실측 결과:

  | 파이썬 권한 | 포토샵 권한 | `GetActiveObject` | `Dispatch` |
  |---|---|---|---|
  | 관리자 | 일반 | 실패 `0x800401E3` (즉시) | 실패 `0x80080005` (30초) |
  | 일반 | 일반 | **성공 (0.0초)** | **성공 (0.0초)** |

  포토샵을 관리자로 띄워야 하는 사정이 있다면 식붕이툴도 관리자로 맞춰야 한다.
  중요한 건 '관리자냐'가 아니라 '양쪽이 같으냐'다.
- 원인을 알 수 없는 연결 실패는 `python tools\ps_diag.py`로 진단할 수 있다.

### 설정 백업 (중요)

소스 실행본과 설치된 4.0이 **같은 레지스트리 키를 공유**한다
(`QSettings("RingNebula", "SB2Tool")` → `HKCU\Software\RingNebula\SB2Tool`).
소스로 띄우면 기존 설정을 읽고 종료 시 덮어쓴다. 먼저 백업할 것:

```cmd
reg export "HKCU\Software\RingNebula\SB2Tool" %USERPROFILE%\sb2tool-settings-backup.reg
```

되돌릴 때는 `.reg` 파일을 더블클릭해서 병합.

---

## 4. 잔재 정리 (선택)

이전 PC에서 넘어온 `__pycache__`에 cpython-310, cpython-313 `.pyc`가 섞여 있다.
파일명에 버전이 박혀 있어 3.8이 무시하므로 해는 없지만, 지우고 시작하면 깔끔하다.

```cmd
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

---

## 5. 빌드 (배포 직전에만)

```cmd
.venv\Scripts\activate
pyinstaller SB2Tool.spec
```

빌드하면 `dist\SB2Tool\` 에 실행 파일과 `_internal\` 폴더가 생긴다.
아이콘과 글꼴은 `.spec`의 `datas`로 자동 포함되므로 손댈 것이 없다.
(4.0 때는 아이콘을 손으로 복사해야 했다)

**PyInstaller 6 기준이다.** 5.x와 출력 구조가 다르다.
- 5.x: 모든 파일이 `dist\SB2Tool\` 최상위
- 6.x: 실행 파일만 최상위, 나머지는 `dist\SB2Tool\_internal\`

이 차이 때문에 **4.0이 설치된 폴더에 그대로 덮어쓰면 실행이 안 된다.**
4.0의 Qt DLL이 최상위에 남아 있으면 윈도우가 그걸 먼저 물어서
`DLL load failed while importing QtCore` 로 죽는다.
그래서 `SB2Tool5.0.nsi`는 설치 전에 폴더를 통째로 비운다.

그다음 NSIS로 `SB2Tool5.0.nsi` 컴파일.

```cmd
"C:\Program Files (x86)\NSIS\makensis.exe" SB2Tool5.0.nsi
```


---

## 6. 빠른 점검

| 확인 | 기대 결과 |
|---|---|
| `py -3.8 --version` | `Python 3.8.10` |
| `pip list` | PyQt5, pywin32, keyboard, pyautogui, photoshop-python-api, comtypes |
| `python SB2Tool.py` | 창 제목이 `식붕이툴 5.0` |
| F2 (고급 설정) | '붙여넣기 기능'에 `Ctrl+V 모드 대기시간` 스핀박스 |
| Ctrl+K | '대사 이동 단축키 설정' 창 |
