; 식붕이툴 5.0 인스톨러
;
; 4.0까지는 HM NIS Edit이 생성한 스크립트를 썼다. 파일이 전부 개별 나열돼
; 있어서(File 123줄, Delete 129줄) 파일 구성이 바뀔 때마다 목록을 손봐야 했고,
; 언인스톨도 나열된 것만 지우다 보니 목록에 없는 파일이 남았다.
; "구버전이 깔려 있으면 최신 버전이 먹통"이라는 제보(ㅇㅋ 님)의 원인으로 보인다.
;
; 5.0부터는
;   - 설치:   File /r 로 dist 폴더를 통째로 넣는다
;   - 제거:   RMDir /r 로 설치 폴더를 통째로 지운다
;   - 덮어쓰기: 기존 설치를 감지해 먼저 제거하도록 안내한다
;
; 이 파일은 UTF-8(BOM 포함)로 저장해야 한다. NSIS는 BOM이 없으면 시스템
; 코드페이지로 읽기 때문에, 다른 환경에서 컴파일하면 한글이 깨진다.

Unicode True

!define PRODUCT_NAME "식붕이툴"
!define PRODUCT_VERSION "5.0"
!define PRODUCT_PUBLISHER "고리성운"
!define PRODUCT_WEB_SITE "https://blog.naver.com/dnjsfh611/"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\SB2Tool.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!include "MUI.nsh"
!include "LogicLib.nsh"

; ---------------------------------------------------------------- 모양새
!define MUI_ABORTWARNING
!define MUI_ICON "icons\new_logo.ico"
!define MUI_UNICON "icons\new_logo.ico"

; 마법사 배경 이미지 (164x314 BMP).
; 4.0까지는 NSIS 설치 폴더에 넣어둔 sb2tl_welcome.bmp를 참조했다. 그 파일은
; 저장소에 없어서 다른 PC에서는 컴파일이 실패한다. 그래서 저장소 안으로 옮겼다.
; 혹시 없더라도 컴파일은 되도록 기본 이미지로 넘어간다.
!if /FileExists "installer\welcome.bmp"
  !define MUI_WELCOMEFINISHPAGE_BITMAP "installer\welcome.bmp"
  !define MUI_WELCOMEFINISHPAGE_UNBITMAP "installer\welcome.bmp"
!endif

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\SB2Tool.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Korean"

; ---------------------------------------------------------------- 기본 정보
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "식붕이툴-5.0_Setup.exe"
InstallDir "$PROGRAMFILES\SB2Tool"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; ---------------------------------------------------------------- 설치 전 검사
Function .onInit
  ; 이전 버전이 남아 있으면 먼저 제거한다.
  ; 덮어쓰기로 설치하면 구버전 DLL/pyd가 남아 새 버전과 섞인다.
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  ${If} $R0 != ""
    MessageBox MB_ICONEXCLAMATION|MB_YESNOCANCEL|MB_DEFBUTTON1 \
      "이전 버전의 식붕이툴이 설치되어 있습니다.$\n$\n\
      먼저 제거해야 합니다. 지금 제거하시겠습니까?$\n\
      (설정과 매크로는 그대로 유지됩니다)" \
      /SD IDYES IDYES uninst_old IDNO keep_going
      Abort

    uninst_old:
      ClearErrors
      ExecWait '$R0 _?=$INSTDIR' $R1
      ${If} $R1 != 0
        MessageBox MB_ICONSTOP|MB_OK \
          "제거가 완료되지 않았습니다.$\n제어판에서 직접 제거한 뒤 다시 실행해 주세요."
        Abort
      ${EndIf}
    keep_going:
  ${EndIf}
FunctionEnd

; ---------------------------------------------------------------- 설치
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  ; PyInstaller 산출물을 통째로 넣는다.
  ; icons, fonts 도 여기에 포함되어 있다 (SB2Tool.spec의 datas 참고)
  File /r "dist\SB2Tool\*.*"
SectionEnd

Section -AdditionalIcons
  SetOutPath "$INSTDIR"
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateDirectory "$SMPROGRAMS\식붕이툴"
  ; 시작 위치를 설치 폴더로 고정한다. 코드가 리소스를 실행 파일 기준으로
  ; 찾긴 하지만, 바로가기의 시작 위치를 비워두면 다른 문제가 생길 수 있다.
  CreateShortCut "$SMPROGRAMS\식붕이툴\식붕이툴.lnk" "$INSTDIR\SB2Tool.exe" "" "" 0 SW_SHOWNORMAL "" "" "$INSTDIR"
  CreateShortCut "$SMPROGRAMS\식붕이툴\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\식붕이툴\Uninstall.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$DESKTOP\식붕이툴.lnk" "$INSTDIR\SB2Tool.exe" "" "" 0 SW_SHOWNORMAL "" "" "$INSTDIR"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\SB2Tool.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\SB2Tool.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; ---------------------------------------------------------------- 제거
Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 \
    "식붕이툴을 제거하시겠습니까?" /SD IDYES IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "식붕이툴은 완전히 제거되었습니다." /SD IDOK
FunctionEnd

Section Uninstall
  ; 설치 폴더를 통째로 지운다.
  ; 4.0처럼 파일을 나열해서 지우면 목록에 없는 것이 남는다.
  Delete "$DESKTOP\식붕이툴.lnk"
  RMDir /r "$SMPROGRAMS\식붕이툴"
  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; 사용자 설정(HKCU\Software\RingNebula\SB2Tool)은 일부러 남긴다.
  ; 재설치할 때 매크로와 고급 설정이 그대로 유지된다.
  SetAutoClose true
SectionEnd
