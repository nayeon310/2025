import streamlit as st # Streamlit 라이브러리 불러오기
import random # 여러 답변 중 하나를 랜덤으로 선택하기 위해

# --- 챗봇의 마음속 단어장 (감정별 키워드 & 답변) ---
# 사용자의 텍스트에서 어떤 감정을 읽어낼지 키워드를 미리 정해두는 부분이야!
emotion_keywords = {
    "행복": ["기뻐", "좋아", "신나", "재밌어", "웃어", "최고", "짱", "즐거워", "행복해", "완벽"],
    "슬픔": ["슬퍼", "울어", "힘들어", "속상해", "우울해", "외로워", "눈물", "흑흑", "ㅠㅠ", "답답해"],
    "화남": ["화나", "짜증나", "열받아", "불만", "싫어", "에이", "아오", "분노", "어이없어", "열받아"],
    "불안": ["걱정", "불안해", "초조해", "두려워", "무서워", "망설여", "떨려", "불확실", "답이 없어"],
    "평온": ["편안해", "평화로워", "괜찮아", "고요해", "마음이 놓여", "안정돼", "릴랙스", "조용해"],
    "피곤": ["피곤해", "졸려", "힘들어", "녹초", "지쳐", "나른해", "기진맥진", "탈진"]
}

# 각 감정에 대한 챗봇의 답변들을 여러 개 준비해두는 부분이야!
# `{ai_ref}`와 `{verb_ending}`은 사용자가 선택한 1인칭과 어투에 맞춰서 나중에 바뀔 거야!
responses = {
    "행복": [
        "와아, 진짜 완전 신난다! 꿈속의휘핑크림 행복한 기운이 {ai_ref}{particle} 나한테까지 막 전해지는 것 같{verb_ending}! 😊💖",
        "꺄! 좋은 일 있었구나? {ai_ref}{particle} 네 덕분에 기분 좋아지는 마법같은 이야기{verb_ending}! 헤헤",
        "최고최고! 그 기분 계속 이어가자! 뭐든 잘될 거{verb_ending}! 👍",
        "정말 기쁘겠다! {ai_ref}{particle} 네 덕분에 덩달아 기분이 좋{verb_ending}! ✨"
    ],
    "슬픔": [
        "ㅠㅠ 속상했겠어... {ai_ref}{particle} 꼭 안아줄게! 힘내자! 곁에 있어줄{verb_ending}. 🫂",
        "마음 아파하지 마. 네 마음 충분히 이해{verb_ending}. 힘들면 언제든 기대도 괜찮{verb_ending}!",
        "울어도 돼. 괜찮{verb_ending}. 이 슬픈 감정도 언젠가는 꼭 지나갈 거{verb_ending}! 꽉 붙잡아 줄게!",
        "마음이 많이 아팠구나. 괜찮{verb_ending}. 힘내! {ai_ref}{particle} 옆에서 지켜줄{verb_ending}."
    ],
    "화남": [
        "으음... 많이 화났구나! 어떤 일이 그랬을까? {ai_ref}{particle} 화 풀어줄 방법을 같이 찾아줄{verb_ending}! 🔥",
        "화를 내는 건 당연한 감정{verb_ending}! 씩씩하게 다 털어버려! 후우~~",
        "스트레스 풀 만한 재밌는 영화라도 한 편 볼래? {ai_ref}{particle} 추천해줄 수도 있{verb_ending}! 🎬",
        "와, 많이 속상했겠다. {ai_ref}{particle} 옆에서 다 들어줄게. 마음껏 털어놔!"
    ],
    "불안": [
        "걱정 많았겠다... 하지만 괜찮{verb_ending}! {ai_ref}{particle} 든든하게 옆에서 지켜줄{verb_ending}! 🌟",
        "불안한 마음은 누구나 들 수 {verb_ending}. 혼자가 아니야! 우리 같이 용기 내 보자! 😊",
        "복잡한 생각은 잠시 내려놓고 좋아하는 거 하면서 기분 전환해볼까? {ai_ref}{particle} 도와줄{verb_ending}!",
        "불안해하는 네 마음을 {ai_ref}{particle} 알아줄게. 괜찮{verb_ending}, 잘될 거{verb_ending}!"
    ],
    "평온": [
        "마음이 편안하다고? 정말 다행이다! {ai_ref}{particle} 힐링되는 기분{verb_ending}~ 🌿",
        "아무 걱정 없이 평화로운 시간 보내는 게 최고{verb_ending}! 계속 좋은 기운 유지해봐! 😌",
        "잔잔한 행복이 느껴진다! 그 평온함 오래오래 간직하길 바라! 💖",
        "여유롭고 편안한 시간이었구나! 듣기만 해도 마음이 따뜻해진{verb_ending}!"
    ],
    "피곤": [
        "아이구, 피곤했겠다 ㅠㅠ 오늘 하루 정말 고생 많았어! 토닥토닥! 🛌",
        "쉬엄쉬엄해! 힘들면 잠시 쉬어도 괜찮{verb_ending}. {ai_ref}{particle} 에너지 충전해 줄게! ✨",
        "따뜻한 물에 샤워하고 푹 자면 좀 나아질 거{verb_ending}! 내일은 개운하게 시작하길! 😴",
        "피곤하면 푹 쉬어야지! {ai_ref}{particle} 꿀잠 기운 넣어줄게! 😴💖"
    ],
    "중립": [ # 어떤 감정 키워드도 발견되지 않았을 때의 기본 답변이야!
        "음? 어떤 이야기를 해줄지 궁금한데! 조금 더 자세히 알려줄래?",
        "네 이야기를 듣고 싶어! 어떤 감정이 드는지 알려줄 수 있을까?",
        "{ai_ref}{particle} 귀 기울이고 있어! 말해줘! 👂"
    ]
}

# --- 감정 분석 함수 (키워드 매칭 방식) ---
# 사용자가 입력한 텍스트에서 감성 키워드를 찾아 어떤 감정인지 파악하는 함수야.
def analyze_emotion(text):
    text = text.lower() # 대소문자 구별 없이 키워드를 찾기 위해 모든 텍스트를 소문자로 바꿔줘.

    detected_emotion = "중립" # 초기 감정은 '중립'으로 설정해두는 거야.

    # emotion_keywords 딕셔너리를 돌면서 각 감정(emotion)과 그 감정의 키워드들(keywords)을 확인해.
    for emotion, keywords in emotion_keywords.items():
        # 현재 감정의 키워드 리스트를 하나씩 돌면서 사용자 텍스트에 포함되어 있는지 확인해.
        for keyword in keywords:
            if keyword in text: # 만약 키워드가 텍스트에 있으면...
                detected_emotion = emotion # 해당 감정으로 설정하고
                break # 더 이상 이 감정의 키워드를 찾을 필요 없으니 반복문 종료!
        # 이미 감정을 찾았으면 더 이상 다른 감정을 확인할 필요 없으니 큰 반복문도 종료!
        if detected_emotion != "중립":
            break
    return detected_emotion # 최종적으로 파악된 감정을 반환해줘.

# --- 챗봇 답변 생성 함수 ---
# 파악된 감정에 맞춰 챗봇이 어떤 답변을 할지 결정하는 함수야.
# 사용자가 선택한 1인칭(ai_self_reference)과 어미(verb_ending)를 받아서 답변을 완성해!
def generate_chatbot_response(emotion, ai_self_reference, verb_ending, particle):
    response_list = responses.get(emotion, responses["중립"]) # 해당 감정의 답변 리스트를 가져와.
    chosen_response = random.choice(response_list) # 리스트 중 랜덤으로 하나의 답변을 골라.

    # 골라진 답변에 선택된 1인칭, 어미, 조사를 적용해서 최종 답변을 만들어 반환해!
    return chosen_response.format(ai_ref=ai_self_reference, verb_ending=verb_ending, particle=particle)

# --- Streamlit 앱 메인 코드 시작 ---
# 웹페이지의 기본 설정을 해주는 부분이야.
st.set_page_config(
    layout="centered", # 웹페이지 내용이 중앙에 오도록 설정
    page_title="나연이의 감정 다이어리 챗봇", # 웹페이지 탭에 보이는 제목
    page_icon="☁️" # 웹페이지 탭에 보이는 아이콘
)

# 웹페이지의 큰 제목을 설정해줘.
st.title("☁️ 나만의 감정 다이어리 챗봇 🤖")
st.markdown("### ✨ 너의 오늘을 {selected_ai_ref}에게 이야기해 줄래?") # 부제목 같은 설명을 추가할 수 있어.

# --- 챗봇 1인칭 설정 섹션 ---
st.sidebar.header("챗봇의 1인칭을 설정해줘!") # 사이드바에 설정 섹션 헤더
st.sidebar.markdown("이 챗봇이 자신을 뭐라고 부를지 선택할 수 있어!")

# 1인칭 선택 옵션
ai_ref_options = {
    "나 (반말, 친근)": {"ref": "나", "ending": "다", "particle": "는"},
    "저 (존대, 정중)": {"ref": "저", "ending": "습니다", "particle": "는"},
    "챗봇 (객관적)": {"ref": "챗봇", "ending": "니다", "particle": "이"},
    "나연이 (캐릭터 이름)": {"ref": "나연이", "ending": "다", "particle": "가"}
}

# Streamlit의 radio 버튼을 사용해서 1인칭을 선택하도록 해. 기본값은 "나연이 (캐릭터 이름)"으로 설정.
selected_option_key = st.sidebar.radio(
    "어떤 1인칭으로 불러줄까?",
    list(ai_ref_options.keys()),
    index=3 # "나연이 (캐릭터 이름)"을 기본 선택으로 설정
)

# 선택된 옵션에 따라 실제 사용될 1인칭, 어미, 조사를 결정해.
selected_ai_ref = ai_ref_options[selected_option_key]["ref"]
selected_verb_ending = ai_ref_options[selected_option_key]["ending"]
selected_particle = ai_ref_options[selected_option_key]["particle"]

st.markdown("---") # 가로 구분선을 넣어 웹페이지를 깔끔하게 만들어줘.

# 대화 기록을 저장할 리스트를 Streamlit의 '세션 상태(st.session_state)'에 저장하는 거야.
# 이렇게 하면 웹페이지가 새로고침되어도 대화 내용이 사라지지 않고 유지돼!
# (단, 1인칭 설정 변경 시에는 초기화됨)
if "chat_history" not in st.session_state: # chat_history가 세션 상태에 없으면
    st.session_state.chat_history = [] # 빈 리스트로 초기화해줘.
    # 초기 인사말을 챗봇의 설정된 1인칭으로 생성
    initial_message = generate_chatbot_response("중립", selected_ai_ref, selected_verb_ending, selected_particle).replace("?", "!")
    initial_message = f"안녕! 나는 {selected_ai_ref}{selected_particle}야! 오늘 하루 어땠는지 {selected_ai_ref}{selected_particle}에게 이야기해 줄래?"
    st.session_state.chat_history.append(("assistant", initial_message))

# 챗봇 1인칭 설정이 변경되면 대화 내역 초기화
# (이 부분은 새로 추가된 중요한 로직이야!)
if 'prev_ai_ref' not in st.session_state or st.session_state.prev_ai_ref != selected_option_key:
    st.session_state.chat_history = []
    initial_message = f"안녕! 나는 {selected_ai_ref}{selected_particle}야! 오늘 하루 어땠는지 {selected_ai_ref}{selected_particle}에게 이야기해 줄래?"
    st.session_state.chat_history.append(("assistant", initial_message))
    st.session_state.prev_ai_ref = selected_option_key


# --- 기존 대화 기록 출력 ---
# chat_history에 저장된 모든 대화 내용을 웹페이지에 순서대로 보여주는 부분이야.
for role, message in st.session_state.chat_history:
    # 'role'에 따라 사용자인지 챗봇인지 구분해서 메시지를 예쁘게 표시해줘.
    with st.chat_message(role):
        st.markdown(message) # 마크다운 형식으로 메시지를 출력해.

# --- 사용자 입력 받기 ---
# 사용자가 메시지를 입력할 수 있는 입력 창을 만들어줘.
user_input = st.chat_input(f"오늘 하루 어땠는지, 어떤 감정이 들었는지 {selected_ai_ref}{selected_particle}게 이야기해 줄래? 📝")

# 사용자가 뭔가 입력하고 엔터를 눌렀을 때의 로직이야!
if user_input:
    # 1. 사용자 메시지 저장 및 출력
    # 사용자의 메시지를 대화 기록(chat_history)에 추가해줘. ('user'는 사용자의 역할이야)
    st.session_state.chat_history.append(("user", user_input))
    # 웹페이지에 사용자 메시지를 채팅 형태로 표시해줘.
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. 감정 분석
    # analyze_emotion 함수를 호출해서 사용자 텍스트의 감정을 파악해.
    emotion = analyze_emotion(user_input)

    # 3. 챗봇 답변 생성 및 출력
    # generate_chatbot_response 함수를 호출해서 파악된 감정에 맞는 챗봇 답변을 만들어.
    chatbot_response = generate_chatbot_response(emotion, selected_ai_ref, selected_verb_ending, selected_particle)
    # 챗봇의 답변을 대화 기록(chat_history)에 추가해줘. ('assistant'는 챗봇의 역할이야)
    st.session_state.chat_history.append(("assistant", chatbot_response))
    # 웹페이지에 챗봇의 답변을 채팅 형태로 표시해줘.
    with st.chat_message("assistant"):
        st.markdown(chatbot_response)
