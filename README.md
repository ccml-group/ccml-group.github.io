# CCML 정적 홈페이지

공식 사이트: https://ccml-group.github.io/

영어 페이지는 루트에, 한국어 페이지는 `ko/`에 있습니다. 각 언어에는 소개, 구성원, 교수 소개, 연구 분야, 논문, 소식, 연구 참여, 연락처의 8개 페이지가 있습니다. 상단 한국어 / English 링크는 같은 페이지와 연구 항목으로 연결됩니다.

## 콘텐츠 수정

- 문구와 메뉴·푸터는 각 HTML에서 변경합니다. 공통 내용은 한국어·영어 페이지에 함께 반영합니다.
- 공통 디자인은 `css/style.css`, 메뉴·언어 전환·논문 검색은 `js/main.js`에 있습니다.
- 논문 정보는 `data/publications.json`에서 수정한 뒤 `python3 scripts/render_publications.py`를 실행합니다. 한영 목록·연도별 편수·필터 연도·홈 대표논문에 함께 반영됩니다. 주저자로 표시할 PI는 `pi_lead_author: true`로 지정합니다. 메인 대표논문의 기여 요약은 해당 논문의 `summary_en`, `summary_ko`에 한 문장씩 작성합니다.
- 대표논문 4편은 `data/selected-publications.json`의 번호로 선택합니다. IF는 검증한 기준연도·원래 수치·출처를 기록하며 자동 조회하지 않습니다. 화면에만 소수점 첫째 자리로 반올림하고, 대표연구의 IF ≥ 9 기준은 반올림 전 수치를 사용합니다. 검증 근거는 [IMPACT-FACTORS.md](IMPACT-FACTORS.md)에 있습니다.
- 인용 통계는 `data/scholar.js`에서 읽고, `js/scholar.js`가 언어별로 표시합니다. 주간 자동 갱신 설정은 [AUTO-UPDATE.md](AUTO-UPDATE.md)에 있습니다.
- 논문 목록에는 graphical abstract만 표시합니다. 없는 항목은 텍스트만 표시하며 Figure 1이나 다른 그림으로 대체하지 않습니다.
- 연구 그림과 편집 내역은 [RESEARCH-FIGURES.md](RESEARCH-FIGURES.md), 논문 대표 그림은 [TOC-SOURCES.md](TOC-SOURCES.md)에 기록했습니다.
- 원본 연구 그림과 TOC는 유지하고, 표시용 파생본은 `assets/derived/`에 저장합니다. 원본 그림 변경 후에는 기존 Pillow 환경에서 `python3 scripts/prepare_images.py`를 실행하고 연구 그림의 srcset도 갱신합니다. 공유 미리보기는 `assets/share-card.png`를 사용합니다.

## 연구 참여 및 위치

- 코딩·계산화학 경험은 필수가 아니며 대학원 진학에 관심 있는 학생을 환영합니다.
- 학부연구생은 약 6개월 참여를 권장하고, 구체적인 일정은 개별 상담으로 정합니다.
- 연구실: 원흥관 E243·E244호 / Wonheung Hall E243, E244
- 교수 사무실: 만해관 B211호 / Manhae Hall B211
- 대표 이메일: yhyuk@dgu.ac.kr

## 검증과 배포

```sh
python3 scripts/render_publications.py --check
python3 scripts/test_publications.py
python3 check.py
python3 scripts/test_scholar.py
node scripts/test_scholar_ui.js
node scripts/test_main_ui.js
```

내부 링크·앵커·이미지, 한영 연결, 논문 정보·상태·주저자 표시, 검색·필터·메뉴, 인용 통계 표시와 JSON/HTML 일치를 검증합니다. 새 논문의 저자·상태·IF는 확인된 자료로 입력해야 합니다.

`main`에 푸시하면 GitHub Actions가 검증 후 HTML과 `css/js/assets/data/ko`를 GitHub Pages에 배포합니다. 매주 자동 인용 통계 갱신도 같은 배포 과정을 사용합니다.

로컬 미리보기는 이 폴더에서 다음 명령을 실행한 후 http://127.0.0.1:8767/ko/index.html 을 엽니다. 다른 프로그램이 사용 중이면 빈 포트를 선택합니다.

```sh
python3 -m http.server 8767 --bind 127.0.0.1
```

## 연구·구성원 안내

연구 페이지의 네 주제 바로가기와 관련 대표논문, 공동연구 연락처를 연결했습니다. 메인 대표논문 네 편에는 한영 연구 기여 요약을 표시합니다. 논문 검색은 일반 숫자와 유니코드 아래첨자를 동일하게 처리합니다.

구성원 페이지에는 사용자 확인 내용을 바탕으로 각 학생의 여러 참여 연구를 한영으로 정리했습니다. 연구 주제는 특정 전공 하나로 고정하거나 완료된 성과로 표현하지 않습니다. 참여 안내의 대학원 모집요강과 방문 안내의 캠퍼스맵은 학교 공식 페이지로 연결됩니다.
