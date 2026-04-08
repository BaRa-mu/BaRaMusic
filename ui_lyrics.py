import streamlit as st

# --- [1. 데이터 사전: 절대 보존] ---
MOODS = {
    "CCM": ["경배와 찬양", "깊은 묵상", "회개와 눈물", "헌신과 소명", "십자가의 은혜", "평안과 위로", "성령의 임재", "동행의 기쁨", "감사와 축복", "어린이의 마음", "새벽의 기도", "광야의 외침", "소망의 노래", "영광의 보좌", "치유의 광선"],
    "대중음악": ["애절한 이별", "설레는 첫사랑", "도시의 쓸쓸함", "청춘의 방황", "레트로 감성", "몽환적인 밤", "열정적인 도전", "따뜻한 힐링", "냉소적인 풍자", "일상의 소소함", "기억의 습작", "여행의 설렘", "비 오는 날", "아침의 싱그러움", "어른의 성장"]
}

GENRES = ["발라드", "소프트 록", "어쿠스틱 포크", "모던 재즈", "블루스", "보사노바", "가스펠 워십", "클래식 소품곡", "뉴에이지", "컨트리", "스윙 재즈", "소울", "시티팝", "펑크(Funk)", "라틴 팝", "아이리시 포크", "블루그래스", "챔버 팝", "프렌치 샹송", "탱고"]

VOCALS = {
    "남성": ["미성 하이톤", "허스키 소울", "중저음 베이스", "록 보컬", "부드러운 테너", "거친 라스피", "담백한 포크톤", "팝 스타일", "뮤지컬 발성", "호소력 짙은", "맑은 가성위주", "클래식 바리톤", "어반 스타일", "따뜻한 음색", "파워풀 벨팅", "공기 반 소리 반", "깊은 울림", "섬세한 바이브레이션", "소년미 보이스", "중후한 신사톤"],
    "여성": ["청아한 소프라노", "매혹적인 알토", "허스키 재즈톤", "소울풀 디바", "속삭이는 듯한", "파워풀 록커", "아이돌 팝스타일", "민요풍 음색", "클래식 메조", "청량한 하이톤", "몽환적인 보이스", "따뜻한 엄마품", "세련된 어반", "애절한 발라더", "귀여운 소녀톤", "브리티시 팝톤", "가녀린 가성", "그루비한 R&B", "깊은 감성의 솔로", "단단한 중음"],
    "듀엣": ["남녀 혼성 화음", "남성 듀오(강/약)", "여성 듀오(화려)", "언플러그드 스타일", "동성간의 경쟁", "속삭이는 연인", "웅장한 합창단", "아카펠라 그룹", "어쿠스틱 밴드", "소박한 연인", "강렬한 대비", "부드러운 조화", "부자간의 대화", "친구와의 수다", "슬픈 이별의 대화", "뮤지컬 넘버풍", "영혼의 단짝", "서로 다른 색깔", "완벽한 유니즌", "메아리 스타일"]
}

INSTRUMENTS = ["그랜드 피아노", "어쿠스틱 기타", "일렉 기타", "첼로", "바이올린", "하프", "플룻", "파이프 오르간", "우쿨렐레", "색소폰"]

# --- [2. AI 세션 설정 로직] ---
SESSION_MAP = {
    "그랜드 피아노": "바이올린 섹션, 부드러운 패드, 콘트라베이스",
    "어쿠스틱 기타": "카혼, 젬베, 쉐이커, 가벼운 베이스",
    "일렉 기타": "드럼 세트, 락 베이스, 신디사이저",
    "첼로": "피아노 반주, 비올라, 소프라노 스트링",
    "바이올린": "하프 오케스트레이션, 팀파니, 첼로",
    "하프": "플룻, 윈드 차임, 앰비언트 패드",
    "플룻": "어쿠스틱 기타, 가벼운 퍼커션",
    "파이프 오르간": "브라스 섹션, 콰이어(합창), 오케스트라 드럼",
    "우쿨렐레": "쉐이커, 우드블록, 가벼운 어쿠스틱 베이스",
    "색소폰": "재즈 드럼, 업라이트 베이스, 일렉 피아노"
}

def render_tab1():
    # [확실함] 글씨 잘림 방지 CSS
    st.sidebar.markdown("""
        <style>
        [data-testid="stSidebar"] div[data-baseweb="select"] > div, 
        [data-testid="stSidebar"] .stTextInput input {
            height: 38px !important; font-size: 14px !important;
        }
        [data-testid="stSidebar"] .stSelectbox label, 
        [data-testid="stSidebar"] .stRadio label {
            font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🎵 음악 생성 파라미터")
        
        # 1. 주제 및 타깃
        subject = st.text_input("💡 곡 주제", placeholder="예: 하나님의 사랑, 노을 지는 강변", key="l_subject")
        target = st.radio("🎯 타깃 설정", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        
        # 2. 가사 분위기 (15개 이상)
        lyric_mood = st.selectbox(f"✨ {target} 가사 분위기", MOODS[target], key="mood_sel")
        
        # 3. 음악 장르 (20개 이상)
        genre = st.selectbox("🎸 음악 장르 (20종)", GENRES, key="genre_list_sel")
        
        # 4. 곡 분위기 & 템포
        col1, col2 = st.columns(2)
        with col1:
            song_atm = st.selectbox("🌈 곡 분위기", ["밝은", "슬픈", "웅장한", "서정적인", "긴박한"])
        with col2:
            tempo = st.select_slider("⏱️ 템포", options=["매우 느림", "느림", "보통", "빠름", "매우 빠름"], value="보통")
            
        # 5. 보컬 (남,여,듀엣 각 20개 이상)
        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
        vocal_style = st.selectbox(f"🗣️ {v_type} 보컬 스타일", VOCALS[v_type], key="v_style_sel")
        
        # 6. 메인 악기 (10개)
        main_inst = st.selectbox("🎹 메인 악기 선택", INSTRUMENTS, key="inst_sel")
        
        st.divider()
        gen_lyrics_btn = st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True)

    # --- 오른쪽 메인 영역: AI 세션 설정 결과 ---
    st.title("🎼 AI 음악 제작 분석")
    
    if gen_lyrics_btn:
        st.session_state.music_ready = True
        with st.spinner("AI가 곡 구성을 분석 중입니다..."):
            # AI 세션 매핑 로직 작동
            recommended_session = SESSION_MAP.get(main_inst, "기본 오케스트라 구성")
            st.session_state.ai_session = recommended_session
            
            # 가사 생성 시뮬레이션
            st.session_state.gen_lyrics = f"[{target} - {genre}]\n분위기: {lyric_mood}\n메인악기: {main_inst}\n보컬: {v_type}({vocal_style})\n\n[Verse 1]\n{subject}에 대해 노래합니다..."

    if st.session_state.get('music_ready'):
        # AI 세션 설정 출력 [확실함]
        with st.container(border=True):
            st.subheader(f"🤖 AI 추천 세션 구성 (메인: {main_inst})")
            st.info(f"👉 추천 서브 세션: **{st.session_state.ai_session}**")
            st.caption(f"템포 '{tempo}'와(과) 보컬 '{vocal_style}'에 맞춰 악기 밸런스가 조정되었습니다.")

        st.divider()
        st.subheader("📝 생성된 가사")
        st.text_area("가사 확인 및 편집", value=st.session_state.gen_lyrics, height=350, key="lyrics_final_edit")
    else:
        st.info("👈 왼쪽 사이드바에서 모든 옵션을 선택한 후 시작 버튼을 눌러주세요.")
