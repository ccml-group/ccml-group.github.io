# CCML 정적 홈페이지

공식 사이트: https://ccml-group.github.io/

영어 페이지는 루트에, 한국어 페이지는 `ko/`에 있습니다. 각 언어에는 소개, 구성원, 교수 소개, 연구 분야, 논문, 소식, 연구 참여, 연락처의 8개 페이지가 있습니다. 상단 한국어 / English 링크는 같은 페이지와 연구 항목으로 연결됩니다.

## 콘텐츠 수정

- 문구와 메뉴·푸터는 각 HTML에서 변경합니다. 공통 내용은 한국어·영어 페이지에 함께 반영합니다.
- 공통 디자인은 `css/style.css`, 메뉴·언어 전환·논문 검색은 `js/main.js`에 있습니다.
- 논문 메타데이터 사본은 `data/publications.json`입니다. 논문 수정 시 이 파일과 두 언어의 `publications.html`, 필요한 경우 두 홈의 대표 논문도 함께 수정합니다.
- 인용 통계는 `data/scholar.js`에서 읽고, `js/scholar.js`가 언어별로 표시합니다. 주간 자동 갱신 설정은 [AUTO-UPDATE.md](AUTO-UPDATE.md)에 있습니다.
- 논문 목록에는 graphical abstract만 표시합니다. 없는 항목은 텍스트만 표시하며 Figure 1이나 다른 그림으로 대체하지 않습니다.
- 연구 그림과 편집 내역은 [RESEARCH-FIGURES.md](RESEARCH-FIGURES.md), 논문 대표 그림은 [TOC-SOURCES.md](TOC-SOURCES.md)에 기록했습니다.

## 연구 참여 및 위치

- 코딩·계산화학 경험은 필수가 아니며 대학원 진학에 관심 있는 학생을 환영합니다.
- 학부연구생은 약 6개월 참여를 권장하고, 구체적인 일정은 개별 상담으로 정합니다.
- 연구실: 원흥관 E243·E244호 / Wonheung Hall E243, E244
- 교수 사무실: 만해관 B211호 / Manhae Hall B211
- 대표 이메일: yhyuk@dgu.ac.kr

## 검증과 배포

```sh
python3 check.py
python3 scripts/test_scholar.py
node scripts/test_scholar_ui.js
```

내부 링크·앵커·이미지, 언어 전환 링크, 논문 36건의 메타데이터·상태·주저자 표시와 인용 통계 표시를 검증합니다. 논문 상태는 기존 공개 목록 기준이며 이번 번역 작업에서 새로 조사하지 않았습니다.

`main`에 푸시하면 GitHub Actions가 검증 후 HTML과 `css/js/assets/data/ko`를 GitHub Pages에 배포합니다. 매주 자동 인용 통계 갱신도 같은 배포 과정을 사용합니다.

로컬 미리보기는 이 폴더에서 다음 명령을 실행한 후 http://127.0.0.1:8765/ko/index.html 을 엽니다.

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```
