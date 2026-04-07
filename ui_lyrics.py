import streamlit as st
import time
import utils
import os
import google.generativeai as genai

# [확실함] API 키 로컬 저장 및 로드 기능
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    return ""

def save_api_key(key):
    with open("api_key.txt", "w") as f:
        f.write(key)

def render_tab1():
    # --- UI 최적화 CSS (슬림 박스 및 겹침 방지) ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -12px !important; }
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 32px !important; min-height: 32px !important;
            padding: 0px 10px !important; display: flex !important; align-items: center !important; font-size: 13px !important;
        }
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 11px !important; margin-bottom: 2px !important; font-weight: 600 !important; color: #444 !important; padding-top: 5px !important;
        }
        div[role="radiogroup"] { gap: 10px !important; margin-top: 3px !important; }
        .stCode { margin-top: -5px !important; border: 1px solid #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        # [확실함] 상단 API 설정 영역 (컴팩트 디자인)
        saved_key = get_api_key()
        api_key = st.text_input("🔑 Google API Key", value=saved_key, type="password", placeholder="AI 키를 입력하세요")
        if api_key != saved_key:
            save_api_key(api_key)
            st.success("API 키 저장됨")

        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") 
            gen_btn = st.button("🚀 AI 가사/제목 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐거운 삶")
        lyric_styles = ["서정적인", "시적인", "직설적인", "성경적인", "현대적인", "감성적인", "이야기하듯", "찬양 중심"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "비장한", "치유되는"]
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

    with right_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not api_key: st.error("API 키를 입력해주세요."); return
            if not subject: st.error("주제를 입력해주세요."); return
            
            with st.spinner("Google AI가 자연스러운 가사와 제목을 생성 중..."):
                try:
                    # [확실함] Google Generative AI 연동
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    # 제목 및 가사 생성을 위한 통합 프롬프트 (3분 이상 분량 강제)
                    prompt = f"""
                    음악 프로듀서로서 다음 조건에 맞는 노래 제목과 풀버전 가사를 작성하라.
                    주제: {subject}
                    장르: {target} - {s_genre}
                    스타일: {s_lyric_style}
                    분위기: {s_mood}
                    악기: {s_inst}
                    보컬: {s_vocal}
                    
                    출력 형식:
                    [TITLE] 한글제목_영어제목
                    [LYRICS]
                    [Intro] (악기 연주 묘사)
                    [Verse 1] (최소 6행)
                    [Pre-Chorus]
                    [Chorus] (후렴구)
                    [Verse 2] (최소 6행)
                    [Chorus]
                    [Bridge] (고조되는 부분)
                    [Interlude] (간주 묘사)
                    [Chorus]
                    [Outro] (여운이 남는 마무리)
                    """
                    
                    response = model.generate_content(prompt)
                    full_text = response.text
                    
                    # 제목과 가사 분리 로직
                    if "[TITLE]" in full_text and "[LYRICS]" in full_text:
                        st.session_state.gen_title = full_text.split("[TITLE]")[1].split("[LYRICS]")[0].strip()
                        st.session_state.gen_lyrics = full_text.split("[LYRICS]")[1].strip()
                    else:
                        st.session_state.gen_title = f"{subject[:5]}_Song"
                        st.session_state.gen_lyrics = full_text

                    st.session_state.gen_prompt = f"Professional {target}. Style: {s_genre}, {s_mood}. Tempo: {s_tempo}. Vocals: {s_vocal}. Main Inst: {s_inst}."
                    
                except Exception as e:
                    st.error(f"AI 연동 오류: {str(e)}")

        if st.session_state.get('gen_lyrics'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (AI 자동 생성)**")
                st.code(st.session_state.gen_title)
            with st.container(border=True):
                st.write("**2. 🎸 Style of Music (프롬프트)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (풀버전 / 복사 가능)**")
                st.code(st.session_state.gen_lyrics, language="markdown")
