import streamlit as st

# [데이터 영역: 분위기 옵션 직관화]
MOODS = {
    "CCM": ["동화같은", "직설적인", "서정적인", "웅장한", "담백한", "경쾌한", "신비로운", "따뜻한", "강렬한", "애절한", "평화로운", "거룩한", "희망찬", "비장한", "소박한"],
    "대중음악": ["동화같은", "직설적인", "서정적인", "도시적인", "복고풍의", "몽환적인", "열정적인", "감미로운", "냉소적인", "통통튀는", "아련한", "우울한", "청량한", "세련된", "투박한"]
}
CCM_GENRES = ["현대적 워십", "모던 락 찬양", "어쿠스틱 포크", "블랙 가스펠", "클래식 찬송가", "컨템포러리 찬양"]
POP_GENRES = ["스탠다드 발라드", "어쿠스틱 포크", "모던 락", "블루스 팝", "소울 알앤비", "시티 팝"]
SONG_ATMOSPHERES = ["밝고 희망찬", "차분하고 정적인", "웅장하고 힘있는", "슬프고 서정적인", "따뜻하고 포근한"]
VOCALS = {"남성": ["허스키한 저음 남성", "맑은 미성 고음 남성"], "여성": ["청아한 고음 여성", "몽환적 음색 여성"], "듀엣": ["남녀 듀엣", "동성 듀엣"]}
INSTRUMENTS = ["신디사이저", "그랜드 피아노", "어쿠스틱 기타", "일렉 기타", "첼로"]
SESSION_MAP = {"신디사이저": "아르페지에이터, 신스 패드", "그랜드 피아노": "스트링 섹션", "어쿠스틱 기타": "퍼커션", "일렉 기타": "드럼과 베이스", "첼로": "피아노 반주"}

def render_tab1():
    # CSS: 탭 왼쪽 정렬 및 텍스트 영역 높이 강제 확장
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }
        div[data-baseweb="textarea"] textarea { min-height: 1000px !important; font-size: 16px !important; line-height: 1.6 !important; }
        .block-container { padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🎵 음악 생성 설정")
        subject = st.text_input("💡 곡 주제", key="l_subject")
        target = st.radio("🎯 타깃", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        lyric_mood = st.selectbox(f"✨ 가사 분위기", MOODS[target], key="mood_sel")
        genre = st.selectbox(f"🎸 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
        song_atm = st.selectbox("🌈 곡 분위기", SONG_ATMOSPHERES, key="song_atm_sel")
        tempo = st.select_slider("⏱️ 템포", options=["느림", "보통", "빠름"], value="보통")
        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
        vocal_style = st.selectbox(f"🗣️ 스타일", VOCALS[v_type], key="v_style_sel")
        main_inst = st.selectbox("🎹 메인 악기", INSTRUMENTS, key="inst_sel")
        st.divider()
        strict_end = st.checkbox("가사 종료 시 즉시 곡 종료", value=True, key="strict_end_check")

        if st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True):
            # [결과] 제목: 한글제목_영어제목 형식
            st.session_state.res_title = f"{subject}_Heavenly_Visions"
            
            # [가사] 3~8분 분량 확보 (대규모 4절 구조)
            ending_tags = "\n\n[Outro]\n(Natural fade out to silence)\n[END]\n[Hard Stop]\n[Silence]"
            st.session_state.res_lyrics = f"""[Verse 1]\n{subject}의 깊은 숨결이 새벽 공기를 타고 내 영혼의 가장 깊은 곳에 스며드네\n캄캄한 어둠의 긴 터널을 지나 우리에게 찾아온 찬란하고 눈부신 소망의 빛줄기 하나\n세상의 무거운 짐을 모두 내려놓고 주님의 넓고 따뜻한 품에 고요히 안기어\n평안한 안식 속에 새로운 생명의 꿈을 꾸게 하시는 은혜의 세밀한 손길\n\n[Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해\n{song_atm}한 리듬이 우리 심장을 뜨겁게 울리며 닫혔던 하늘 문을 활짝 열어줄 때\n{subject}의 놀라운 축복이 마르지 않는 강물처럼 우리 삶에 넘치도록 흐르리\n\n[Verse 2]\n메마른 광야 길을 걷다 지쳐 쓰러질 때도 생명수의 샘물은 결코 마르지 않네\n낮에는 구름 기둥으로 밤에는 불 기둥으로 우리의 모든 앞길을 한 치 오차 없이 인도하시니\n거친 파도가 휘몰아치고 폭풍우가 날 덮쳐와도 흔들리지 않는 견고한 반석 같은 믿음으로\n약속의 땅, 젖과 꿀이 흐르는 그 아름다운 곳을 향해 우린 담대히 한 걸음씩 나아가리라\n\n[Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해\n\n[Bridge]\n하늘 문이 활짝 열리고 영광의 찬란한 광채가 이 낮고 천한 땅 위를 가득 비추네\n상처 입은 모든 영혼들이 주님의 따스한 손길로 치유받고 온전히 회복되는 역사의 현장\n간절한 기도의 향연이 금향로에 담겨 보좌 앞에 가장 향기롭게 상달될 때\n우리의 영혼은 독수리 날개 치며 저 높은 푸른 창공을 향해 힘차게 솟구쳐 오르리\n\n[Verse 3]\n눈물로 씨를 뿌리는 자는 정녕 기쁨의 단을 거두며 돌아오게 되리라는 약속의 말씀을 붙드네\n마지막 승리의 날 주님 앞에 서는 그 영광스러운 순간까지 믿음의 선한 경주를 멈추지 않으리\n내게 맡겨진 십자가 기쁘게 지고 묵묵히 저 좁은 생명의 길을 끝까지 걸어가며\n영원한 하나님 나라의 소망을 온 세상 만방에 담대히 전파하며 주와 함께 살아가리\n\n[Final Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해""" + ending_tags

            # [프롬프트] 700~1000자 기술적 묘사
            s_info = SESSION_MAP.get(main_inst, "")
            p_style = f"Music Composition Style: A professional high-fidelity {genre} track for {target}. Mood: {lyric_mood}, Atmosphere: {song_atm}. Tempo: {tempo}. "
            p_vocal = f"Vocal Directives: Feature a {vocal_style} lead {v_type} vocal with 24-bit studio clarity. Deep emotional resonance. "
            p_inst = f"Instrumentation: Lead {main_inst} with supporting session: {s_info}. Wide immersive soundstage, balanced mastering. "
            p_tech = "Engineering: Warm analog saturation, silky highs, no digital clipping. Long 3-8 minute cinematic flow. "
            p_end = f"Constraint: { 'CRITICAL: NO looping. MUST end in silence after [END].' if strict_end else 'Natural end.' } "
            p_detail = f"Narrative: Build tension during the bridge for '{subject}' and resolve into a grand celebratory finale. Every note must serve the theme."
            st.session_state.res_prompt = (p_style + p_vocal + p_inst + p_tech + p_end + p_detail).strip()[:1000]

    # --- 출력 영역 (render_tab1 내부) ---
    if st.session_state.get('res_title'):
        st.subheader("🏷️ 생성 제목 (한글_영어제목)")
        st.code(st.session_state.res_title, language="text")
        st.divider()
        st.subheader("📝 곡 가사 (즉시 수정 및 편집)")
        st.text_area("Lyric Box", value=st.session_state.res_lyrics, key="lyrics_final_view", label_visibility="collapsed")
        if st.button("📋 가사 복사"):
            st.code(st.session_state.res_lyrics, language="text")
        st.divider()
        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
        st.text_area("Prompt Box", value=st.session_state.res_prompt, height=600, key="prompt_final_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_prompt, language="text")
        
        # --- [이동 버튼] ---
        st.divider()
        st.subheader("🏁 다음 단계로 바로 가기")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎨 2. 이미지 생성 탭으로 이동", use_container_width=True):
                st.info("상단의 '2. 이미지 생성' 탭을 클릭하거나 페이지를 새로고침 하세요.")
        with c2:
            if st.button("🎬 3. 영상 렌더링 탭으로 이동", use_container_width=True):
                st.info("상단의 '3. 영상 렌더링' 탭을 클릭하거나 페이지를 새로고침 하세요.")
    else:
        st.info("👈 왼쪽 설정 후 생성 버튼을 눌러주세요.")
