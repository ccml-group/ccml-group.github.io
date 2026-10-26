# Google Scholar 자동 갱신 설정

## 구현 상태

수집 코드, 실패 시 기존 값 보존, 홈페이지의 지표·연도별 인용 그래프, 매주 실행 및 GitHub Pages 배포 설정을 포함했습니다. **최신 저장값과 수집 시점은 `data/scholar.js`와 홈페이지의 갱신일을 확인하세요.** 2026-10-26 문서 점검 당시 스냅샷은 인용 1,140, h-index 15, i10-index 17이었습니다. 이 문서 수정 과정에서는 저장소 Secret 등록 여부와 실제 예약 실행 상태를 확인하지 않았습니다. 예약·수동 갱신에는 아래 설정이 필요합니다.

## 필요한 것

1. **GitHub 계정과 홈페이지 전용 저장소**: 아래 구성은 기본 브랜치 이름이 `main`인 저장소를 기준으로 합니다.
2. **SerpApi 계정과 API 키**: Google Scholar의 공식 서비스가 아닌 외부 수집 서비스입니다. 요금·무료 제공량은 가입 시 https://serpapi.com/pricing 에서 확인하세요. 기본 예약은 주 1회, 월 약 4–5회 요청하며 수동 실행 시 요청이 추가됩니다. Google 로그인 비밀번호는 필요하지 않습니다.
3. **공개 Google Scholar 프로필**: `iqaMS78AAAAJ`로 지정되어 있습니다. 출처는 기존 CCML 사이트의 Scholar 링크입니다.
4. **GitHub Actions와 Pages 사용 설정**: 컴퓨터가 꺼져 있어도 GitHub에서 실행됩니다. GitHub/SerpApi의 서비스 사용 한도는 각 계정 정책에 따릅니다.

## 한 번만 설정하기

1. ZIP을 풀고 `ccml-website` 폴더 **안의 내용**을 저장소 루트에 올립니다. `index.html`, `scripts/`, `data/`, **숨김 폴더 `.github/`**가 같은 레벨이어야 합니다. macOS Finder에서는 Command+Shift+. 로 숨김 폴더를 표시합니다.
2. GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에서 이름을 `SERPAPI_API_KEY`, 값을 본인의 SerpApi API 키로 저장합니다. 채팅·HTML·공개 저장소에는 키를 넣지 마세요.
3. **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 선택합니다.
4. Actions가 비활성화돼 있다면 활성화합니다. 조직 정책이 있는 경우 워크플로의 저장소 쓰기 권한과 Pages 배포가 허용돼야 합니다. 코드의 권한 범위는 마지막 정상 지표를 저장하는 데 필요한 `contents: write`, 배포 작업의 `pages: write`, `id-token: write`입니다. 보호 브랜치에서 자동 커밋이 금지돼 있다면 현재 구성은 실패합니다. 보호 규칙을 무작정 끄지 말고 관리자에게 전용 배포 브랜치 또는 PR 방식 구성을 요청하세요.
5. **Actions → Update Scholar and deploy CCML → Run workflow**를 한 번 실행합니다. 기본 브랜치 `main`에서 실행해야 합니다.
6. 실행 성공 후 Pages 주소에서 인용 수·h-index·i10-index, 갱신일과 Publications의 연도별 인용 그래프를 확인합니다.

이후 **매주 월요일 오전 9:17 한국시간**에 갱신됩니다. GitHub의 예약 실행은 지연될 수 있습니다. 콘텐츠를 `main`에 올리면 API 호출 없이 저장된 지표로 다시 배포됩니다. 기본 브랜치 이름을 바꾸면 `.github/workflows/site.yml`의 `push.branches`도 맞춰 변경하세요.

## 갱신 방식과 실패 처리

SerpApi 조회 → 프로필 ID·숫자·연도 검증 → `data/scholar.js` 원자적 교체 → 정상 스냅샷 커밋 → 공개 파일만 Pages 배포 순서입니다. 브라우저가 SerpApi를 호출하지 않으므로 키가 방문자에게 노출되지 않습니다. 원본 API 응답이나 API 키가 포함된 요청 URL은 저장·출력하지 않습니다.

`main` 푸시에서는 키 유무와 관계없이 API 수집을 건너뛰고 저장된 지표로 검증·배포합니다. 주간 예약 또는 수동 실행에서는 키가 없으면 구성 검사 단계에서 실패하며 배포하지 않습니다. 키 등록 후 네트워크 오류, 요청 한도 초과, 응답 형식 변경, 프로필 불일치가 발생해도 작업을 실패로 종료하고 기존 데이터와 이미 배포된 사이트를 유지합니다. 마지막 갱신 후 21일이 지나면 화면에 `Update delayed` 또는 `갱신 지연`이 표시됩니다. API 대시보드와 Actions 실행 기록을 확인하고 문제 해결 후 수동 실행하세요. GitHub Actions 실패 알림은 본인 GitHub 알림 설정에 따릅니다.

공개 저장소의 예약 작업은 저장소 활동이 60일 없으면 비활성화될 수 있습니다. 정상 갱신은 날짜가 포함된 스냅샷을 커밋하지만, 실패가 오래 지속되면 Actions에서 재활성화가 필요할 수 있습니다.

## 수집 범위

인용 수·h-index·i10-index의 **전체 기간(All-time)** 수치와 연도별 인용 수입니다. 교수 개인 프로필의 전체 경력 지표이며 CCML 설립 이후의 실적만을 뜻하지 않습니다. 해당 연도 인용 수는 연초부터 수집 시점까지의 값입니다. 논문 수와 논문 본문 목록은 자동 수정하지 않습니다.

## 학교 서버를 사용하는 경우

같은 수집 프로그램을 학교 서버의 예약 실행 기능으로 주 1회 실행할 수 있습니다. 필요한 추가 정보는 서버의 Python 3 지원 여부, 예약 실행 가능 여부, 웹 폴더 경로와 파일 쓰기 권한입니다. 이 경우 SerpApi 키는 웹 공개 폴더 밖의 서버 환경변수에 보관하고 `python3 scripts/update_scholar.py`를 실행합니다. GitHub에서 수집한 뒤 학교 서버로 보내려면 별도의 SFTP/SSH 배포 연결이 필요합니다. 현재 ZIP의 자동 배포 대상은 GitHub Pages이며 학교 서버 접속 설정은 포함하지 않았습니다.

## 검증과 한계

2026-10-26 로컬 검사에서 `python3 check.py`, `python3 scripts/test_scholar.py`, `node scripts/test_scholar_ui.js`가 통과했습니다. 수집 프로그램 검사는 실제 요청을 보내지 않는 모의 응답으로 정상 처리, 잘못된 프로필, 빈 데이터, 음수·중복 연도, 키 누락 및 네트워크 오류 시 기존 값 보존을 확인합니다. UI 검사는 한영 지표와 인용 그래프, 21일 초과 갱신 지연 표시를 확인합니다. 이번 문서 수정에서는 실제 API 수집, 저장소 Secret 등록 여부, GitHub 예약 실행 및 배포 성공 여부를 검증하지 않았습니다.

공식 참고 자료:
- https://serpapi.com/google-scholar-author-cited-by
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
