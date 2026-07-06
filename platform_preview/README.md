# platform_preview

Twiv 캐릭터 **화면 프리뷰** 도구 (Streamlit) — 실제 제품과 유사한 **대화(챗) 화면** 과 크리에이터 프로필을 미리봅니다.

> ⚠️ **내부 검토용(internal review only) — 외부 게시용이 아닙니다.**
> - 특정 플랫폼(로고 · 상표 · 버튼 문구 · 원본 UI)을 **복제하지 않습니다.** 일반화된 카드 UI만 사용합니다.
> - 미디어는 repo(`characters/<slug>/media/`, `images/`)에서만 읽으며, 저장/전송하지 않습니다.
> - 모든 캐릭터는 **가상 성인 캐릭터(fictional, adults only)**입니다. 미성년/실존 인물 소재는 금지입니다.

## 기능 — 미리볼 화면 2종

`characters/<slug>/` 의 **`canon.md` + `media/`(온보딩 영상) + `images/`(사진)** 를 직접 읽어 화면을 구성합니다.
**수동 입력·업로드 없이 repo 데이터가 원본**입니다. 각 화면은 `components.html` iframe으로 렌더해 온보딩 영상이 자동재생(무음 루프)됩니다.

**상단 컨트롤**: 캐릭터 선택 드롭다운 + **◀ 이전 화면 / 다음 화면 ▶** (대화 화면 ↔ 프로필).

- 💬 **대화 화면** (기본) — 실제 제품 유사 구성: **세로 온보딩 영상 풀블리드** + 상단바(`‹` · `♡ 0` · `Ⓟ` · `⋮`) + **첫 대사** 오프닝 버블 + 하단 입력 UI(아바타 · `메시지를 입력하세요` · `♡` · `✳` · `↑`). 영상 업로드 전에는 커버 이미지가 대신 깔립니다.
- 👤 **크리에이터 프로필** — 아바타(커버)·이름·핸들 · 영상/좋아요/팔로워 스탯 · 바이오 · `대화 시작하기` · **영상 / 사진 / 정보** 탭
  - 🎬 영상: 온보딩 썸네일(▶ 배지) · 🖼️ 사진: `images/*.png` 3열 2:3 그리드 · ⓘ 정보: 스토리·관심사·취미·좋아하는 말·이상형 (canon 파싱)

**에셋 규칙**: `media/온보딩.mp4` = 첫 화면 영상, `images/01_커버.png` = 대표/아바타(없으면 폴더 첫 사진), `images/*.png` = 갤러리(세로 2:3 권장). 첫 대사는 canon `## 👋 첫 인사말` 의 인용문.

## 실행

```bash
cd edge_repos/chatbot_platform_twiv/platform_preview
python -m streamlit run app.py
```

→ 브라우저 http://localhost:8501. 드롭다운에서 캐릭터를 고르고 **◀ ▶** 로 화면을 넘깁니다.
(포트가 쓰이면 8502 등 다른 포트 — 실행 로그의 `Local URL` 확인.)

## Streamlit Cloud 배포

- Repository: `macximin/chatbot_platform_twiv`
- Branch: `main`
- **Main file path**: `platform_preview/app.py`
- 별도 secrets 불필요. `requirements.txt`(streamlit, pillow)만 사용.

## 구조
```
platform_preview/
  app.py             # Streamlit 앱 (대화 화면 + 프로필)
  README.md          # 이 문서
  requirements.txt   # streamlit, pillow
  .streamlit/config.toml  # 다크 테마 (twiv 핑크 #ff2e63)
  sample/            # 테스트용 미디어 (.gitkeep만 커밋)
```

## 주의
- 실제 상표/서비스명/로고/원본 UI를 넣지 마세요. 이 목업의 출력은 **외부 배포 금지**입니다.
- 온보딩 영상은 base64로 iframe에 인라인됩니다. 영상이 크면(수십 MB) 로딩이 느려질 수 있으니 프리뷰용은 짧은 세로 클립을 권장합니다.
