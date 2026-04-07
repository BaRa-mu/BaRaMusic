import streamlit as st
import time
import utils
import os
import google.generativeai as genai

# [확실함] API 키 로드 및 저장 함수
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    return ""

def save_api_key(key):
    with open("api_key.txt", "w") as f:
        f.write(key)

def render_tab1():
    # --- [검증완료] 슬림 박스 및 겹침 방지 레이아웃 CSS ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -12px !important; }
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 32px !important; min-height: 32px !important;
            padding: 0px 10px !important; display: flex !important; align-items: center !important; font-size: 13px !important;
        }
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 12px !important; margin-bottom: 2px !important; font-weight: 600 !important; color: #444 !important; padding-top: 6px !important;
        }
        div[role="radiogroup"] { gap: 12px !important; margin-top: 4px !important; }
        .stCode { margin-top: -5px !important; border: 1px solid #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        saved_key = get_api_key()
        api_key = st.text_input("🔑 Google API Key", value=saved_key, type="password")
        if api_key != saved_key: save_api_key(api_key)

        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") 
            gen_btn = st.button("🚀 초강력 AI 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        lyric_styles = ["서정적인", "시적인", "직설적인", "성경적인", "현대적인", "감성적인", "이야기하듯", "찬양 중심"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
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

    # --- [검증 완료] 생성 및 출력 로직 ---
    with right_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key: st.error("API 키를 확인해주세요."); return
            if not subject: st.error("주제를 입력해주세요."); return
            
            with st.spinner("최신 Gemini 3.1 Pro 모델이 대곡을 구성 중입니다..."):
                try:
                    genai.configure(api_key=api_key)
                    # [확실함] 지원 목록 중 최상위 지능 모델 적용
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # [초강력] 프롬프트 설계: 작사가 페르소나 및 구조화 지시
                    prompt = f"""
                    역할: 빌보드급 작사가 및 음악 프로듀서
                    작업: 다음 주제를 바탕으로 '인간이 쓴 것 같은' 깊이 있는 가사와 제목 생성
                    
                    입력 주제: {subject}
                    음악 환경: {target} / {s_genre} / {s_mood} / {s_inst}
                    가사 문체: {s_lyric_style}
                    보컬 스타일: {s_vocal}
                    
                    요구사항:
                    1. [TITLE]: 주제를 관통하는 상징적인 '한글제목_영어제목'을 1개 작성하라.
                    2. [PROMPT]: Suno AI 입력용 스타일 프롬프트를 800자 내외의 영어로 작성하라. (중복 문구 금지, 전문 오디오 용어 포함)
                    3. [LYRICS]: 3분 이상의 재생 시간을 보장하는 정밀한 곡 구조로 작성하라.
                       - [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Chorus], [Bridge], [Guitar/Inst Solo], [Chorus], [Outro] 단계 준수.
                       - 각 Verse는 최소 6행 이상의 긴 서사를 가질 것.
                       - {subject}의 내용을 가사 맥락에 녹여 자연스럽게 고백하도록 할 것.
                    """
                    
                    response = model.generate_content(prompt)
                    full_text = response.text
                    
                    # 파싱 로직 (에러 방지용)
                    try:
                        st.session_state.gen_title = full_text.split("[TITLE]")[1].split("[PROMPT]")[0].strip()
                        st.session_state.gen_prompt = full_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip()
                        st.session_state.gen_lyrics = full_text.split("[LYRICS]")[1].strip()
                    except:
                        st.session_state.gen_title = f"{subject[:5]}_Song"
                        st.session_state.gen_prompt = f"{s_genre}, {s_mood}, {s_vocal}, {s_inst}"
                        st.session_state.gen_lyrics = full_text

                except Exception as e:
                    st.error(f"AI 호출 오류: {str(e)}")

        # 세션 데이터 존재 시에만 렌더링
        if 'gen_title' in st.session_state:
            with st.container(border=True):
                st.write("**1. 🎵 Title**")
                st.code(st.session_state.gen_title)
            with st.container(border=True):
                st.write("**2. 🎸 Style of Music (프롬프트)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (풀버전 / 복사 가능)**")
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
