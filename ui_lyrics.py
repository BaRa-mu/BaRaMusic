import streamlit as st
import time
import os
import google.generativeai as genai
import utils

# [확실함] 보컬 데이터 70종 완벽 보존
VOCAL_DATA = {
    "남자": ["감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"],
    "여자": ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련된 재즈 보컬", "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"],
    "듀엣": ["아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", "그루비한 R&B 소울 듀엣", "남성 2인조 화음 보컬", "여성 2인조 팝 화음 보컬", "에너제틱한 락 보컬 남녀 듀엣", "인디 감성의 나른한 남녀 듀엣", "오페라/크로스오버 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "서로 주고받는 대화형 뮤지컬 듀엣", "잔잔하고 위로가 되는 포크 듀엣", "재지한 피아노 바 감성의 듀엣", "어두운 분위기의 시네마틱 듀엣", "소년 소녀 느낌의 풋풋한 듀엣", "메인 남성 보컬 & 여성 코러스 화음", "메인 여성 보컬 & 남성 코러스 화음", "신비로운 앰비언트 보컬 듀엣", "폭발적인 가창력 대결 스타일 듀엣"],
    "합창": ["웅장하고 홀리한 대규모 성가대", "파워풀하고 리드미컬한 흑인 가스펠 합창", "맑고 순수한 어린이 성가대", "신비로운 중세 그레고리안 성가", "장엄하고 시네마틱한 에픽 코러스", "따뜻하고 대중적인 교회 성가대", "천상의 소리 같은 앰비언트 코러스", "강렬하고 비장한 오페라 합창", "경쾌하고 희망찬 청년 연합 찬양대", "속삭이는 듯한 몽환적인 백그라운드 합창"]
}

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab1():
    # [확실함] 겹침 해결 및 가시성 확보 CSS
    st.markdown("""
        <style>
        /* 음수 마진 제거하여 겹침 방지 */
        [data-testid="stVerticalBlock"] > div { margin-top: 5px !important; margin-bottom: 8px !important; }
        
        /* 슬림한 박스 디자인 (32px) 유지 */
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 32px !important; min-height: 32px !important;
            padding: 0px 10px !important; display: flex !important; align-items: center !important; font-size: 13px !important;
        }
        
        /* 라벨 가독성 확보 */
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 12px !important; font-weight: 600 !important; color: #333 !important;
            margin-bottom: 4px !important; padding-top: 5px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        # API 설정
        api_key = st.text_input("🔑 API Key", value=get_api_key(), type="password")
        if api_key:
            with open("api_key.txt", "w") as f: f.write(api_key)

        # 제목과 버튼 겹침 차단 배치
        h_col, b_col = st.columns([0.8, 1.2])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: gen_btn = st.button("🚀 초강력 AI 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 새벽녘 부활하신 주님")
        s_lyric_style = st.selectbox("✒️ 가사 스타일", ["서정적인", "시적인", "직설적인", "성경적인", "현대적인", "감성적인", "이야기하듯", "찬양 중심"])
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 장르 및 분위기
        s_genre = st.selectbox("🎧 장르", utils.suno_pop_list if target=="대중음악" else utils.suno_ccm_list)
        s_mood = st.selectbox("✨ 분위기", ["선택안함", "감성적인", "기쁘고 희망찬", "평화롭고 차분한", "웅장한", "비장한"])

        c1, c2 = st.columns(2)
        with c1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with c2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider()
        v_type = st.radio("🎤 보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True)
        s_vocal = st.selectbox(f"👨‍🎤 {v_type} 스타일", VOCAL_DATA[v_type]) if v_type != "경음악" else "Instrumental"

    with right_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key or not subject: st.error("키와 주제를 확인하세요."); return
            with st.spinner("한국어 가사와 고밀도 프롬프트를 생성 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # [확실함] 한국어 가사 강제 및 제목/프롬프트 최적화 명령
                    prompt = f"""
                    Role: Professional Songwriter & Music Producer.
                    Task: Generate [TITLE], [PROMPT], and [LYRICS].
                    
                    Instructions:
                    1. [TITLE]: Create a title as 'KoreanTitle_EnglishTitle'.
                    2. [PROMPT]: Provide a Suno AI style prompt in English, at least 900 characters long. Include detailed audio engineering terms (wide stereo, high-fidelity, pristine mixing, spatial depth). NO BOLDING (**).
                    3. [LYRICS]: Write a 3-8 minute full-length song structure. 
                    4. IMPORTANT: ALL [LYRICS] MUST BE WRITTEN IN KOREAN ONLY. NO ENGLISH IN LYRICS.
                    
                    Input Context:
                    Subject: {subject} / Genre: {target}-{s_genre} / Style: {s_lyric_style} / Mood: {s_mood} / Vocal: {s_vocal} / Inst: {s_inst}
                    """
                    
                    res_raw = model.generate_content(prompt).text.replace("**", "")
                    
                    # 파싱
                    st.session_state.gen_title = res_raw.split("[TITLE]")[1].split("[PROMPT]")[0].strip()
                    st.session_state.gen_prompt = res_raw.split("[PROMPT]")[1].split("[LYRICS]")[0].strip()
                    st.session_state.gen_lyrics = res_raw.split("[LYRICS]")[1].strip()

                except Exception as e: st.error(f"오류: {str(e)}")

        if 'gen_title' in st.session_state:
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(st.session_state.gen_title)
            with st.container(border=True):
                st.write(f"**2. 🎸 Style Prompt ({len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (한국어 풀버전)**")
                st.code(st.session_state.gen_lyrics, language="markdown")
