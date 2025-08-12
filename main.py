# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MBTI 진로 추천기", layout="wide")

# 샘플 데이터 (실제로는 CSV/DB에서 불러오기)
careers = [
    {"id":1, "title":"심리 상담사", "mbti":["INFP","INFJ"], "skills":"공감, 경청, 심리학 지식", "desc":"사람의 마음을 돌보는 직업"},
    {"id":2, "title":"그래픽 디자이너", "mbti":["INFP","ISFP"], "skills":"디자인 툴, 창의력", "desc":"시각적 메시지 제작"},
    {"id":3, "title":"프로젝트 매니저", "mbti":["ESTJ","ENTJ"], "skills":"리더십, 일정관리", "desc":"팀을 이끌고 프로젝트 완수"}
]
df = pd.DataFrame(careers)

st.title("✨ MBTI 기반 진로 추천기")
st.write("MBTI를 선택하면 어울리는 직업을 추천해줘요. 관심 분야나 스킬을 추가하면 더 맞춤 추천이 가능해요.")

# 사이드바: 선택/필터
with st.sidebar:
    mbti = st.selectbox("너의 MBTI를 선택해줘", ["INFP","INFJ","ISFP","ESTJ","ENTJ"])
    interest = st.text_input("관심 분야(선택): 예) 디자인, IT, 교육")
    st.button("추천 받기")

# 추천 로직(간단 매핑)
def recommend(selected_mbti, interest_text=""):
    candidates = df[df['mbti'].apply(lambda x: selected_mbti in x)]
    # 관심 키워드가 있으면 우선순위 조정
    if interest_text:
        candidates['score'] = candidates['title'].apply(lambda t: interest_text.lower() in t.lower()).astype(int)
        candidates = candidates.sort_values(by='score', ascending=False)
    return candidates

results = recommend(mbti, interest)

# 결과 출력
cols = st.columns(3)
for i, row in results.iterrows():
    col = cols[i % 3]
    with col:
        st.markdown(f"### {row['title']}")
        st.write(row['desc'])
        st.write("필요 스킬:", row['skills'])
        if st.button(f"자세히 보기 - {row['title']}", key=row['id']):
            st.write("상세 정보: 예시 설명과 진로 팁을 여기에 넣어줘")

# 저장/다운로드 예시
if st.button("추천 결과 다운로드"):
    st.download_button("CSV로 저장", data=results.to_csv(index=False), file_name="recommendations.csv")
