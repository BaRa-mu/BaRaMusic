import streamlit as st
import time
import utils

def render_tab1():
    # --- 폰트 크기 축소를 위한 CSS 주입 (메뉴를 한눈에 더 많이 보기 위함) ---
    st.markdown("""
        <style>
        .stSelectbox div[data-baseweb="select"] { font-size: 13px !important; }
        .stSelectbox label { font-size: 12px !important; margin-bottom: 0px !important; }
        .stRadio label { font-size: 13px !important; }
        .stTextInput label { font-size: 13px !important; }
        </style>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        # --- 상단: 곡 설정 제목과 생성 버튼을 한 줄에 배치 ---
        header_col, btn_col = st.columns([1, 1.2])
        with header_col:
            st.subheader("📝 곡 설정")
        with btn_col:
            # 버튼을 상단 메뉴 옆으로 이동
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐거운 삶")
        
        # 가사 스타일 추가 (시적인, 직설적인 등 풍성하게 구성)
        lyric_styles = [
            "시적인 (Poetic)", "직설적인 (Direct)", "서사적인 (Narrative)", "은유적인 (Metaphorical)", 
            "현대적인 (Contemporary)", "성경적인 (Biblical)", "추상적인 (Abstract)", "감성적인 (Emotive)", 
            "이야기하듯 (Storytelling)", "대화하듯 (Conversational)", "비유적인 (Allegorical)", 
            "철학적인 (Philosophical)", "찬양 중심 (Worship)", "생활 밀착형 (Life-centered)", 
            "웅변적인 (Eloquent)", "서정적인 (Lyrical)", "간결한 (Minimalist)", "따뜻한 (Heartwarming)"
        ]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 타겟 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            pop_moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "어둡고 무거운", "몽환적인", "쓸쓸하고 우울한", "따뜻하고 포근한", "신비로운", "향수를 부르는", "사랑스러운", "흥겨운"]
            s_mood = st.selectbox("✨ 분위기", pop_moods)
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            ccm_moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬", "감성적인"]
            s_mood = st.selectbox("✨ 분위기", ccm_moods)

        col_a, col_b = st.columns(2)
        with col_a: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with col_b: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.write("**🎤 보컬 유형**")
        vocal_type = st.radio("보컬", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # 보컬 데이터 (기존 유지)
        if vocal_type == "남자": s_vocal = st.selectbox("👨‍🎤 남성 스타일", ["감미로운 남성 팝", "허스키 남성", "파워풀 락 남성", "인디 남성", "R&B 남성", "바리톤", "가스펠 남성", "미성 남성", "빈티지 락", "신스팝 남성", "ASMR 보컬", "힙합/랩", "발라드 남성", "담백한 포크", "드라마틱 남성", "블루지 남성", "청량한 남성", "몽환적 남성", "재지한 남성", "트렌디 오토튠"])
        elif vocal_type == "여자": s_vocal = st.selectbox("👩‍🎤 여성 스타일", ["청아한 여성 팝", "파워 디바", "공기반 소리반", "알앤비 여성", "포근한 어쿠스틱", "상큼한 아이돌", "소울 가스펠", "세련된 재즈", "폭발적 락 여성", "인디 포크", "감성 발라드", "청량한 여성", "신비로운 일렉", "소프라노", "로파이 여성", "걸크러시 힙합", "드라마틱 여성", "빈티지 레트로", "트렌디 팝", "시네마틱 여성"])
        elif vocal_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 듀엣 스타일", ["남녀 어쿠스틱", "남녀 발라드", "가스펠 듀엣", "로맨틱 듀엣", "R&B 소울 듀엣", "남성 화음", "여성 팝 화음", "락 듀엣", "인디 남녀", "오페라 남녀", "댄스 팝 듀엣", "뮤지컬 듀엣", "포크 듀엣", "재즈 듀엣", "시네마틱 듀엣", "소년소녀 듀엣", "메인남 코러스여", "메인여 코러스남", "앰비언트 듀엣", "가창력 대결"])
        elif vocal_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 합창 스타일", ["대규모 성가대", "흑인 가스펠", "어린이 성가대", "그레고리안 성가", "에픽 코러스", "교회 성가대", "앰비언트 코러스", "오페라 합창", "청년 찬양대", "몽환적 백그라운드"])
        else: s_vocal = "Instrumental"

        # --- 생성 로직 시작 ---
        if gen_btn:
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("AI가 사람처럼 고심하여 가사를 쓰고 있습니다..."):
                time.sleep(0.5) 
                st.session_state.gen_title_kr = f"{subject[:10]}" if len(subject) > 10 else subject
                st.session_state.gen_title_en = "Melody of Life"

                # 1. 프롬프트 생성 (스타일 반영)
                prompt_blocks = [
                    f"Professional {target} track. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. ",
                    f"Vocals: {s_vocal}. Main Instrument: {s_inst}. Lyric Style: {s_lyric_style}. ",
                    "Full long version (3-8 min) with cinematic builds and emotional depth. Studio quality."
                ]
                final_p = "".join(prompt_blocks)
                while len(final_p) < 850: final_p += "Enhance the spatial richness and professional arrangement. "
                st.session_state.gen_prompt = final_p[:995]

                # 2. 가사 생성 (스타일과 흐름을 사람처럼 자연스럽게)
                inst_nm = s_inst if s_inst != '선택안함' else '악기'
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 정서를 담아 곡을 여는 {inst_nm}의 서정적인 연주)

[Verse 1]
창밖의 풍경이 멈춘 듯한 이 고요한 시간에
내 마음 깊은 곳에 담아둔 이야기를 꺼내어 봅니다
단순한 말들로는 다 채울 수 없는 커다란 고백
{subject}
이 문장 하나를 가슴에 품고 오늘을 살아냈습니다
때로는 거친 바람이 앞길을 가로막아도
내 곁을 지켜주던 따스한 온기가 다시 나를 깨우네요

[Pre-Chorus]
스타일: {s_lyric_style}
천천히 스며드는 빛의 물결을 따라서
잊고 지냈던 소중한 꿈들이 다시 숨을 쉬기 시작합니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 춤추리

[Verse 2]
내딛는 발걸음마다 새겨진 수많은 흔적들 속에
{subject}
그 약속의 말씀이 내 삶의 나침반이 되어줍니다
상처 입은 날개로 힘겹게 날아오르던 어제는 가고
이제는 독수리처럼 저 하늘 높이 비상할 새 힘을 얻네
눈물로 씨를 뿌리던 골짜기는 기쁨의 강물이 되어 흐르고

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 춤추리

[Bridge]
시간의 강물이 굽이쳐 흐르고 모든 것이 변해가도
내 영혼에 새겨진 그 이름, 결코 지워지지 않는 영원한 불꽃
(점점 고조되며 폭발적인 {inst_nm} 솔로와 함께 웅장해지는 사운드)
나의 모든 호흡과 진심을 다해 그 영광을 노래하노라

[Interlude]
({inst_nm}가 폭발적으로 몰아치며 감정을 최고조로 끌어올리는 간주)

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 춤추리

[Outro]
나 이제 참된 자유를 얻었네
{subject}
그 영원하고도 아름다운 사랑 안에서...
({inst_nm}의 잔잔한 여운과 함께 평화롭게 마무리)"""

    with right_col:
        st.subheader("✨ 생성 결과물")
        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            with st.container(border=True):
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=550, label_visibility="collapsed")
        else:
            st.info("👈 왼쪽에서 곡 설정을 마친 후 상단 '생성' 버튼을 눌러주세요.")
