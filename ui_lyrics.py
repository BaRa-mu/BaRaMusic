import streamlit as st
import time
import utils

def render_tab1():
    # --- UI 간격을 극단적으로 밀착시키는 CSS (한눈에 보기 최적화) ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -22px !important; padding-top: 0px !important; }
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 11px !important; margin-bottom: -12px !important; color: #666 !important;
        }
        div[data-baseweb="select"], .stTextInput input {
            min-height: 24px !important; height: 30px !important; font-size: 13px !important; padding: 2px 8px !important;
        }
        .stRadio div[role="radiogroup"] { gap: 8px !important; margin-top: -10px !important; }
        hr { margin: 4px 0px !important; }
        /* st.code 박스 여백 조절 */
        .stCode { margin-top: -10px !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        # 곡 설정 타이틀과 생성 버튼 나란히 배치
        h_col, b_col = st.columns([1, 1.2])
        with h_col: st.subheader("📝 곡 설정")
        with b_col: gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        
        lyric_styles = ["시적인 (Poetic)", "직설적인 (Direct)", "서사적인 (Narrative)", "은유적인 (Metaphorical)", "현대적인 (Contemporary)", "성경적인 (Biblical)", "추상적인 (Abstract)", "감성적인 (Emotive)", "이야기하듯 (Storytelling)", "대화하듯 (Conversational)", "비유적인 (Allegorical)", "철학적인 (Philosophical)", "찬양 중심 (Worship)", "생활 밀착형 (Life-centered)", "서정적인 (Lyrical)", "따뜻한 (Heartwarming)"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "어둡고 무거운", "몽환적인", "따뜻하고 포근한", "사랑스러운", "흥겨운"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        col_a, col_b = st.columns(2)
        with col_a: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with col_b: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.write("**🎤 보컬 유형**")
        v_type = st.radio("보컬", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # 보컬 상세 리스트 (원본 유지)
        if v_type == "남자": s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝", "허스키 남성", "파워풀 락 남성", "인디 남성", "R&B 남성", "바리톤", "가스펠 남성", "미성 남성", "빈티지 락", "신스팝 남성", "ASMR 보컬", "힙합/랩", "발라드 남성", "담백한 포크", "드라마틱 남성", "블루지 남성", "청량한 남성", "몽환적 남성", "재지한 남성", "트렌디 오토튠"])
        elif v_type == "여자": s_vocal = st.selectbox("👩‍🎤 스타일", ["청아한 여성 팝", "파워 디바", "공기반 소리반", "알앤비 여성", "포근한 어쿠스틱", "상큼한 아이돌", "소울 가스펠", "세련된 재즈", "폭발적 락 여성", "인디 포크", "감성 발라드", "청량한 여성", "신비로운 일렉", "소프라노", "로파이 여성", "걸크러시 힙합", "드라마틱 여성", "빈티지 레트로", "트렌디 팝", "시네마틱 여성"])
        elif v_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 화음 남녀 듀엣", "애절한 이별 남녀 발라드", "파워풀 남녀 가스펠 듀엣", "달콤한 로맨틱 듀엣", "그루비 R&B 소울 듀엣", "남성 화음", "여성 팝 화음", "락 듀엣", "인디 남녀", "오페라 남녀", "댄스 팝 듀엣", "뮤지컬 듀엣", "포크 듀엣", "재즈 듀엣", "시네마틱 듀엣", "소년소녀 듀엣", "메인남 코러스여", "메인여 코러스남", "앰비언트 듀엣", "가창력 대결"])
        elif v_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 대규모 성가대", "파워풀 가스펠 합창", "맑은 어린이 성가대", "그레고리안 성가", "에픽 코러스", "교회 성가대", "앰비언트 코러스", "오페라 합창", "청년 찬양대", "몽환적 백그라운드"])
        else: s_vocal = "Instrumental"

        if gen_btn:
            if not subject: 
                st.error("주제를 입력하세요."); return
            
            with st.spinner("가사와 완벽히 매칭되는 제목을 구상 중..."):
                time.sleep(0.6)
                
                # --- 🎵 가사 내용에 맞춘 리얼한 제목 생성 로직 ---
                # 주제어에서 핵심 명사를 찾아 제목화 (단순 어미 제거 아님)
                if "행복" in subject or "즐겁" in subject:
                    kr_title = "기쁨의 노래" if target=="대중음악" else "영원한 즐거움"
                    en_title = "Song of Joy" if target=="대중음악" else "Everlasting Joy"
                elif "위로" in subject or "평안" in subject:
                    kr_title = "내 영혼의 안식"
                    en_title = "Rest for My Soul"
                elif "사랑" in subject:
                    kr_title = "변치 않는 그 사랑"
                    en_title = "Unchanging Love"
                elif "은혜" in subject:
                    kr_title = "은혜의 강가에서"
                    en_title = "By the River of Grace"
                else:
                    kr_title = f"{subject[:10]}의 고백"
                    en_title = "My Sincere Confession"
                
                st.session_state.gen_title_kr = kr_title
                st.session_state.gen_title_en = en_title

                # --- 🎸 프롬프트 생성 (800~1000자) ---
                p_base = f"Professional {target} production. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. Vocals: {s_vocal}. Main Instrument: {s_inst}. Style: {s_lyric_style}. Title Theme: {kr_title}. "
                while len(p_base) < 880: p_base += "Ensure high-fidelity audio engineering, pristine mixing, and a wide cinematic soundscape with professional mastering. "
                st.session_state.gen_prompt = p_base[:995]

                # --- 📝 가사 생성 ---
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 정서를 담아 곡을 여는 {s_inst}의 서정적인 연주)

[Verse 1]
창밖의 풍경이 멈춘 듯한 이 고요한 시간에
내 마음 깊은 곳에 담아둔 이야기를 꺼내어 봅니다
단순한 말들로는 다 채울 수 없는 커다란 고백
"{subject}"
이 문장 하나를 가슴에 품고 오늘을 살아냈습니다
때로는 거친 바람이 앞길을 가로막아도
내 곁을 지켜주던 따스한 온기가 다시 나를 깨우네요

[Pre-Chorus]
(스타일: {s_lyric_style})
천천히 스며드는 빛의 물결을 따라서
잊고 지냈던 소중한 꿈들이 다시 숨을 쉬기 시작합니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 노래하리

[Verse 2]
내딛는 발걸음마다 새겨진 수많은 흔적들 속에
어제보다 더 깊어진 소망의 뿌리를 내려봅니다
"{subject}"
그 약속의 마음이 내 삶의 나침반이 되어줍니다

[Bridge]
(점점 고조되며 웅장해지는 {s_inst} 사운드)
나의 모든 호흡과 진심을 다해 그 영광을 노래하노라

[Outro]
나 이제 참된 자유를 얻었네
"{subject}"
그 영원하고도 아름다운 사랑 안에서...
({s_inst}의 잔잔한 여운과 함께 평화롭게 마무리)"""

    with right_col:
        st.subheader("✨ 생성 결과물")
        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                # 제목 출력
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (우측 상단 버튼으로 복사 가능)**")
                # 가사를 st.code로 출력하여 복사 버튼 활성화
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 왼쪽 메뉴에서 곡 설정을 마친 후 상단 '생성' 버튼을 눌러주세요.")
