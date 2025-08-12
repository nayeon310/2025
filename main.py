# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

# lottie helper (requires streamlit-lottie)
try:
    from streamlit_lottie import st_lottie
    LOTTIE_AVAILABLE = True
except Exception:
    LOTTIE_AVAILABLE = False

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

/* 컨테이너 */
.container {
    max-width:1100px;
    margin:0 auto;
}

/* 랜딩 히어로 */
.hero {
    border-radius: 18px;
    padding: 22px;
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
    box-shadow: 0 12px 30px rgba(110, 90, 160, 0.06);
    margin-bottom: 20px;
    display:flex;
    gap:18px;
    align-items:center;
}

/* 제목 */
.h1 { font-size:30px; color:#6A5ACD; font-weight:800; margin-bottom:8px; }

/* 설명 */
.lead { color:#666; font-size:15px; }

/* 입력창 */
.mbti-input {
    border-radius:12px;
    padding:10px 12px;
    border: 1px solid rgba(100,100,140,0.08);
    background: rgba(255,255,255,0.98);
}

/* 버튼 */
.ghost-btn {
    background: linear-gradient(90deg,#FFD6E0,#FFEFD9);
    border-radius:12px;
    padding:10px 16px;
    font-weight:700;
    color:#6A2E6F;
    border:none;
    cursor:pointer;
}

/* 결과 카드 */
.result-card {
    border-radius: 14px;
    padding: 12px;
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.95));
    box-shadow: 0 10px 24px rgba(100,100,140,0.05);
    margin-bottom: 14px;
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
# 궁합 데이터 (필요하면 확장)
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
    "INFJ": [
        {"pair":"ENFP", "score":94, "reason":"직관과 감정의 균형으로 서로를 자극하고 지지한다.", "image":"images/INFJ_ENFP.png"},
        {"pair":"ENFJ", "score":90, "reason":"가치와 사명에 공감하며 안정적인 유대감을 형성한다.", "image":"images/INFJ_ENFJ.png"},
        {"pair":"INFP", "score":84, "reason":"내적 가치와 이상을 함께 공감하며 성장할 수 있다.", "image":"images/INFJ_INFP.png"},
    ],
    # 필요하면 16종 전체로 확장 가능
}
MBTI_TYPES = sorted(list(compat.keys()))
IMG_DIR = Path("images")
PLACEHOLDER = IMG_DIR / "placeholder.png"

# -----------------
# 유틸: 안전한 이미지 로드
# -----------------
def load_image_safe(path_or_url):
    try:
        p = Path(path_or_url)
        if p.exists():
            try:
                return Image.open(p)
            except UnidentifiedImageError:
                return None
        if isinstance(path_or_url, str) and path_or_url.startswith("http"):
            resp = requests.get(path_or_url, timeout=6)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content))
    except Exception:
        return None
    try:
        if PLACEHOLDER.exists():
            return Image.open(PLACEHOLDER)
    except Exception:
        return None
    return None

# -----------------
# lottie 로드 유틸
# -----------------
def load_lottie_url(url):
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

# -----------------
# 세션 상태 초기화
# -----------------
if "selected_mbti" not in st.session_state:
    st.session_state.selected_mbti = None

# -----------------
# 랜딩 + 입력 UI
# -----------------
st.markdown("<div class='container'>", unsafe_allow_html=True)

st.markdown("<div class='hero'>", unsafe_allow_html=True)
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("<div class='h1'>MBTI 궁합 도우미 💕</div>", unsafe_allow_html=True)
    st.markdown("<div class='lead'>너의 MBTI를 직접 입력하면, 잘 맞는 MBTI와 간단한 설명·이미지를 보여줄게. (예: INFP)</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # 입력창: 텍스트 입력 + 엔터/버튼 제출
    mbti_input = st.text_input("너의 MBTI를 입력해줘", placeholder="예: INFP", key="mbti_input")
    sub_col1, sub_col2 = st.columns([1,1])
    with sub_col1:
        if st.button("궁합 보기 ♥", key="submit_btn"):
            if not mbti_input or not isinstance(mbti_input, str):
                st.warning("MBTI를 입력해줘~ (예: INFP)")
            else:
                user_mbti = mbti_input.strip().upper()
                # 간단 검증: 4글자, I/E, N/S, F/T, P/J 조합 형태 체크
                valid_chars = set("IE") | set("NS") | set("FT") | set("PJ")
                if len(user_mbti) != 4 or any(ch not in "IE NSFTPJ".replace(" ", "") and True for ch in user_mbti): 
                    # 더 정확한 체크:
                    allowed = {"I","E","N","S","F","T","P","J"}
                    if len(user_mbti)==4 and all(c in allowed for c in user_mbti):
                        st.session_state.selected_mbti = user_mbti
                        st.experimental_rerun()
                    else:
                        st.error("유효한 MBTI 형식이 아니야. 예: INFP, ENFP 등 4글자 조합으로 입력해줘.")
                else:
                    st.session_state.selected_mbti = user_mbti
                    st.experimental_rerun()
    with sub_col2:
        if st.button("추천 예시 보기", key="example_btn"):
            st.info("예시: INFP, ENFP, INFJ 등 (대문자/소문자 구분 없이 입력 가능)")

with col2:
    # Lottie 애니메이션 (로컬 json 또는 URL)
    lottie_url = "https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json"  # 예시 URL (귀여운 캐릭터)
    lottie_json = load_lottie_url(lottie_url)
    if LOTTIE_AVAILABLE and lottie_json:
        st_lottie(lottie_json, height=220)
    else:
        # fallback: 이미지 로드 (logo/placeholder)
        logo = load_image_safe("images/logo.png")
        if logo:
            st.image(logo, width=200)
        else:
            st.markdown("<div style='text-align:center; color:#FF6B6B; font-weight:700'>여기에 귀여운 애니메이션이 표시돼요</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # hero 종료

# 애니메이션/랜딩 리소스에 대해: Lottie 같은 형태는 랜딩 모션에 특히 잘 맞아 [【10】](https://lottiefiles.com/kr/free-animations/3d-%EB%9E%9C%EB%94%A9-%ED%8E%98%EC%9D%B4%EC%A7%80).
# 랜딩 모션 아이디어는 랜디자인 샘플에서 영감을 얻으면 좋아 [【1】](https://www.behance.net/search/projects/landing%20page%20animation%20motion%20design?locale=ko_KR).

# -----------------
# 결과 영역
# -----------------
st.markdown("<br>", unsafe_allow_html=True)
if st.session_state.selected_mbti:
    mbti = st.session_state.selected_mbti
    st.markdown(f"<div style='font-weight:800; font-size:20px; color:#6A5ACD'>{mbti} 궁합 결과</div>", unsafe_allow_html=True)
    results = compat.get(mbti, [])
    if not results:
        st.info("아직 이 MBTI의 데이터가 없네. 전체 16종으로 채워줄까? 요청해줘~")
    else:
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

    # CSV 다운로드
    if st.button("결과 CSV로 저장"):
        df = pd.DataFrame(results)
        csv = df.to_csv(index=False)
        st.download_button("다운로드: CSV", csv, file_name=f"{mbti}_compat.csv", mime="text/csv")

# 하단 안내
st.markdown("---")
st.info("이미지 안내: 이미지가 없으면 'images/placeholder.png'를 넣어줘. 직접 이미지를 만들고 싶으면 '이미지 제작 도구'를 사용해서 images/ 폴더에 업로드하면 자동 표시돼.")

st.markdown("</div>", unsafe_allow_html=True)
