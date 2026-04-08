import streamlit as st

# [데이터 영역: 절대 수정 금지]
MOODS = {
    "CCM": ["동화같은", "직설적인", "서정적인", "웅장한", "담백한", "경쾌한", "신비로운", "따뜻한", "강렬한", "애절한", "평화로운", "거룩한", "희망찬", "비장한", "소박한"],
    "대중음악": ["동화같은", "직설적인", "서정적인", "도시적인", "복고풍의", "몽환적인", "열정적인", "감미로운", "냉소적인", "통통튀는", "아련한", "우울한", "청량한", "세련된", "투박한"]
}
CCM_GENRES = ["현대적 워십", "모던 락 찬양", "어쿠스틱 포크", "블랙 가스펠", "클래식 찬송가", "컨템포러리 찬양", "블루스 워십", "컨트리 가스펠", "콰이어 앤섬", "묵상 연주곡", "소울 찬양", "펑키 워십", "인디 포크 찬양", "보사노바 워십", "재즈 찬양", "아이리시 워십", "블루그래스 가스펠", "챔버 오케스트라 찬양", "장엄한 교향곡풍", "켈틱 워십"]
POP_GENRES = ["스탠다드 발라드", "어쿠스틱 포크", "모던 락", "블루스 팝", "소울 알앤비", "시티 팝", "펑크(Funk)", "7080 포크", "90년대 감성 발라드", "보사노바 팝", "정통 재즈", "스윙 재즈", "라틴 팝", "탱고", "칸초네", "샹송", "챔버 팝", "모던 포크", "컨트리 팝", "재즈 발라드"]
SONG_ATMOSPHERES = ["밝고 희망찬", "차분하고 정적인", "웅장하고 힘있는", "슬프고 서정적인", "몽환적이고 신비로운", "긴박하고 긴장된", "따뜻하고 포근한", "거칠고 날카로운", "우아하고 고전적인", "애절하고 가슴아픈", "담백하고 소박한", "세련되고 도시적인", "목가적이고 평화로운", "장엄하고 거룩한", "신나고 에너제틱한"]
VOCALS = {
    "남성": ["허스키하며 애절한 저음 남성", "맑고 투명한 미성의 고음 남성", "거칠고 파워풀한 샤우팅 락 보컬 남성", "담백하고 절제된 감성의 포크 보컬 남성", "호소력 짙고 비브라토가 깊은 발라드 남성", "속삭이는 듯 공기 반 소리 반의 감성 남성", "성량이 풍부하고 웅장한 바리톤 남성", "리듬감이 좋고 비음이 섞인 팝 보컬 남성", "소울풀하고 그루비한 R&B 보컬 남성", "정갈하고 깨끗한 성가대풍 테너 남성", "세련되고 도회적인 시티팝 보컬 남성", "묵직하고 신뢰감을 주는 중저음 남성", "날카롭고 엣지 있는 하이톤 펑크 보컬 남성", "아련하고 슬픔에 젖은 미성 보컬 남성", "에너지 넘치고 밝은 텐션의 팝 보컬 남성", "톤이 높고 섬세한 감정선의 소년미 남성", "중후하고 울림이 깊은 신사적인 보컬 남성", "블루지하고 끈적한 음색의 재즈 보컬 남성", "뮤지컬 발성으로 극적인 표현의 남성 보컬", "정통 트로트 감성의 꺾기가 있는 남성 보컬"],
    "여성": ["청아하고 이슬 같은 맑은 고음 여성", "매혹적이고 허스키한 재즈 보컬 여성", "성량이 폭발적인 소울풀 디바 여성", "가냘프고 애처로운 느낌의 미성 여성", "몽환적이고 신비로운 분위기의 음색 여성", "단단하고 힘 있는 중저음 발라드 여성", "속삭이는 듯 감미로운 보사노바 보컬 여성", "톡톡 튀고 귀여운 하이톤의 아이돌 보컬 여성", "소울이 깊고 허스키한 감성의 R&B 여성", "고전적이고 우아한 성악 발성의 소프라노 여성", "도도하고 차가운 느낌의 시티팝 보컬 여성", "따스하고 정감이 넘치는 엄마 같은 보컬 여성", "샤프하고 공격적인 톤의 락 보컬 여성", "정통 발라드에 최적화된 호소력 짙은 여성", "그루비하고 세련된 팝 재즈 보컬 여성", "투명한 감성의 인디 포크 보컬 여성", "중후한 깊이감을 가진 알토 보컬 여성", "연극적인 표현력이 풍부한 보컬 여성", "비음이 섞여 애교 섞인 감성의 보컬 여성", "민요적 울림이 있는 한국적 보컬 여성"],
    "듀엣": ["서로 다른 음색의 애틋한 남녀 듀엣", "완벽한 하모니의 동성 2인조 보컬", "서로 경쟁하듯 주고받는 강렬한 듀엣", "속삭이며 대화하는 듯한 연인 컨셉 듀엣", "웅장하고 압도적인 합창 위주의 듀엣", "메아리치듯 감정이 이어지는 연쇄적 듀엣", "소박하고 따뜻한 어쿠스틱 듀오", "톤 차이가 극명하여 대비가 확실한 듀엣", "오랜 시간 맞춰온 듯 완벽한 유니즌 듀엣", "뮤지컬 넘버 같은 극적인 전개의 듀엣", "한 명은 랩, 한 명은 보컬로 조화된 듀엣", "어른과 아이의 목소리가 섞인 세대간 듀엣", "상반된 감정을 노래하는 갈등 구조의 듀엣", "슬픈 이별 장면을 연기하는 듯한 듀엣", "밝고 희망찬 멜로디의 팝 듀오", "블루지하고 소울 넘치는 흑인 음악풍 듀엣", "담백한 기타 반주에 얹은 소박한 듀엣", "가성과 진성을 오가는 화려한 화음 듀엣", "전통적인 찬송가풍의 남녀 화답 듀엣", "세련된 비트 위의 도회적인 감성 듀엣"]
}
INSTRUMENTS = ["신디사이저", "그랜드 피아노", "어쿠스틱 기타", "일렉 기타", "첼로", "바이올린", "하프", "플룻", "파이프 오르간", "우쿨렐레", "색소폰"]
SESSION_MAP = {"신디사이저": "아르페지에이터 시퀀스, 딥 베이스 신스, 공간감 있는 앰비언트 패드, 리버브 드럼", "그랜드 피아노": "바이올린 섹션, 부드러운 패드, 콘트라베이스", "어쿠스틱 기타": "카혼, 젬베, 쉐이커, 가벼운 베이스", "일렉 기타": "드럼 세트, 락 베이스, 신디사이저", "첼로": "피아노 반주, 비올라, 소프라노 스트링", "바이올린": "하프 오케스트레이션, 팀파니, 첼로", "하프": "플룻, 윈드 차임, 앰비언트 패드", "플룻": "어쿠스틱 기타, 가벼운 퍼커션", "파이프 오르간": "브라스 섹션, 콰이어(합창), 오케스트라 드럼", "우쿨렐레": "쉐이커, 우드블록, 가벼운 어쿠스틱 베이스", "색소폰": "재즈 드럼, 업라이트 베이스, 일렉 피아노"}

def render_tab1():
    # CSS 정렬 및 강제 높이 설정
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }
        .block-container { padding-top: 1rem !important; }
        div[data-baseweb="textarea"] textarea { min-height: 1200px !important; font-size: 16px !important; line-height: 1.6 !important; }
        [data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] .stTextInput input { height: 38px !important; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🎵 음악 생성 설정")
        subject = st.text_input("💡 곡 주제", key="l_subject")
        target = st.radio("🎯 타깃 설정", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        lyric_mood = st.selectbox(f"✨ {target} 가사 분위기", MOODS[target], key="mood_sel")
        genre = st.selectbox(f"🎸 {target} 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
        song_atm = st.selectbox("🌈 곡 분위기 상세", SONG_ATMOSPHERES, key="song_atm_sel")
        tempo = st.select_slider("⏱️ 템포", options=["매우 느림", "느림", "보통", "빠름", "매우 빠름"], value="보통")
        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
        vocal_style = st.selectbox(f"🗣️ {v_type} 스타일 상세", VOCALS[v_type], key="v_style_sel")
        main_inst = st.selectbox("🎹 메인 악기 선택", INSTRUMENTS, key="inst_sel")
        st.divider()
        strict_end = st.checkbox("가사 종료 시 즉시 곡 종료", value=True, key="strict_end_check")

        if st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True):
            st.session_state.res_title = f"{subject}_Divine_Grace_Visions"
            
            ending_tags = "\n\n[Outro]\n(Natural fade out to silence)\n[END]\n[Hard Stop]\n[Silence]"
            st.session_state.res_lyrics = f"""[Verse 1]\n{subject}의 깊은 향기가 새벽 안개를 뚫고 내 영혼의 가장 깊은 곳에 스며드네\n캄캄한 어둠의 긴 터널을 지나 우리에게 찾아온 찬란하고 눈부신 소망의 빛줄기 하나\n세상의 무거운 짐을 모두 내려놓고 주님의 넓고 따뜻한 품에 고요히 안기어\n평안한 안식 속에 새로운 생명의 꿈을 꾸게 하시는 은혜의 세밀한 손길\n\n[Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해\n{song_atm}한 리듬이 우리 심장을 뜨겁게 울리며 닫혔던 하늘 문을 활짝 열어줄 때\n{subject}의 놀라운 축복이 마르지 않는 강물처럼 우리 삶에 넘치도록 흐르리\n\n[Verse 2]\n메마른 광야 길을 걷다 지쳐 쓰러질 때도 생명수의 샘물은 결코 마르지 않네\n낮에는 구름 기둥으로 밤에는 불 기둥으로 우리의 모든 앞길을 한 치 오차 없이 인도하시니\n거친 파도가 휘몰아치고 폭풍우가 날 덮쳐와도 흔들리지 않는 견고한 반석 같은 믿음으로\n약속의 땅, 젖과 꿀이 흐르는 그 아름다운 곳을 향해 우린 담대히 한 걸음씩 나아가리라\n\n[Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해\n{song_atm}한 리듬이 우리 심장을 뜨겁게 울리며 닫혔던 하늘 문을 활짝 열어줄 때\n{subject}의 놀라운 축복이 마르지 않는 강물처럼 우리 삶에 넘치도록 흐르리\n\n[Bridge]\n하늘 문이 활짝 열리고 영광의 찬란한 광채가 이 낮고 천한 땅 위를 가득 비추네\n상처 입은 모든 영혼들이 주님의 따스한 손길로 치유받고 온전히 회복되는 역사의 현장\n간절한 기도의 향연이 금향로에 담겨 보좌 앞에 가장 향기롭게 상달될 때\n우리의 영혼은 독수리 날개 치며 저 높은 푸른 창공을 향해 힘차게 솟구쳐 오르리\n\n[Verse 3]\n눈물로 씨를 뿌리는 자는 정녕 기쁨의 단을 거두며 돌아오게 되리라는 약속의 말씀을 붙드네\n마지막 승리의 날 주님 앞에 서는 그 영광스러운 순간까지 믿음의 선한 경주를 멈추지 않으리\n내게 맡겨진 십자가 기쁘게 지고 묵묵히 저 좁은 생명의 길을 끝까지 걸어가며\n영원한 하나님 나라의 소망을 온 세상 만방에 담대히 전파하며 주와 함께 살아가리\n\n[Final Chorus]\n오 영원히 변치 않는 그 이름 {lyric_mood}한 찬양의 선율 속에 내 모든 진심을 실어보내리\n온 땅과 하늘이 하나 되어 소리 높여 주의 거룩하고 위대하신 이름을 목놓아 노래해\n{song_atm}한 리듬이 우리 심장을 뜨겁게 울리며 닫혔던 하늘 문을 활짝 열어줄 때\n{subject}의 놀라운 축복이 마르지 않는 강물처럼 우리 삶에 넘치도록 흐르리""" + ending_tags

            session_info = SESSION_MAP.get(main_inst, "Full Orchestration")
            p_style = f"Music Composition Style: A professional high-fidelity {genre} track meticulously produced for the {target} market. The sonic landscape is characterized by a {lyric_mood} narrative depth combined with a {song_atm} atmosphere. Tempo: {tempo}. "
            p_vocal = f"Vocal Directives: Feature a {vocal_style} through a lead {v_type} vocal arrangement. Requires advanced studio processing for crystalline clarity and deep resonance. Harmonies should be rich and professional. "
            p_inst = f"Instrumentation: Driven by {main_inst} as the melodic guide, supported by {session_info}. The stereo field must be wide, immersive, and balanced across all frequency spectrums for a radio-ready finish. "
            p_tech = "Engineering Standards: 24-bit studio quality, warm analog saturation on the low end, and silky-smooth air in the highs. Expressive dynamic range from intimate verses to celebratory choruses. No digital clipping. "
            p_end = f"Constraint: { 'CRITICAL: NO looping or repetition after the final lyric. MUST end in absolute silence after [END].' if strict_end else 'Standard natural fade.' } "
            p_detail = f"Narrative Arc: The arrangement for '{subject}' must feel like a 3-8 minute cinematic journey. Build tension during the bridge and resolve into a grand celebratory finale. Every note must serve the theme of '{subject}' without artificial time padding."
            st.session_state.res_prompt = (p_style + p_vocal + p_inst + p_tech + p_end + p_detail).strip()[:1000]

    # --- [출력 영역: 함수 내부] ---
    if st.session_state.get('res_title'):
        st.subheader("🏷️ 생성 곡 제목 (한글_영어제목)")
        st.code(st.session_state.res_title, language="text")
        st.divider()
        st.subheader("📝 생성 가사 (즉시 수정 및 편집 가능)")
        st.text_area("Lyric Box", value=st.session_state.res_lyrics, key="lyrics_final_view", label_visibility="collapsed")
        if st.button("📋 가사 전체 복사"):
            st.code(st.session_state.res_lyrics, language="text")
        st.divider()
        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
        st.text_area("Prompt Box", value=st.session_state.res_prompt, height=600, key="prompt_final_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_prompt, language="text")
        st.divider()
        st.subheader("🏁 다음 단계로 이동")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎨 2. 이미지 생성으로 이동", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()
        with col2:
            if st.button("🎬 3. 영상 렌더링으로 이동", use_container_width=True):
                st.session_state.active_tab = 2
                st.rerun()
    else:
        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
