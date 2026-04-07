import streamlit as st
import time
import utils

def render_tab1():
    # --- 메뉴 가시성을 위해 폰트 크기 축소 CSS ---
    st.markdown("""
        <style>
        .stSelectbox div[data-baseweb="select"] { font-size: 13px !important; }
        .stSelectbox label { font-size: 12px !important; margin-bottom: 0px !important; }
        .stRadio label { font-size: 13px !important; }
        .stTextInput label { font-size: 13px !important; }
        </style>
    """, unsafe_allow_html=True)

    # 왼쪽 메뉴칸(1) : 오른쪽 결과물(2.5) 비율
    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        # 곡 설정 타이틀과 생성 버튼을 한 줄에 배치
        header_col, btn_col = st.columns([1, 1.2])
        with header_col:
            st.subheader("📝 곡 설정")
        with btn_col:
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐거운 삶")
        
        # 가사 스타일 드롭다운 (사람이 쓴 것처럼 풍성하게 구성)
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
        
        # 보컬 리스트 복구 (원래의 긴 명칭 20개/10개 리스트)
        if vocal_type == "남자":
            s_vocal = st.selectbox("👨‍🎤 남성 스타일", [
                "감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", 
                "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", 
                "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", 
                "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", 
                "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"
            ])
        elif vocal_type == "여자":
            s_vocal = st.selectbox("👩‍🎤 여성 스타일", [
                "맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", 
                "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련되고 도도한 재즈 보컬", 
                "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", 
                "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", 
                "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"
            ])
        elif vocal_type == "듀엣":
            s_vocal = st.selectbox("🧑‍🤝‍🧑 듀엣 스타일", [
                "아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", 
                "그루비한 R&B 소울 듀엣", "남성 2인조 화음 보컬", "여성 2인조 팝 화음 보컬", "에너제틱한 락 보컬 남녀 듀엣", 
                "인디 감성의 나른한 남녀 듀엣", "오페라/크로스오버 스타일 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "서로 주고받는 대화형 뮤지컬 듀엣", 
                "잔잔하고 위로가 되는 포크 듀엣", "재지한 피아노 바 감성의 듀엣", "어두운 분위기의 시네마틱 듀엣", "소년 소녀 느낌의 풋풋한 듀엣", 
                "메인 남성 보컬 & 여성 코러스 화음", "메인 여성 보컬 & 남성 코러스 화음", "신비로운 앰비언트 보컬 듀엣", "폭발적인 가창력 대결 스타일 듀엣"
            ])
        elif vocal_type == "합창":
            s_vocal = st.selectbox("👨‍👩‍👧‍👦 합창 스타일", [
                "웅장하고 홀리한 대규모 성가대", "파워풀하고 리드미컬한 흑인 가스펠 합창", "맑고 순수한 어린이 성가대", "신비로운 중세 그레고리안 성가", 
                "장엄하고 시네마틱한 에픽 코러스", "따뜻하고 대중적인 교회 성가대", "천상의 소리 같은 앰비언트 코러스", "강렬하고 비장한 오페라 합창", 
                "경쾌하고 희망찬 청년 연합 찬양대", "속삭이는 듯한 몽환적인 백그라운드 합창"
            ])
        else:
            s_vocal = "Instrumental"

        if gen_btn:
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("생성 중..."):
                time.sleep(0.5)
                # 제목: 한글제목_영어제목 형식
                st.session_state.gen_title_kr = f"{subject[:15]}"
                st.session_state.gen_title_en = "Grace of Life"

                # 프롬프트: 800-1000자
                prompt_blocks = [
                    f"Professional {target} track. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. ",
                    f"Vocals: {s_vocal}. Main Instrument: {s_inst}. Lyric Style: {s_lyric_style}. ",
                    "Song Structure: [Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Solo], [Outro]. ",
                    "Length: Full version 3:00-8:00 minutes. Studio quality, high fidelity, wide stereo."
                ]
                final_p = "".join(prompt_blocks)
                while len(final_p) < 850: final_p += "Enhance the spatial richness and professional harmonic balance. "
                st.session_state.gen_prompt = final_p[:995]

                # 가사: 3분 이상 분량, subject를 독립 행으로 처리하여 자연스럽게 구성
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 분위기를 담아 곡을 여는 {s_inst}의 서정적인 연주)

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
상처 입은 날개로 힘겹게 날아오르던 어제는 가고
이제는 독수리처럼 저 하늘 높이 비상할 새 힘을 얻네

[Bridge]
시간의 강물이 굽이쳐 흐르고 모든 것이 변해가도
내 영혼에 새겨진 그 이름, 결코 지워지지 않는 영원한 불꽃
(점점 고조되며 웅장해지는 사운드)
나의 모든 호흡과 진심을 다해 그 영광을 노래하노라

[Interlude]
({s_inst}가 폭발적으로 몰아치며 감정을 최고조로 끌어올리는 간주)

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 머무르리
흔들리던 마음도, 차갑게 얼어붙은 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 영원히 노래하리

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
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (전/간/후주 포함)**")
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=550, label_visibility="collapsed")
