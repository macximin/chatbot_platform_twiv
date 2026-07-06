# Twiv 등록 입력값 / 폼 필드

> ⚠️ TODO: 실제 create 폼 필드/순서는 로그인 상태의 Twiv 등록 화면에서 최종 확인해 확정할 것.
> 아래는 현재 제품 설계 기준의 입력값 계약이다. 플랫폼 UI가 바뀌면 이 문서와 `profile.twiv.md` 템플릿을 같이 고친다.
> **Twiv은 영상 우선 플랫폼** — 온보딩 세로 영상이 첫 화면 에셋이다.

## 핵심 분리

| 레이어 | 파일 | 역할 |
| --- | --- | --- |
| 사람이 읽는 정본 | `canon.md` | Notion `wiki`와 맞추는 캐릭터 표면 |
| 장기 운용 규칙 | `lorebook.md` | 호감도, 금지선, 트리거, 아이템 해석 |
| 플랫폼 복붙본 | `profile.twiv.md` | Twiv 폼에 맞춘 압축 투영 |

## 폼 필드 계약

| 폼 필드 | repo 소스 | 비고 |
| --- | --- | --- |
| 캐릭터 이름 | `profile.twiv.md` / `meta.yml:name` | 실제 노출명. 컨셉 타이틀과 다를 수 있음 |
| 채널 계정 | `profile.twiv.md` / `meta.yml:channel_handle` | 릴스형 피드/프로필 표면용 |
| 온보딩 영상 | `characters/<slug>/media/온보딩.mp4` + `media/INDEX.md` | **첫 화면 에셋.** 세로 영상. 6초 내 인상 |
| 캐릭터 소개 | `profile.twiv.md` | 온보딩 영상 위 훅. 1~3문장 |
| 캐릭터 상세 설정 | `profile.twiv.md` | `canon.md` + `lorebook.md` 압축본 |
| 캐릭터 에셋(사진) | `characters/<slug>/images/*` + `images/INDEX.md` | 대표/갤러리/성인씬 포인터 분리 |
| 시작 상황 | `profile.twiv.md` | 시작 장면 이름 |
| 첫 상황 | `profile.twiv.md` | 대화 시작 전 장면 설명 |
| 첫 대사 | `profile.twiv.md` | 캐릭터의 첫 발화 |
| 해시태그 | `profile.twiv.md` / `meta.yml:hashtags` | 외부 노출 태그. 위험 태그 금지 |
| 추가 정보 | `profile.twiv.md` | 나이, 키, 직업, 관심사, 취미, 좋아하는 말, 이상형 등 |

## 파일별 책임

- `canon.md`에는 플랫폼 폼 제한 때문에 깎이지 않은 정본만 둔다.
- `lorebook.md`에는 폼에 다 넣기 무거운 운용 규칙과 안전선을 둔다.
- `profile.twiv.md`에는 실제 복붙 가능한 최종 입력값만 둔다.
- `media/INDEX.md`에는 온보딩 영상 원본 경로와 컷 라벨만 둔다.
- `images/INDEX.md`에는 사진 원본 경로와 상황 라벨만 둔다. Notion에는 업로드 대신 경로만 포인팅한다.

## 등록 원칙

- 최종 등록(제출) 버튼은 **사용자 명시 승인 없이 자동 클릭 금지.**
- 등록 스냅샷/이력은 승격된 캐릭터의 `characters/<slug>/`(필요 시 `audits/` 확장)에 남긴다.
