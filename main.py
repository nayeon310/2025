# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="MBTI 궁합 도우미", layout="wide", initial_sidebar_state="expanded")

# --- 스타일: 밝은 파스텔 테마 (간단한 CSS) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #FFF8FB 0%, #F0FBFF 100%); }
    .card {
        border-radius: 14px;
        padding: 16px;
        background: rgba(255,255,255,0.9);
        box-shadow: 0 6px 18px rgba(100,100,140,0.08);
        margin-bottom: 16px;
    }
    .mbti-title { font-weight:700; font-size:20px; color:#6A5ACD; }
    .sub { color:#555555; }
</style>
""", unsafe_allow_html=True)

# --- 샘플 궁합 데이터 ---
# 실제 서비스라면 CSV/DB로 관리. 아래는 예시 매핑(각 MBTI별 상위 3개 추천)
compat = {
    "INFP": [
        {"pair":"ENFJ", "score":92, "reason":"감정과 가치에서 서로를 잘 보완하며, 응원해주는 관계가 된다.", "image":"images/INFP_ENFJ.png"},
        {"pair":"ENFP", "score":88, "reason":"창의성과 이상을 공유하며 서로에게 영감을 준다.", "image":"images/INFP_ENFP.png"},
        {"pair":"INFJ", "score":84, "reason":"내향적 직관과 감정으로 깊은 이해를 나눌 수 있다.", "image":"images/INFP_INFJ.png"},
    ],
    "INFJ": [
        {"pair":"ENFP", "score":94, "reason":"직관과 감정의 균형으로 서로를 자극하고 지지한다.", "image":"images/INFJ_ENFP.png"},
        {"pair":"ENFJ", "score":90, "reason":"가치와 사명에 공감하며 안정적인 유대감을 형성한다.", "image":"images/INFJ_ENFJ.png"},
        {"pair":"INFP", "score":84, "reason":"내적 가치와 이상을 함께 공감하며 성장할 수 있다.", "image":"images/INFJ_INFP.png"},
    ],
    "ENFP": [
        {"pair":"INFJ", "score":94, "reason":"상호 보완적 직관과 감정으로 깊은 케미가 난다.", "image":"images/ENFP_INFJ.png"},
        {"pair":"INTJ", "score":83, "reason":"아이디어와 실행이 만나 좋은 시너지를 낼 수 있다.", "image":"images/ENFP_INTJ.png"},
        {"pair":"INFP", "score":88, "reason":"감정과 창의성에서 공감대를 형성한다.", "image":"images/ENFP_INFP.png"},
    ],
    "ENFJ": [
        {"pair":"INFP", "score":92, "reason":"타인의 성장을 돕는 성향이 잘 맞는다.", "image":"images/ENFJ_INFP.png"},
        {"pair":"INFJ", "score":90, "reason":"가치 지향적인 대화로 깊이 있는 유대를 만든다.", "image":"images/ENFJ_INFJ.png"},
        {"pair":"ISFP", "score":80, "reason":"감성적 안정감과 따뜻한 지지를 준다.", "image":"images/ENFJ_ISFP.png"},
    ],
    "INTJ": [
        {"pair":"ENFP", "score":83, "reason":"큰 그림과 아이디어를 실험하는 파트너가 된다.", "image":"images/INTJ_ENFP.png"},
        {"pair":"ENTP", "score":82, "reason":"논리적 도전과 창의적 토론에서 자극을 받는다.", "image":"images/INTJ_ENTP.png"},
        {"pair":"INTP", "score":78, "reason":"지적 공감대와 독립성을 존중한다.", "image":"images/INTJ_INTP.png"},
    ],
    "INTP": [
        {"pair":"ENTP", "score":88, "reason":"아이디어 토론에서 즐겁고 자극적인 관계다.", "image":"images/INTP_ENTP.png"},
        {"pair":"INFJ", "score":80, "reason":"감정을 보완해주는 파트너가 될 수 있다.", "image":"images/INTP_INFJ.png"},
        {"pair":"INTJ", "score":78, "reason":"논리적 대화와 목표 지향성이 공존한다.", "image":"images/INTP_INTJ.png"},
    ],
    "ENTP": [
        {"pair":"INTP", "score":88, "reason":"아이디어 경쟁과 협업에서 시너지를 낸다.", "image":"images/ENTP_INTP.png"},
        {"pair":"INFJ", "score":81, "reason":"아이디어를 현실로 연결하는 데 도움된다.", "image":"images/ENTP_INFJ.png"},
        {"pair":"ENTJ", "score":80, "reason":"목표 지향성과 추진력에서 합이 좋다.", "image":"images/ENTP_ENTJ.png"},
    ],
    "ENTJ": [
        {"pair":"INFP", "score":82, "reason":"비전과 실행에서 서로 자극을 주는 관계가 된다.", "image":"images/ENTJ_INFP.png"},
        {"pair":"INTP", "score":80, "reason":"전략적 사고와 아이디어 실행에서 보완된다.", "image":"images/ENTJ_INTP.png"},
        {"pair":"ENTP", "score":80, "reason":"도전적이고 역동적인 파트너십이 가능하다.", "image":"images/ENTJ_ENTP.png"},
    ],
    "ISFP": [
        {"pair":"ESFJ", "score":86, "reason":"실용적 배려와 감성적 안정이 잘 맞는다.", "image":"images/ISFP_ESFJ.png"},
        {"pair":"ENFJ", "score":80, "reason":"따뜻한 지지를 통해 안정감을 느낀다.", "image":"images/ISFP_ENFJ.png"},
        {"pair":"ISFJ", "score":78, "reason":"실생활에서 서로를 돌보는 관계가 된다.", "image":"images/ISFP_ISFJ.png"},
    ],
    "ISFJ": [
        {"pair":"ESFP", "score":85, "reason":"활기 있는 에너지가 안정감을 불러온다.", "image":"images/ISFJ_ESFP.png"},
        {"pair":"ISTP", "score":80, "reason":"실용성에서 서로를 보완한다.", "image":"images/ISFJ_ISTP.png"},
        {"pair":"ISFP", "score":78, "reason":"세심한 배려로 안정적인 관계가 가능하다.", "image":"images/ISFJ_ISFP.png"},
    ],
    "ESFP": [
        {"pair":"ISFJ", "score":85, "reason":"즐거움과 안정감의 균형이 좋다.", "image":"images/ESFP_ISFJ.png"},
        {"pair":"ESTJ", "score":80, "reason":"에너지와 조직력이 어우러져 잘 맞는다.", "image":"images/ESFP_ESTJ.png"},
        {"pair":"ENFP", "score":82, "reason":"공유하는 즐거움과 창의성이 잘 맞는다.", "image":"images/ESFP_ENFP.png"},
    ],
    "ESTJ": [
        {"pair":"ISFP", "score":80, "reason":"실무적 안정성과 따뜻함이 보완된다.", "image":"images/ESTJ_ISFP.png"},
        {"pair":"ESFP", "score":80, "reason":"실행력과 활기가 시너지를 낸다.", "image":"images/ESTJ_ESFP.png"},
        {"pair":"ISTJ", "score":86, "reason":"체계적이고 안정적인 파트너십을 이룬다.", "image":"images/ESTJ_ISTJ.png"},
    ],
    "ISTJ": [
        {"pair":"ESTJ", "score":86, "reason":"규범과 책임감에서 공감대가 높다.", "image":"images/ISTJ_ESTJ.png"},
        {"pair":"ISFJ", "score":84, "reason":"실용성과 세심함으로 안정적인 관계가 가능.", "image":"images/ISTJ_ISFJ.png"},
        {"pair":"ENTJ", "score":78, "reason":"목표 지향적 성향에서 상호 보완될 수 있다.", "image":"images/ISTJ_ENTJ.png"},
    ],
    "ISTP": [
        {"pair":"ESFJ", "score":80, "reason":"실용적 도움과 실천에서 균형을 이룬다.", "image":"images/ISTP_ESFJ.png"},
        {"pair":"ISFJ", "score":80, "reason":"현실적 문제 해결에서 조화가 난다.", "image":"images/ISTP_ISFJ.png"},
        {"pair":"INTP", "score":78, "reason":"논리적 호기심으로 함께 할 수 있다.", "image":"images/ISTP_INTP.png"},
    ],
    "ESFJ": [
        {"pair":"ISFP", "score":86, "reason":"보살핌과 감성적 교감이 잘 맞는다.", "image":"images/ESFJ_ISFP.png"},
        {"pair":"ISTP", "score":80, "reason":"실용성에서 서로 보완된다.", "image":"images/ESFJ_ISTP.png"},
        {"pair":"ENFJ", "score":84, "reason":"사람 중심의 가치관으로 공감대가 높다.", "image":"images/ESFJ_ENFJ.png"},
    ],
}

# --- 지원 함수 ---
IMG_DIR = Path("images")  # 이미지 폴더
def load_image_safe(path_or_url):
    try:
        if Path(path_or_url).exists():
            return Image.open(path_or_url)
        else:
            # URL 로드 (선택). PIL로 URL 바로 로드하려면 requests 필요. 여기서는 예외처리로 대체 이미지 사용.
            return Image.open("images/placeholder.png")
    except Exception:
        return None

# --- UI: 사이드바 ---
with st.sidebar:
    st.header("MBTI 궁합 찾기 💕")
    mbti_input = st.selectbox("너의 MBTI를 골라줘", sorted(list(compat.keys())))
    top_n = st.slider("몇 개의 궁합을 볼래?", 1, 5, 3)

# --- 메인: 결과 ---
st.markdown(f"<div class='mbti-title'>너의 MBTI: {mbti_input}</div>", unsafe_allow_html=True)
st.write("같이 잘 맞는 MBTI들을 아래에서 확인해봐! (이미지는 project/images 폴더에 넣어두면 자동으로 표시돼요.)")

results = compat.get(mbti_input, [])
results = results[:top_n]

cols = st.columns(len(results) if len(results)>0 else 1)
for i, item in enumerate(results):
    col = cols[i]
    with col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        # 이미지 로드(로컬 우선)
        img_obj = load_image_safe(item["image"])
        if img_obj:
            st.image(img_obj, use_column_width=True, caption=f"{mbti_input} ↔ {item['pair']}")
        else:
            # 이미지 없을 때: 간단한 대체 텍스트
            st.write("이미지가 없어요. '이미지 제작 도구'로 만들어서 images/ 폴더에 넣어줘 💌")
        st.markdown(f"<div class='mbti-title'>{item['pair']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>호환도: <strong>{item['score']}%</strong></div>", unsafe_allow_html=True)
        st.write(item["reason"])
        with st.expander("더 자세히 보기"):
            st.write(f"이 유형과의 관계에서 어떤 점이 강점인지, 조심할 점을 적어줘도 좋아!")
            # 예시 추가 텍스트
            st.write("- 강점: 서로의 차이를 보완하고 성장할 기회가 많다.")
            st.write("- 유의할 점: 소통 방식의 차이로 오해가 생길 수 있으니 대화 시간을 가지자.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 다운로드: CSV ---
if st.button("추천 결과 CSV로 받기"):
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)
    st.download_button("다운로드: CSV", csv, file_name=f"{mbti_input}_compat.csv", mime="text/csv")

# --- 푸터 안내 ---
st.markdown("---")
st.info("참고: 이미지를 직접 생성해야 하는 경우, '이미지 제작 도구'를 사용해 MBTI 쌍별 이미지를 만든 뒤 project/images/ 폴더에 넣어주세요. 예: images/INFP_ENFJ.png")
