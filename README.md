# SB2Tool
식붕이툴 전체 코드 및 파일
- backuptest 압축파일의 경우, pyinstaller로 식붕이툴을 실행파일로 만들었을 때 생기는 파일들 중, 프로그램 실행에 영향을 끼치지 않아 제외해도 되는 파일들을 모아놓음. tcl, tk는 안에 dummy.txt만 생성해 놓고 다 빼도 됨.

각종 링크들
- 설치파일 다운로드 : https://drive.google.com/file/d/1Eh_qFd1z4a-s9qlpdN-OK0l2TEcCocrB/view?usp=sharing
- 매뉴얼 : https://docs.google.com/document/d/1JzMC_iyi265wXQv3zo2yEuC0qF0_NcdVGzgWb15UWig/edit?usp=sharing
- 버그 제보 및 피드백 : https://docs.google.com/spreadsheets/d/1L4ai00inqZpMqeJuhz7bOCdrWgMTYHEZKl7EXY-nHqM/edit?usp=sharing

&nbsp;

# 최근 업데이트 내용 정리
## Beta3.2
- 대사 태그별 포토샵 문자 설정 가능 -> 태그: 대화, 생각, 강조, 독백, 배경, 효과
- 포토샵 모드 활성화 방식 변경(버그 수정) -> GetActiveObject("Photoshop.Application")를 사용하지 않고 프로세스를 직접 검색하여 확인하는 방식으로 변경
- 책갈피 표시 방식 변경
- 모든 텍스트 묶음 활성화 및 비활성화 기능 추가
- 초기 메인 윈도우 창 크기 변경
- 실행 취소, 되돌리기 시 해당 라인으로 이동하게끔 수정
---
## Beta3.1
- 항상 위에 고정 기능 추가
- 버그 수정 -> 포토샵 모드 동작 중 '연결된 텍스트 라인' 붙여넣기 진행 시, 개행이 제대로 이루어지지 않는 문제 해결
- 글꼴 변경 시 현재 사용 중인 글꼴을 default 값으로 지정
---
## Beta3.0
- 드래그 앤 드랍 보완 -> 모드 켰을 때 드랍 못하도록 막음
- 텍스트 라인 더블클릭 시 바로 텍스트 수정 가능하게 개선
- 오류 시스템 보완 -> 파일 불러오기, 프로그램 지정 시 강제 종료 방지
- 포토샵 지정 간편화 -> 원래는 불러온 파일 이름, 레이어 이름까지 동일해야 포토샵 모드 버튼이 활성화됐으나 이제는 포토샵이 켜져만 있으면 활성화 (텍스트 프로그램 지정했는데 포토샵이 켜져 있으면 활성화됨, 포토샵 모드도 정상적으로 작동, 자동 모드만 지정한 프로그램으로 적용)
- 메인 창과 텍스트 라인 창 사이 여백 삭제
- 묶음 복붙 기능 추가 -> 텍스트에서 줄 사이에 개행이 한 번만 들어갈 경우, 불러올 때 묶음 처리. 묶음 처리된 줄은 한번에 복붙이 가능하며 이 묶음을 해제해서 개별 복붙도 가능함.
- 중괄호, 대괄호 제외 복사 기능 추가
- 주석 폰트 -> 이탤릭체로 변경
- 책갈피 기능 추가 -> 한 개 책갈피만 가능, 책갈피가 있는 파일을 불러올 경우 자동으로 책갈피가 있는 라인으로 이동.
- 종료 확인창 삭제
---

