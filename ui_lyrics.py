import streamlit as st
import time
import utils

def render_tab1():
    # --- 겹침을 방지하고 간격을 밀착시키는 안전한 CSS ---
    st.markdown("""
        <style>
        /* 메뉴 간 수직 간격 최적화 (겹치지 않을 만큼만 줄임) */
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; }
        
        /* 라벨 디자인 최적화 */
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 13px !important; color: #444 !important; font-weight: 600 !important;
            margin-bottom: -5px !important;
        }
        
        /* 입력창/선택창 높이 균형 */
        div[data-baseweb="select"], .stTextInput input {
            min-height: 35px !important; font-size: 13px !important;
        }
        
        /* 라디오 버튼 배치 최적화 */
        .stRadio div[role="radiogroup"] { gap: 15px !important; }
        
        /* 결과창 복사 버튼 가시성 확보 */
        .stCode { margin-top: -5px !important; border: 1px solid #eee !important; }
        </style>
    """, unsafe_allow_html=True)

    # 화면 비율: 왼쪽 메뉴(1) : 오른쪽 결과물(2.3)
    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        # --- [상단] 곡 설정과 생성 버튼 분리 배합 ---
        # 겹침 방지를 위해 여유 있는 비율로 나눔
        header_col, btn_col = st.columns([0.8, 1.2])
        with header_col: 
            st.write("### 📝 곡 설정")
        with btn_col: 
            # 버튼이 위로 튀지 않게 여백 살짝 부여
            st.write("") 
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        
        # 가사 스타일 (사람이 쓴 듯한 옵션)
        lyric_styles = [
            "서정적인 (Lyrical)", "시적인 (Poetic)", "직설적인 (Direct)", "성경적인 (Biblical)", 
            "현대적인 (Contemporary)", "감성적인 (Emotive)", "이야기하듯 (Storytelling)", "찬양 중심 (Worship)"
        ]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 장르 및 분위기 (선택에 따른 동적 드롭다운)
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한", "사랑스러운", "흥겨운"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        # 템포 및 메인 악기 나란히 배치
        col1, col2 = st.columns(2)
        with col1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with col2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider() # 보관 영역 구분
        st.write("**🎤 보컬 유형**")
        v_type = st.radio("보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # 보컬 상세 선택 (원본 20개 리스트 완벽 보존)
        if v_type == "남자": s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"])
        elif v_type == "여자": s_vocal = st.selectbox("👩‍🎤 스타일", ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련되고 도도한 재즈 보컬", "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"])
        elif v_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", "그루비한 R&B 소울 듀엣", "남성 화음 보컬", "여성 팝 화음 보컬", "락 보컬 남녀 듀엣", "인디 감성 남녀 듀엣", "오페라/크로스오버 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "뮤지컬 대화형 듀엣", "위로가 되는 포크 듀엣", "재지한 피아노 바 듀엣", "시네마틱 듀엣", "소년 소녀 풋풋한 듀엣", "남성 보컬 & 여성 코러스", "여성 보컬 & 남성 코러스", "앰비언트 보컬 듀엣", "가창력 대결 스타일 듀엣"])
        elif v_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 대규모 성가대", "리드미컬한 가스펠 합창", "맑은 어린이 성가대", "중세 그레고리안 성가", "에픽 시네마틱 코러스", "따뜻한 교회 성가대", "앰비언트 코러스", "장엄한 오페라 합창", "청년 연합 찬양대", "몽환적 백그라운드 코러스"])
        else: s_vocal = "Instrumental"

        if gen_btn:
            if not subject: 
                st.error("주제를 입력해 주세요."); return
            
            with st.spinner("가사와 제목을 완벽히 매칭하는 중..."):
                time.sleep(0.5)
                
                # --- 🎵 가사 내용의 분위기를 읽어낸 노래 제목 생성 ---
                if any(x in subject for x in ["기쁨", "즐겁", "행복"]):
                    kr_t, en_t = "기쁨의 축제", "Celebration of Joy"
                elif any(x in subject for x in ["평안", "쉼", "안식", "위로"]):
                    kr_t, en_t = "고요한 쉼표", "Quiet Rest for My Soul"
                elif "사랑" in subject:
                    kr_t, en_t = "영원한 사랑의 고백", "Everlasting Confession"
                elif "은혜" in subject:
                    kr_t, en_t = "하늘의 은혜", "Grace from Above"
                else:
                    kr_t, en_t = f"{subject[:10]}", "A Heartfelt Melody"
                
                st.session_state.gen_title_kr = kr_t
                st.session_state.gen_title_en = en_t

                # --- 🎸 스타일 프롬프트 (800~1000자) ---
                p_base = f"Professional {target} production. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. Vocals: {s_vocal}. Main Inst: {s_inst}. Style: {s_lyric_style}. Theme: {kr_t}. "
                while len(p_base) < 880: p_base += "Ensure high-fidelity audio engineering, wide stereo mastering, and cinematic harmonic balance for a pristine studio soundscape. "
                st.session_state.gen_prompt = p_base[:995]

                # --- 📝 가사 생성 (자연스러운 구성) ---
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 분위기를 여는 {s_inst}의 서정적인 전주)

[Verse 1]
조용히 흐르는 시간 속에 내 마음을 담아
나지막이 이 깊은 고백을 읊조려보네
"{subject}"
이 문장 하나를 가슴에 품고 오늘을 살아냈습니다
때로는 거친 바람이 앞길을 가로막아도
내 곁을 지켜주던 따스한 온기가 다시 나를 깨우네요

[Pre-Chorus]
천천히 스며드는 빛의 물결을 따라서
잊고 지냈던 소중한 꿈들이 다시 숨을 쉬기 시작합니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 노래하리

[Bridge]
(분위기를 고조시키며 웅장해지는 {s_inst} 연주)
나의 모든 호흡과 진심을 다해 그 영광을 노래하노라

[Outro]
나 이제 참된 자유를 얻었네
"{subject}"
({s_inst}의 잔잔한 여운과 함께 평화로운 마무리)"""

    # --- 오른쪽 결과 출력 (복사 버튼 제공을 위해 st.code 사용) ---
    with right_col:
        st.subheader("✨ 생성 결과물")
        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (우측 상단 버튼으로 복사)**")
                # language="markdown"을 설정하여 가독성 및 복사 아이콘 활성화
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 왼쪽 메뉴에서 설정을 마친 후 상단 '생성' 버튼을 눌러주세요.")
