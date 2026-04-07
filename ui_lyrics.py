import streamlit as st
import time
import utils
import os
import google.generativeai as genai

# [확실함] API 키 로컬 저장 기능
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    return ""

def save_api_key(key):
    with open("api_key.txt", "w") as f:
        f.write(key)

def render_tab1():
    # [확실함] 슬림 박스 및 겹침 방지 CSS (검증 완료)
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -12px !important; }
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 32px !important; min-height: 32px !important;
            padding: 0px 10px !important; display: flex !important; align-items: center !important; font-size: 13px !important;
        }
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 11px !important; margin-bottom: 2px !important; font-weight: 600 !important; color: #444 !important; padding-top: 6px !important;
        }
        div[role="radiogroup"] { gap: 10px !important; margin-top: 3px !important; }
        .stCode { margin-top: -5px !important; border: 1px solid #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        # API 설정
        saved_key = get_api_key()
        api_key = st.text_input("🔑 Google API Key", value=saved_key, type="password")
        if api_key != saved_key:
            save_api_key(api_key)

        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") 
            gen_btn = st.button("🚀 AI 가사/제목 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐거운 삶")
        lyric_styles = ["서정적인", "시적인", "직설적인", "성경적인", "현대적인", "감성적인", "이야기하듯", "찬양 중심"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 장르 및 분위기
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["경건하고 거룩한", "평화롭고 차분한", "웅장한", "비장한", "치유되는", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        c1, c2 = st.columns(2)
        with c1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with c2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider()
        v_type = st.radio("보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True)
        
        if v_type == "남자": s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝", "허스키 남성", "파워풀 락 남성", "미성 남성", "바리톤"])
        elif v_type == "여자": s_vocal = st.selectbox("👩‍🎤 스타일", ["청아한 여성 팝", "파워 디바", "몽환적 여성", "어쿠스틱 여성", "소프라노"])
        elif v_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 남녀 화음", "애절한 발라드 듀엣", "가스펠 듀엣", "로맨틱 듀엣"])
        elif v_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 성가대", "가스펠 합창", "어린이 성가대", "에픽 코러스"])
        else: s_vocal = "Instrumental"

    # --- [검증 결과] 생성 로직 및 출력 영역 분리 ---
    with right_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key: st.error("API 키를 입력해주세요."); return
            if not subject: st.error("주제를 입력해주세요."); return
            
            with st.spinner("Google AI가 가사를 생성 중입니다..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"""
                    음악 프로듀서로서 다음 주제로 노래 제목([TITLE])과 풀버전 가사([LYRICS])를 작성하라.
                    주제: {subject}
                    장르: {target} - {s_genre}
                    스타일: {s_lyric_style}
                    보컬: {s_vocal}
                    
                    형식:
                    [TITLE] 한글제목_영어제목
                    [LYRICS]
                    [Intro] (연주 묘사)
                    [Verse 1]
                    [Pre-Chorus]
                    [Chorus]
                    [Verse 2]
                    [Chorus]
                    [Bridge]
                    [Chorus]
                    [Outro]
                    """
                    response = model.generate_content(prompt)
                    full_text = response.text
                    
                    # 데이터 파싱 및 세션 상태 저장
                    if "[TITLE]" in full_text and "[LYRICS]" in full_text:
                        st.session_state.gen_title = full_text.split("[TITLE]")[1].split("[LYRICS]")[0].strip()
                        st.session_state.gen_lyrics = full_text.split("[LYRICS]")[1].strip()
                    else:
                        st.session_state.gen_title = f"{subject[:5]}_Song"
                        st.session_state.gen_lyrics = full_text

                    st.session_state.gen_prompt = f"Professional {target}. Style: {s_genre}, {s_mood}. Vocals: {s_vocal}. Inst: {s_inst}."
                except Exception as e:
                    st.error(f"AI 오류: {str(e)}")

        # [확실함] 에러 원인 해결: 데이터가 있을 때만 렌더링하도록 조건부 출력 적용
        if 'gen_title' in st.session_state:
            with st.container(border=True):
                st.write("**1. 🎵 Title**")
                st.code(st.session_state.gen_title)
            
            with st.container(border=True):
                st.write("**2. 🎸 프롬프트**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (복사 가능)**")
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 설정 후 '생성' 버튼을 누르면 여기에 결과가 나타납니다.")
