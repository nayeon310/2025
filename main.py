# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="MBTI 궁합 도우미 · 귀여운 버전", layout="wide", initial_sidebar_state="collapsed")

# -----------------
# 기본 스타일 (부드러운 파스텔)
# -----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;600;800&display=swap');

body, .stApp {
    background: linear-gradient(180deg, #FFF7FB 0%, #F5FDFF 100%);
    font-family: 'Nunito', sans-serif;
}

/* 헤로 섹션 */
.hero {
    border-radius: 20px;
    padding: 28px;
    background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.7));
    box-shadow: 0 12px 30px rgba(110, 90, 160, 0.06);
    margin-bottom: 18px;
    display: flex;
    gap: 20px;
    align-items: center;
}

/* 큰 제목 */
.h1 {
    font-size: 32px;
    color: #6A5ACD;
    font-weight: 800;
}

/* 서브 텍스트 */
.lead {
    color: #6b6b6b;
    font-size: 16px;
}

/* 시작 버튼 */
.start-btn {
    background: linear-gradient(90deg,#FFD6E0,#FFEFD9);
    border: none;
    color: #6A2E6F;
    padding: 12px 22px;
    border-radius: 14px;
    font-weight: 700;
    box-shadow: 0 8px 18px rgba(106,90,205,0.12);
}

/* MBTI 버튼 카드 */
.mbti-card {
    background: rgba(255,255,255,0.9);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(100,100,140,0.05);
    transition: transform .12s ease-in-out;
}
.mbti-card:hover { transform: translateY(-6px); }

/* 결과 카드 */
.result-card {
    border-radius: 14px;
    padding: 14px;
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
    box-shadow: 0 12px 30px rgba(100,100,140,0.06);
    margin-bottom: 16px;
}
.small-muted { color:#888; font-size:13px; }
.score-pill {
    background: linear-gradient(90deg,#FFD6E0,#FFECB3);
    padding:6px 10px;
    border-radius:999px;
    font-weight:700;
    color:#6A2E6F;
}
</style>
""", unsafe_allow_html=True)

# -----------------
# 샘플 궁합 데이터 (간단)
# -----------------
compat = {
    "INFP": [
        {"pair":"ENFJ", "score":92, "reason":"감정과 가치에서 서로를 잘 보완하며, 응원해주는 관계가 된다.", "image":"images/INFP_ENFJ.png"},
        {"pair":"ENFP", "score":88, "reason":"창의성과 이상을 공유하며 서로에게 영감을 준다.", "image":"images/INFP_ENFP.png"},
        {"pair":"INFJ", "score":84, "reason":"내향적 직관과 감정으로 깊은 이해를 나눌 수 있다.", "image":"images/INFP_INFJ.png"},
    ],
    "ENFP": [
        {"pair":"INFJ", "score":94, "reason":"상호 보완적 직관과 감정으로 깊은 케미가 난다.", "image":"images/ENFP_INFJ.png"},
        {"pair":"INTJ", "score":83, "reason":"아이디어와 실행이 만나 좋은 시너지를 낼 수 있다.", "image":"images/ENFP_INTJ.png"},
        {"pair":"INFP", "score":88, "reason":"감정과 창의성에서 공감대를 형성한다.", "image":"images/ENFP_INFP.png"},
    ],
    # ... 나머지 MBTI도 위 형식으로 추가 가능 (편의상 일부만 넣음)
}

MBTI_TYPES = sorted(list(compat.keys()))

# -----------------
# 이미지 로드 유틸 (로컬 우선, 다음 URL)
# -----------------
IMG_DIR = Path("images")
PLACEHOLDER = IMG_DIR / "placeholder.png"

def load_image_safe(path_or_url):
    try:
        p = Path(path_or_url)
        if p.exists():
            return Image.open(p)
        # URL 시도
        if str(path_or_url).startswith("http"):
            resp = requests.get(path_or_url, timeout=5)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content))
    except Exception:
        pass
    # 대체 이미지 시도
    try:
        if PLACEHOLDER.exists():
            return Image.open(PLACEHOLDER)
    except Exception:
        pass
    return None

# -----------------
# 세션 상태 초기화
# -----------------
if "started" not in st.session_state:
    st.session_state.started = False
if "selected_mbti" not in st.session_state:
    st.session_state.selected_mbti = None

# -----------------
# 랜딩 화면
# -----------------
def show_landing():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<div class='h1'>MBTI 궁합 도우미 💕</div>", unsafe_allow_html=True)
        st.markdown("<div class='lead'>너의 MBTI를 선택하면 잘 맞는 MBTI를 깔끔한 카드로 보여줄게. 귀여운 이미지와 짧은 설명까지 준비했어.</div>", unsafe_allow_html=True)
        st.markdown("<br>")
        if st.button("START ♥️", key="start_btn", help="클릭하면 MBTI 선택 화면으로 이동해요"):
            st.session_state.started = True
    with col2:
        # 로고/일러스트 자리 (로컬 이미지나 URL 적용 가능)
        logo = load_image_safe("images/logo.png")  # 프로젝트 images/logo.png 권장
        if logo:
            st.image(logo, width=160)
        else:
            # 간단한 텍스트 대체
            st.markdown("<div style='text-align:center; color:#FF6B6B; font-weight:800; font-size:14px'>♡ 귀여운 로고를 넣어봐요 ♡</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>")

# -----------------
# MBTI 선택 화면
# -----------------
def show_mbti_picker():
    st.markdown("### MBTI 선택 🧸", unsafe_allow_html=True)
    st.markdown("버튼을 눌러 너의 MBTI를 고르면 바로 궁합을 보여줄게!", unsafe_allow_html=True)
    rows = []
    per_row = 4
    for i in range(0, len(MBTI_TYPES), per_row):
        rows.append(MBTI_TYPES[i:i+per_row])

    for row in rows:
        cols = st.columns(per_row)
        for col, m in zip(cols, row):
            with col:
                # 각 버튼을 카드형으로 보이게 함
                st.markdown(f"<div class='mbti-card'><div style='font-weight:800; color:#6A5ACD; font-size:16px'>{m}</div><div class='small-muted'>클릭해서 선택</div></div>", unsafe_allow_html=True)
                if st.button(f"선택 {m}", key=f"pick_{m}"):
                    st.session_state.selected_mbti = m
                    st.session_state.started = True
                    # 페이지 바로 아래로 스크롤될 수 있게 간단히 리렌더
                    st.experimental_rerun()

# -----------------
# 결과 화면
# -----------------
def show_results(mbti):
    st.markdown(f"<div style='display:flex; align-items:center; gap:14px'><div style='font-weight:800; font-size:20px; color:#6A5ACD'>{mbti} 궁합 결과</div><div class='small-muted'>아래에서 서로 잘 맞는 MBTI를 확인해봐!</div></div>", unsafe_allow_html=True)
    st.write("")
    results = compat.get(mbti, [])
    if not results:
        st.info("아직 이 MBTI의 데이터가 없어요. 데이터 추가 요청해줘~")
        return

    cols = st.columns(len(results))
    for i, item in enumerate(results):
        col = cols[i]
        with col:
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            img = load_image_safe(item.get("image", ""))
            if img:
                st.image(img, use_column_width=True, caption=f"{mbti} ↔ {item['pair']}")
            else:
                st.markdown("<div style='height:140px; display:flex; align-items:center; justify-content:center; color:#999; background:#FFF7F9; border-radius:10px;'>이미지를 images/ 폴더에 넣어줘요</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-top:8px'><div style='font-weight:800; color:#6A5ACD'>{item['pair']}</div><div class='score-pill'>{item['score']}%</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-muted' style='margin-top:6px'>{item['reason']}</div>", unsafe_allow_html=True)
            with st.expander("더 자세히 보기"):
                st.write("- 강점: 서로 어떻게 잘 맞는지 예시를 적어줘.")
                st.write("- 유의할 점: 갈등 포인트와 해결 팁을 적어줘.")
                st.write("- 팁: 소소한 데이트 아이디어 또는 소통 팁을 적어줘.")
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# 레이아웃 로직
# -----------------
st.markdown("<div style='max-width:1100px; margin:0 auto'>", unsafe_allow_html=True)

if not st.session_state.started:
    show_landing()
    # 아래에 화면 안내(짧게)
    st.markdown("<div class='small-muted'>원하면 랜딩에 짧은 애니메이션(간단한 Lottie)이나 배경 일러스트도 넣어줄게~</div>", unsafe_allow_html=True)
else:
    # 선택기가 먼저 보이게 하고, 선택이 있으면 결과 표시
    show_mbti_picker()
    if st.session_state.selected_mbti:
        st.markdown("---")
        show_results(st.session_state.selected_mbti)
        # 다운로드 버튼 (선택 결과를 CSV로)
        if st.button("결과 CSV로 다운로드"):
            df = pd.DataFrame(compat.get(st.session_state.selected_mbti, []))
            csv = df.to_csv(index=False)
            st.download_button("다운로드: CSV", csv, file_name=f"{st.session_state.selected_mbti}_compat.csv", mime="text/csv")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# 푸터 안내 (이미지 제작 관련)
# -----------------
st.markdown("---")
st.info("이미지 안내: 현재는 직접 이미지를 생성하진 못해. '이미지 제작 도구'로 MBTI 쌍별 이미지를 만들고 프로젝트의 images/ 폴더에 넣어줘. 파일명 예: INFP_ENFJ.png")
