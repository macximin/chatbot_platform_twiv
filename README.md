# chatbot_platform_twiv

Twiv 캐릭터 제품의 **정본·원본 저장소**. 상위 `chatbot_hq`의 DDD-lite 철학을 따르되,
이 repo는 **플랫폼(Twiv) 스코프 + 캐릭터 복수**이므로 "캐릭터 = bounded context"로 나눈다.

- 부모 repo에서는 `edge_repos/`로 격리된 **독립 child repo**다 (submodule 아님).
- **private 전용.** 성인·상업 콘텐츠. 비밀(`.env` 등)은 절대 커밋 금지.
- **Twiv은 영상 우선(릴스/쇼츠형) 플랫폼이다.** 캐릭터의 첫 표면은 세로 온보딩 영상이고, 사진은 보조 갤러리다.
  (자매 repo `chatbot_platform_liveher`는 인스타형 사진 피드 — 포맷이 다르다.)

## 폴더 구조

```
chatbot_platform_twiv/
├─ _platform/        Twiv 공유 커널 (캐릭터 이름 0개)
│  ├─ profile_schema.md   wiki/canon 계약 = 사람이 읽는 정본 (영상 우선)
│  ├─ create_flow.md      Twiv 등록 입력값 / 폼 필드
│  ├─ lorebook_schema.md  로어북 계약 = 운용 규칙/금지선/트리거
│  └─ copy_rules.md       외부 카피 금지어 + 감리 라인 (영상 감리 포함)
├─ backlog/          아이디어 = 작업 보드 IDEA 카드의 git 정본
├─ characters/       캐릭터 1명 = 폴더 1개 (bounded context)
│  ├─ _TEMPLATE/     복제용 (= Notion 캐릭터 도메인/템플릿)
│  │  ├─ canon.md         정본 = wiki 필드
│  │  ├─ meta.yml         slug / notion_url / 상태 / 태그 / copy_risk
│  │  ├─ images/          사진(세로 2:3) + INDEX.md
│  │  └─ media/           온보딩 영상(세로) + INDEX.md
│  ├─ sports-yuserin/  유세린 (스포츠) — 봐주기 없는 스포츠부 후배
│  └─ brat-yeonseo/    하연서 (일상) — 새벽 편의점 당돌한 알바 후배
└─ platform_preview/   Streamlit 화면 프리뷰 (대화 화면 + 프로필, 내부 검토용)
   └─ app.py · requirements.txt · README.md · .streamlit/config.toml
```

## 캐릭터 에셋 규칙

- `media/온보딩.mp4` — **첫 화면 에셋.** 세로 온보딩 영상(6초 내 인상).
- `images/01_커버.png` — 대표/커버(프로필 아바타). 없으면 폴더 첫 사진을 커버로.
- `images/*.png` — 보조 갤러리(세로 2:3 권장).
- 원본 경로/라벨은 `media/INDEX.md`, `images/INDEX.md`에만 적고 Notion은 경로만 포인팅.

## 프리뷰 실행

```bash
cd edge_repos/chatbot_platform_twiv/platform_preview
python -m streamlit run app.py
```

→ 브라우저 http://localhost:8501. `characters/<slug>/` 의 `canon.md` + `media/` + `images/` 를 직접 읽어
**대화(챗) 화면**(영상 + 첫 대사 + 하단 입력 UI) / 크리에이터 프로필 2화면을 미리본다. 자세한 건 `platform_preview/README.md`.

## 안전

- 실제 상표/서비스명/로고/원본 UI를 복제하지 않는다(일반화). 프리뷰 출력물은 **외부 배포 금지**.
- 모든 캐릭터는 **가상 성인 캐릭터(fictional, adults only)**. 미성년/실존 인물 소재 금지 (`_platform/copy_rules.md`).
- 최종 등록(제출)은 사용자 명시 승인 없이 자동 실행 금지.
