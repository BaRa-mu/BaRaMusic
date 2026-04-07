import streamlit as st
import time
import utils

def render_tab1():
    # --- UI 간격 및 박스 높이 최적화 CSS (기존 유지) ---
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
        hr { margin: 8px 0px !important; }
        .stCode { margin-top: -5px !important; border: 1px solid #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") 
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        
        # 가사 스타일 리스트
        lyric_styles = ["서정적인 (Lyrical)", "시적인 (Poetic)", "직설적인 (Direct)", "성경적인 (Biblical)", "현대적인 (Contemporary)", "감성적인 (Emotive)", "이야기하듯 (Storytelling)", "찬양 중심 (Worship)"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한", "사랑스러운", "흥겨운"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        c1, c2 = st.columns(2)
        with c1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with c2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider()
        st.write("**🎤 보컬 유형**")
        v_type = st.radio("보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # 보컬 상세 데이터 (생략)
        if v_type == "남자": s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝 보컬", "허스키 남성", "파워풀 락 남성", "인디 남성", "R&B 남성", "바리톤", "가스펠 남성", "미성 남성", "빈티지 락", "신스팝 남성", "ASMR 보컬", "힙합/랩", "발라드 남성", "담백한 포크", "드라마틱 남성", "블루지 남성", "청량한 남성", "몽환적 남성", "재지한 남성", "트렌디 오토튠"])
        elif v_type == "여자": s_vocal = st.selectbox("👩‍🎤 스타일", ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적 여성", "알앤비 여성", "포근한 어쿠스틱", "상큼한 아이돌", "소울 가스펠", "세련된 재즈", "폭발적 락 여성", "인디 포크", "감성 발라드", "청량한 여성", "신비로운 일렉", "소프라노", "로파이 여성", "걸크러시 힙합", "드라마틱 여성", "빈티지 레트로", "트렌디 팝", "시네마틱 여성"])
        elif v_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 화음 남녀 듀엣", "애절한 이별 남녀 발라드", "파워풀 남녀 가스펠 듀엣", "달콤한 로맨틱 듀엣", "그루비 R&B 소울 듀엣", "남성 화음 보컬", "여성 팝 화음 보컬", "락 보컬 남녀 듀엣", "인디 감성 남녀 듀엣", "오페라 남녀 듀엣", "댄스 팝 남녀 듀엣", "뮤지컬 대화형 듀엣", "위로가 되는 포크 듀엣", "재지한 피아노 바 듀엣", "시네마틱 듀엣", "소년 소녀 풋풋한 듀엣", "남성 보컬 & 여성 코러스", "여성 보컬 & 남성 코러스", "앰비언트 보컬 듀엣", "가창력 대결"])
        elif v_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 대규모 성가대", "리드미컬한 가스펠 합창", "맑은 어린이 성가대", "중세 그레고리안 성가", "에픽 시네마틱 코러스", "따뜻한 교회 성가대", "앰비언트 코러스", "장엄한 오페라 합창", "청년 연합 찬양대", "몽환적 백그라운드 코러스"])
        else: s_vocal = "Instrumental"

    with right_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not subject: st.error("주제를 먼저 입력해 주세요."); return
            with st.spinner(f"[{s_lyric_style}] 스타일로 가사를 구성 중..."):
                time.sleep(0.5)
                
                # 🎵 가사 스타일에 따른 어휘 및 템플릿 엔진
                if "시적인" in s_lyric_style:
                    v1 = f"달빛이 내려앉은 고요한 숲길 사이로\n나부끼는 바람에 실려온 은은한 향기\n{subject}, 그 떨림의 조각들을 모아\n밤하늘 은하수 위에 수놓아 봅니다"
                    ch = f"별들이 노래하는 영원한 평안 속에\n내 영혼은 나비가 되어 너울거리네\n눈물마저 보석이 되는 신비로운 사랑\n나 그 품에 안겨 영원을 꿈꾸리"
                elif "직설적인" in s_lyric_style:
                    v1 = f"어제는 정말 힘들고 지쳐서 쓰러질 뻔했죠\n누구 하나 내 마음 알아주는 사람 없었지만\n{subject}, 이 한마디가 나를 다시 일으켰어요\n이제는 숨기지 않고 내 진심을 말해볼게요"
                    ch = f"정말 행복해요, 당신과 함께하는 이 시간\n복잡한 생각은 다 버리고 그냥 웃어봐요\n내 옆에 있어줘서 고맙다는 그 말\n오늘 꼭 전하고 싶었어요"
                elif "성경적인" in s_lyric_style:
                    v1 = f"광야의 메마른 땅을 걷는 이스라엘처럼\n목마름에 지쳐 하늘을 우러러볼 때\n{subject}, 만나와 메추라기로 채우시는 은혜\n불기둥과 구름기둥으로 우리를 인도하시네"
                    ch = f"여호와는 나의 목자시니 부족함 없으리\n푸른 초장 잔잔한 물가로 이끄시는 주\n사망의 음침한 골짜기도 두렵지 않음은\n주의 지팡이와 막대기가 나를 안위하심이라"
                else: # 기본 서정적인 스타일
                    v1 = f"조용히 흐르는 시간 속에 내 마음을 담아\n나지막이 이 깊은 고백을 읊조려보네\n{subject}\n고단했던 하루의 끝에서 나를 기다려준\n따스한 주의 온기가 다시 나를 깨웁니다"
                    ch = f"영원한 평안, 그 깊은 안식 속에 나 머무르리\n흔들리던 마음도, 얼어붙은 두려움도\n주의 품 안에서 눈 녹듯 사라지니\n나 영원히 주를 찬양하며 노래하리"

                # 최종 제목 및 가사 조합
                st.session_state.gen_title_kr = f"{subject[:8]}" if len(subject)>8 else subject
                st.session_state.gen_title_en = "Grace of Heart"
                
                st.session_state.gen_lyrics = f"""[Intro]\n({s_mood} 분위기를 여는 {s_inst} 전주)\n\n[Verse 1]\n{v1}\n\n[Pre-Chorus]\n잊고 지냈던 소중한 꿈들이 다시 숨을 쉽니다\n이제는 두려움 없이 저 넓은 소망의 바다로 나아갑니다\n\n[Chorus]\n{ch}\n\n[Verse 2]\n한 걸음 내딛는 삶의 모든 발자국 속에\n어제보다 더 깊어진 소망의 뿌리를 내립니다\n{subject}\n그 약속의 말씀이 내 삶의 나침반이 됩니다\n\n[Bridge]\n시간의 강물이 흐르고 세상이 변해가도\n내 영혼에 새겨진 그 이름, 영원한 불꽃\n(웅장해지는 {s_inst} 연주)\n\n[Chorus]\n{ch}\n\n[Outro]\n나 이제 참된 자유와 안식을 얻었네\n{subject}\n({s_inst}의 잔잔한 여운과 함께 마무리)"""
                st.session_state.gen_prompt = f"Professional track. Style: {s_lyric_style}. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. Inst: {s_inst}. Vocals: {s_vocal}."

            # 결과 출력
            with st.container(border=True):
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            with st.container(border=True):
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.code(st.session_state.gen_lyrics, language="markdown")
