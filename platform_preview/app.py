"""platform_preview — Twiv 캐릭터 화면 프리뷰 (내부 검토용).

`characters/<slug>/` 의 canon.md + media/(온보딩 영상) + images/(사진) 를 **직접 로드**해서
실제 제품과 유사한 **대화(챗) 화면** 과 크리에이터 프로필을 미리본다.
사이드바 수동 입력 없이 repo 데이터가 원본. 특정 플랫폼 로고/상표/원본 UI는 복제하지 않는 일반화 UI.
외부 게시용 아님. 모든 캐릭터는 가상 성인 캐릭터.

대화 화면 = 세로 온보딩 영상(풀블리드) + 첫 대사 + 하단 입력 UI.
에셋 규칙: media/온보딩.mp4 = 첫 화면 영상, images/01_커버.png = 대표/아바타, images/*.png = 갤러리(세로 2:3).
"""

import base64
import html
import io
import re
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="platform_preview", page_icon="💬", layout="centered")

ACCENT = "#ff2e63"
CHARS_DIR = Path(__file__).resolve().parent.parent / "characters"
COVER_NAMES = ("01_커버.png", "커버.png", "01_thumbnail.png")
VIDEO_NAMES = ("온보딩.mp4",)
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_SLUG = "sports-yuserin"

# canon에 없는 데모 수치 (프리뷰용, 가짜)
DEMO_LIKES = "12.4천"
DEMO_FOLLOWERS = "2.1만"


# ------------------------------------------------ 미디어 헬퍼
def _prep(img: Image.Image, ratio: float) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    w, h = img.size
    if w / h > ratio:
        nw = int(round(h * ratio))
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(round(w / ratio))
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img.thumbnail((1080, 1350))
    return img


@st.cache_data(show_spinner=False)
def img_uri(path_str: str, mtime: int, ratio: float) -> str:
    img = _prep(Image.open(path_str), ratio)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=86)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def video_uri(path_str: str, mtime: int) -> str:
    data = Path(path_str).read_bytes()
    return "data:video/mp4;base64," + base64.b64encode(data).decode()


def esc(s) -> str:
    return html.escape(s or "")


# ------------------------------------------------ 캐릭터 로딩 (canon.md + media/ + images/)
def parse_canon(text):
    fm, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    sections = {}
    for hm in re.finditer(r"(?ms)^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", body):
        sections[hm.group(1).strip()] = hm.group(2).strip()
    return fm, sections


def sect(sections, *needles):
    for k, v in sections.items():
        if any(n in k for n in needles):
            return v
    return ""


def bullets(t):
    return [re.sub(r"^[-*]\s*", "", ln).strip() for ln in t.splitlines() if ln.strip()[:1] in "-*"]


def quotes(t):
    out = []
    for ln in t.splitlines():
        s = ln.strip()
        if s.startswith(">"):
            s = s.lstrip(">").strip().strip('"').strip("“”")
            if s:
                out.append(s)
    return out


def kv_from_bullets(t):
    d = {}
    for b in bullets(t):
        if ":" in b:
            k, v = b.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def find_cover(images_dir: Path):
    for name in COVER_NAMES:
        p = images_dir / name
        if p.exists():
            return p
    imgs = list_images(images_dir)
    return imgs[0] if imgs else None


def list_images(images_dir: Path):
    if not images_dir.exists():
        return []
    return sorted(p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXT)


def find_video(media_dir: Path):
    if not media_dir.exists():
        return None
    for name in VIDEO_NAMES:
        p = media_dir / name
        if p.exists():
            return p
    vids = sorted(p for p in media_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp4")
    return vids[0] if vids else None


def _sig(slug):
    d = CHARS_DIR / slug
    fs = [d / "canon.md"] + list_images(d / "images")
    v = find_video(d / "media")
    if v:
        fs.append(v)
    return tuple((f.name, int(f.stat().st_mtime)) for f in fs if f.exists())


@st.cache_data(show_spinner=False)
def load_char(slug, sig):
    d = CHARS_DIR / slug
    fm, sc = parse_canon((d / "canon.md").read_text(encoding="utf-8"))
    imgs_dir = d / "images"
    cover = find_cover(imgs_dir)
    photos = list_images(imgs_dir)
    video = find_video(d / "media")
    basic = kv_from_bullets(sect(sc, "기본 정보"))
    age = basic.get("나이", "")
    mnum = re.search(r"\d+", age)
    says = quotes(sect(sc, "좋아하는 말"))
    first = quotes(sect(sc, "첫 인사"))
    tags = [t.strip() for t in fm.get("hashtags", "").split(",") if t.strip()]
    return {
        "slug": slug,
        "name": fm.get("channel_display_name") or fm.get("name") or slug,
        "handle": fm.get("channel_handle") or "@" + slug.replace("-", "."),
        "age": mnum.group() if mnum else age,
        "job": basic.get("직업", fm.get("job", "")),
        "concept": fm.get("concept_title", "") or fm.get("name", ""),
        "intro": sect(sc, "소개"),
        "story": sect(sc, "스토리 개요"),
        "video_hook": sect(sc, "온보딩"),
        "interests": bullets(sect(sc, "관심사")),
        "hobbies": bullets(sect(sc, "취미")),
        "says": says,
        "ideal": sect(sc, "이상형"),
        "first_line": first[0] if first else (says[0] if says else ""),
        "hashtags": tags,
        "cover": {"path": str(cover), "mtime": int(cover.stat().st_mtime)} if cover else None,
        "photos": [{"path": str(p), "mtime": int(p.stat().st_mtime)} for p in photos],
        "video": {"path": str(video), "mtime": int(video.stat().st_mtime)} if video else None,
    }


def list_chars():
    if not CHARS_DIR.exists():
        return []
    out = []
    for dd in sorted(CHARS_DIR.iterdir()):
        if dd.is_dir() and dd.name != "_TEMPLATE" and (dd / "canon.md").exists():
            if find_cover(dd / "images") or find_video(dd / "media"):
                out.append(dd.name)
    return sorted(out, key=lambda slug: (slug != DEFAULT_SLUG, slug))


# ------------------------------------------------ 공통 조각
def hook_line(char):
    return char["intro"].split(".")[0].strip() if char["intro"] else char["concept"]


def hashtags(char):
    src = char["hashtags"] or [x.split("(")[0].split("/")[0].split("·")[0].split(",")[0].strip()
                               for x in (char["interests"] + char["hobbies"])]
    return ["#" + x.replace(" ", "") for x in src][:5]


def cover_uri(char, ratio):
    return img_uri(char["cover"]["path"], char["cover"]["mtime"], ratio) if char["cover"] else ""


def big_media_tag(char, cls):
    """풀블리드 미디어: 영상 있으면 자동재생, 없으면 커버."""
    if char["video"]:
        uri = video_uri(char["video"]["path"], char["video"]["mtime"])
        return f'<video class="{cls}" src="{uri}" autoplay muted loop playsinline preload="auto"></video>'
    if char["cover"]:
        return f'<img class="{cls}" src="{cover_uri(char, 9 / 16)}"/>'
    return f'<div class="{cls}" style="background:#222;"></div>'


CSS = """
<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:transparent;font-family:-apple-system,'Segoe UI',Roboto,'Noto Sans KR',sans-serif;}
  .phone{width:360px;height:720px;margin:0 auto;position:relative;background:#000;
         border-radius:22px;overflow:hidden;color:#f2f2f5;box-shadow:0 8px 40px rgba(0,0,0,.5);}
  .phone.scroll{overflow-y:auto;background:#0b0b0f;}
  .phone.scroll::-webkit-scrollbar{width:0;}

  /* ---- chat (대화) ---- */
  .cmedia{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;}
  .cgrad-top{position:absolute;top:0;left:0;right:0;height:96px;
             background:linear-gradient(to bottom,rgba(0,0,0,.55),transparent);}
  .cgrad-bot{position:absolute;bottom:0;left:0;right:0;height:260px;
             background:linear-gradient(to top,rgba(0,0,0,.82),rgba(0,0,0,.25) 55%,transparent);}
  .ctop{position:absolute;top:0;left:0;right:0;height:52px;display:flex;align-items:center;
        justify-content:space-between;padding:0 12px;z-index:6;}
  .ctop .grp{display:flex;align-items:center;gap:14px;}
  .ctop .ic{color:#fff;font-size:1.35rem;line-height:1;}
  .ctop .like{display:flex;align-items:center;gap:5px;font-size:.95rem;color:#fff;}
  .ctop .pbadge{width:24px;height:24px;border-radius:50%;border:1.5px solid #fff;color:#fff;
                font-size:.72rem;font-weight:800;display:flex;align-items:center;justify-content:center;}
  .obubble{position:absolute;left:12px;right:56px;bottom:78px;z-index:6;display:flex;gap:8px;align-items:flex-end;}
  .obubble .oav{width:34px;height:34px;border-radius:50%;overflow:hidden;flex:0 0 34px;border:1px solid rgba(255,255,255,.4);}
  .obubble .oav img{width:100%;height:100%;object-fit:cover;}
  .obubble .obody{max-width:100%;}
  .obubble .oname{font-size:.72rem;color:#ffb3c8;font-weight:700;margin:0 0 3px 4px;}
  .obubble .otext{background:rgba(20,20,26,.82);color:#f4f4f6;padding:9px 12px;border-radius:4px 14px 14px 14px;
                  font-size:.86rem;line-height:1.45;backdrop-filter:blur(2px);}
  .composer{position:absolute;left:10px;right:10px;bottom:14px;z-index:7;display:flex;align-items:center;gap:8px;}
  .composer .cav{width:38px;height:38px;border-radius:50%;overflow:hidden;flex:0 0 38px;
                 border:1.5px solid rgba(255,255,255,.5);}
  .composer .cav img{width:100%;height:100%;object-fit:cover;}
  .composer .cinput{flex:1;height:40px;border-radius:20px;background:rgba(30,30,36,.7);
                    border:1px solid rgba(255,255,255,.14);display:flex;align-items:center;
                    padding:0 10px 0 14px;gap:10px;backdrop-filter:blur(4px);}
  .composer .cinput .ph{flex:1;color:#c9c9d0;font-size:.85rem;}
  .composer .cinput .ic{color:#e2e2e8;font-size:1.05rem;line-height:1;}
  .composer .csend{width:38px;height:38px;border-radius:50%;flex:0 0 38px;background:rgba(245,245,248,.92);
                   color:#111;font-size:1.15rem;font-weight:700;display:flex;align-items:center;justify-content:center;}

  /* ---- profile ---- */
  .pbar{height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;
        border-bottom:1px solid #1c1c22;font-weight:700;position:sticky;top:0;background:#0b0b0f;z-index:5;}
  .phead{display:flex;gap:14px;align-items:center;padding:16px 16px 8px;}
  .avatar{width:76px;height:76px;border-radius:50%;overflow:hidden;flex:0 0 76px;border:2px solid #26262e;}
  .avatar img{width:100%;height:100%;object-fit:cover;}
  .avatar .ph{width:100%;height:100%;background:linear-gradient(135deg,%ACCENT%,#7a4bc9);
              display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.5rem;}
  .pname{font-weight:800;font-size:1.08rem;}
  .phandle{color:#a0a0aa;font-size:.82rem;margin-top:1px;}
  .stats{display:flex;gap:18px;margin-top:8px;}
  .stats .s b{font-weight:800;}.stats .s span{color:#a0a0aa;font-size:.72rem;margin-left:3px;}
  .bio{padding:2px 16px 12px;font-size:.85rem;color:#dcdce2;line-height:1.5;}
  .cta2{margin:0 16px 14px;text-align:center;background:%ACCENT%;color:#fff;padding:11px;
        border-radius:12px;font-weight:800;font-size:.92rem;}
  .tabbar{display:flex;border-top:1px solid #1c1c22;border-bottom:1px solid #1c1c22;}
  .tabbtn{flex:1;background:none;border:none;color:#8a8a92;padding:11px 0;font-size:.86rem;
          font-weight:700;cursor:pointer;}
  .tabbtn.active{color:#fff;box-shadow:inset 0 -2px 0 %ACCENT%;}
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;padding:3px;}
  .tile{position:relative;width:100%;padding-bottom:150%;background:#16161c;overflow:hidden;}
  .tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
  .tile .play{position:absolute;top:6px;right:6px;font-size:1rem;filter:drop-shadow(0 1px 2px #000);}
  .tile .dur{position:absolute;bottom:6px;right:6px;background:rgba(0,0,0,.6);color:#fff;
             font-size:.62rem;padding:1px 5px;border-radius:4px;}
  .isec{padding:12px 16px;}
  .isec h4{font-size:.9rem;margin-bottom:5px;}
  .isec .body{color:#dcdce2;font-size:.85rem;line-height:1.55;}
  .chip{display:inline-block;background:#1c1c26;border-radius:999px;padding:3px 10px;margin:0 4px 4px 0;font-size:.78rem;}
  .pane{display:none;}.pane.show{display:block;}
  .nav{display:flex;align-items:center;justify-content:space-around;padding:8px 0 6px;
       border-top:1px solid #1c1c22;background:#0b0b0f;}
  .nav .n{display:flex;flex-direction:column;align-items:center;gap:1px;font-size:.6rem;color:#9a9aa2;}
  .nav .n.on{color:#fff;}.nav .n .g{font-size:1.15rem;}
  .nav .plusbtn{width:34px;height:26px;border-radius:8px;
       background:linear-gradient(135deg,%ACCENT%,#ff7a3d);color:#fff;font-size:1.1rem;
       font-weight:700;display:flex;align-items:center;justify-content:center;}
</style>
"""
CSS = CSS.replace("%ACCENT%", ACCENT)

AUTOPLAY_JS = """
<script>
  document.addEventListener('DOMContentLoaded', function(){
    var v = document.querySelector('video');
    if(v){ v.muted = true; var p = v.play(); if(p && p.catch){ p.catch(function(){}); } }
  });
  function twivTab(name){
    var panes = document.querySelectorAll('.pane');
    for(var i=0;i<panes.length;i++){ panes[i].classList.remove('show'); }
    var btns = document.querySelectorAll('.tabbtn');
    for(var j=0;j<btns.length;j++){ btns[j].classList.remove('active'); }
    var pane = document.getElementById('pane-'+name); if(pane){ pane.classList.add('show'); }
    var btn = document.getElementById('tab-'+name); if(btn){ btn.classList.add('active'); }
  }
</script>
"""


def render(body_html, height):
    st.iframe(CSS + body_html + AUTOPLAY_JS, height=height)


def nav_bar(active="chat"):
    def n(g, lb, key):
        on = " on" if key == active else ""
        return f'<div class="n{on}"><div class="g">{g}</div>{lb}</div>'
    return (
        '<div class="nav">'
        + n("🏠", "홈", "home")
        + n("🔍", "탐색", "search")
        + '<div class="n"><div class="plusbtn">＋</div></div>'
        + n("💬", "채팅", "chat")
        + n("👤", "프로필", "profile")
        + "</div>"
    )


# ================================================================ 뷰
def view_chat(char):
    """실제 제품과 유사한 대화 화면: 풀블리드 영상 + 첫 대사 + 하단 입력 UI."""
    avatar = f'<img src="{cover_uri(char, 1.0)}"/>' if char["cover"] else ""
    first = char["first_line"] or char["concept"]
    body = (
        '<div class="phone">'
        f'{big_media_tag(char, "cmedia")}'
        '<div class="cgrad-top"></div><div class="cgrad-bot"></div>'
        # top bar: ‹  ♡ 0        Ⓟ  ⋮
        '<div class="ctop">'
        '<div class="grp"><span class="ic">‹</span>'
        '<span class="like">♡ <span>0</span></span></div>'
        '<div class="grp"><span class="pbadge">P</span><span class="ic">⋮</span></div>'
        "</div>"
        # opening line (첫 대사)
        '<div class="obubble">'
        f'<div class="oav">{avatar}</div>'
        f'<div class="obody"><div class="oname">{esc(char["name"])}</div>'
        f'<div class="otext">{esc(first)}</div></div></div>'
        # bottom composer
        '<div class="composer">'
        f'<div class="cav">{avatar}</div>'
        '<div class="cinput"><span class="ph">메시지를 입력하세요</span>'
        '<span class="ic">♡</span><span class="ic">✳</span></div>'
        '<div class="csend">↑</div>'
        "</div>"
        "</div>"
    )
    render(body, 744)


def view_profile(char):
    avatar = (
        f'<div class="avatar"><img src="{cover_uri(char, 1.0)}"/></div>'
        if char["cover"]
        else f'<div class="avatar"><div class="ph">{esc(char["name"][:1])}</div></div>'
    )
    bio = []
    line1 = " · ".join(x for x in [(char["age"] + "세") if char["age"] else "", char["job"]] if x)
    if line1:
        bio.append("🎬 " + line1)
    if char["interests"] or char["hobbies"]:
        bio.append("🍃 " + " · ".join(char["interests"] + char["hobbies"]))
    if char["intro"]:
        bio.append("✨ " + hook_line(char))
    bio_html = "<br/>".join(esc(x) for x in bio)

    vtile = ""
    if char["video"]:
        thumb = f'<img src="{cover_uri(char, 2 / 3)}"/>' if char["cover"] else ""
        vtile = f'<div class="tile">{thumb}<div class="play">▶</div><div class="dur">온보딩</div></div>'
    photo_tiles = "".join(
        f'<div class="tile"><img src="{img_uri(p["path"], p["mtime"], 2 / 3)}"/></div>'
        for p in char["photos"]
    )

    def chips(xs):
        return "".join(f'<span class="chip">{esc(x)}</span>' for x in xs)

    story_html = esc(char["story"]).replace("\n\n", "<br/><br/>").replace("\n", "<br/>")
    says_html = "<br/>".join(f"“{esc(x)}”" for x in char["says"])
    info_html = (
        f'<div class="isec"><h4>📖 스토리 개요</h4><div class="body">{story_html}</div></div>'
        f'<div class="isec"><h4>✨ 관심사</h4><div class="body">{chips(char["interests"])}</div></div>'
        f'<div class="isec"><h4>🎯 취미</h4><div class="body">{chips(char["hobbies"])}</div></div>'
        f'<div class="isec"><h4>💬 좋아하는 말</h4><div class="body">{says_html}</div></div>'
        f'<div class="isec"><h4>💕 이상형</h4><div class="body">{esc(char["ideal"])}</div></div>'
    )
    n_videos = 1 if char["video"] else 0
    body = (
        '<div class="phone scroll">'
        f'<div class="pbar"><span>‹ {esc(char["handle"].lstrip("@"))}</span><span>⋮</span></div>'
        f'<div class="phead">{avatar}<div>'
        f'<div class="pname">{esc(char["name"])}</div>'
        f'<div class="phandle">{esc(char["handle"])}</div>'
        '<div class="stats">'
        f'<div class="s"><b>{n_videos}</b><span>영상</span></div>'
        f'<div class="s"><b>{DEMO_LIKES}</b><span>좋아요</span></div>'
        f'<div class="s"><b>{DEMO_FOLLOWERS}</b><span>팔로워</span></div>'
        "</div></div></div>"
        f'<div class="bio">{bio_html}</div>'
        '<div class="cta2">💬 대화 시작하기</div>'
        '<div class="tabbar">'
        '<button class="tabbtn active" id="tab-video" onclick="twivTab(\'video\')">🎬 영상</button>'
        '<button class="tabbtn" id="tab-photo" onclick="twivTab(\'photo\')">🖼️ 사진</button>'
        '<button class="tabbtn" id="tab-info" onclick="twivTab(\'info\')">ⓘ 정보</button>'
        "</div>"
        f'<div class="pane show" id="pane-video"><div class="grid">{vtile}</div></div>'
        f'<div class="pane" id="pane-photo"><div class="grid">{photo_tiles}</div></div>'
        f'<div class="pane" id="pane-info">{info_html}</div>'
        + nav_bar("profile")
        + "</div>"
    )
    render(body, 744)


# ================================================================ 상단 컨트롤 + 라우팅
chars = list_chars()
if not chars:
    st.error(f"`canon.md` + 온보딩 영상/커버 이미지를 가진 캐릭터 폴더가 없습니다:\n\n`{CHARS_DIR}`")
    st.stop()

slug = st.selectbox("캐릭터", chars, index=0, label_visibility="collapsed")
char = load_char(slug, _sig(slug))

VIEWS = ["💬 대화 화면", "👤 크리에이터 프로필"]
st.session_state.setdefault("view_i", 0)
navL, navC, navR = st.columns([1, 3, 1])
if navL.button("◀ 이전 화면", use_container_width=True):
    st.session_state["view_i"] = (st.session_state["view_i"] - 1) % len(VIEWS)
if navR.button("다음 화면 ▶", use_container_width=True):
    st.session_state["view_i"] = (st.session_state["view_i"] + 1) % len(VIEWS)
vi = st.session_state["view_i"]
navC.markdown(
    f"<div style='text-align:center;font-weight:800;padding-top:6px;'>{VIEWS[vi]}"
    f" &nbsp;·&nbsp; {vi + 1}/{len(VIEWS)}</div>",
    unsafe_allow_html=True,
)

if vi == 0:
    view_chat(char)
else:
    view_profile(char)

st.caption(
    f"· 내부 검토용 목업 (Twiv) · `characters/{slug}` 데이터 로드 · 특정 서비스 UI/로고/CTA 복제 아님 · 가상 성인 캐릭터 ·"
)
