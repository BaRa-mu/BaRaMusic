import streamlit as st

# [데이터 영역: 절대 수정 금지]
MOODS = {
    "CCM": ["경배와 찬양", "깊은 묵상", "회개와 눈물", "헌신과 소명", "십자가의 사랑", "성령의 임재", "소망과 위로", "경배와 영광", "제자의 길", "중보와 간구", "은혜의 강가", "어린이의 마음", "새벽의 기도", "광야의 외침", "소망의 노래", "영광의 보좌", "치유의 광선"],
    "대중음악": ["애절한 이별", "설레는 첫사랑", "도시의 쓸쓸함", "청춘의 방황", "레트로 감성", "몽환적인 밤", "열정적인 도전", "따뜻한 힐링", "냉소적인 풍자", "일상의 소소함", "기억의 습작", "여행의 설렘", "비 오는 날", "아침의 싱그러움", "어른의 성장"]
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
    # 사이드바 CSS 및 상단 탭 정렬 CSS 추가
    st.markdown("""
        <style>
        /* 탭 왼쪽 위 정렬 */
        .stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }
        .block-container { padding-top: 1rem !important; }
        /* 사이드바 스타일 보존 */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] .stTextInput input { height: 38px !important; font-size: 14px !important; }
        [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label { font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px !important; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("음악 생성 설정")
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
            # [결과 잠금 로직] 제목: 한글제목_영어제목 형식 엄격 적용
            st.session_state.res_title = "영원한소망_EternalHopeOfGrace"
            
            # [가사 생성] 3분~8분 분량 확보를 위해 대형 4절 구조로 확장
            ending_tags = "\n\n[Outro]\n(Natural fade out to silence)\n[END]\n[Hard Stop]\n[Silence]"
            st.session_state.res_lyrics = f"""[Verse 1]
{subject}의 빛이 어두운 방안을 비추고
지친 내 영혼에 새로운 숨결을 불어넣네
세상의 소음 속에서도 들려오는 그 음성
나의 발걸음을 인도하시는 따스한 손길

[Chorus]
오 영원한 그 사랑 {lyric_mood}한 선율 속에
우리 모두 하나 되어 기쁨으로 노래해
{song_atm}한 리듬이 온 땅을 가득 채울 때
{subject}의 영광이 우리 삶에 피어나리

[Verse 2]
광야 같은 길을 걸어도 나는 두렵지 않네
구름 기둥과 불 기둥으로 나를 지키시니
때로는 거친 파도가 나를 덮쳐와도
바다를 가르시는 주님의 능력을 믿네

[Chorus]
오 영원한 그 사랑 {lyric_mood}한 선율 속에
우리 모두 하나 되어 기쁨으로 노래해
{song_atm}한 리듬이 온 땅을 가득 채울 때
{subject}의 영광이 우리 삶에 피어나리

[Bridge]
하늘의 문이 열리고 축복의 비가 내리네
간절한 우리의 기도가 보좌 앞에 닿을 때
치유와 회복의 역사가 지금 시작되리
소망의 닻을 내리고 흔들리지 않으리

[Verse 3]
마지막 날에 주님 앞에 서는 그 순간까지
맡겨진 소명의 길을 묵묵히 걸어가리
눈물로 씨를 뿌리는 자 기쁨으로 거두리니
약속의 땅 향해 힘차게 전진해 나가세

[Chorus]
오 영원한 그 사랑 {lyric_mood}한 선율 속에
우리 모두 하나 되어 기쁨으로 노래해
{song_atm}한 리듬이 온 땅을 가득 채울 때
{subject}의 영광이 우리 삶에 피어나리""" + ending_tags

            # 프롬프트 조합 (700~1000자 확보용)
            session_info = SESSION_MAP.get(main_inst, "Full Orchestration")
            p_style = f"A professional high-fidelity {genre} track for the {target} market. Mood: {lyric_mood}, {song_atm}. Tempo: {tempo}. Long duration composition targeted for 3-8 minutes. "
            p_vocal = f"Vocal Performance: This production features a {vocal_style} through a {v_type} lead performance. The recording requires meticulous vocal processing with high-end studio gear to achieve crystalline clarity and deep emotional resonance. Harmonies should be rich, professional, and stylistic of the {genre} tradition. "
            p_inst = f"Instrumentation and Soundstage: The arrangement is anchored by {main_inst} providing the primary harmonic and melodic foundation. This is augmented by a carefully curated session including {session_info}. The stereo field must be wide, immersive, and balanced across all frequency spectrums. "
            p_tech = "Engineering Specs: 24-bit studio quality, professional mastering with warm analog-style saturation on the low-end and silky-smooth air in the high-frequency range. Dynamic range should be carefully managed to allow the emotional bridge to soar before landing on a powerful, celebratory final chorus. "
            p_end = f"Structural Constraint: { 'CRITICAL: NO looping and NO repetition of song sections once the lyrics conclude. The track MUST end naturally and definitively into absolute silence following the [END] tag.' if strict_end else 'Standard end.' } "
            p_detail = f"Detailed Production Analysis: The arrangement for '{subject}' must prioritize a sophisticated and highly nuanced harmonic progression that resonates deeply with {target} listeners. The {main_inst} should lead with a rhythmic and lyrical foundation that integrates perfectly with the emotive {vocal_style}. The sonic environment must mirror a world-class studio recording, ensuring total absence of digital artifacts or monotonous loops. Each instrument in the {session_info} should be strategically placed within the 3D stereo field, providing a lush, immersive depth. The dynamic range should allow the emotional bridge to soar before landing on a celebratory final chorus. Care should be taken to respect {genre} foundations while injecting modern energy. The transition from the {lyric_mood} mood to the {song_atm} atmosphere must feel organic and earned. Final check: the song MUST terminate into absolute silence immediately after the concluding lyrics, ensuring a one-take, definitive performance that captures the essence of {subject} without artificial time extension. This track must maintain professional industry standards, ensuring the balance between the {main_inst} and the {v_type} vocals remains consistent throughout the mix. No additional instrumental filler should be added after the lyrics are completed. Meticulous care in the mastering stage is required to preserve the {song_atm} character while keeping the low-end punchy."
            
            full_p = (p_style + p_vocal + p_inst + p_tech + p_end + p_detail).strip()
            st.session_state.res_prompt = full_p[:1000]

    # --- [오른쪽 메인 출력 영역] ---
    if st.session_state.get('res_title'):
        # [곡 제목] 출력 및 복사 기능
        st.subheader("🏷️ 곡 제목 (한글_영어제목)")
        st.code(st.session_state.res_title, language="text")
        st.divider()
        st.subheader("📝 곡 가사 비교 및 편집")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**[생성된 원본 가사]**")
            st.markdown(f"```text\n{st.session_state.res_lyrics}\n```")
        with col_r:
            st.markdown("**[가사 수정 및 편집]**")
-           st.text_area("편집창", value=st.session_state.res_lyrics, key="lyrics_final_view", label_visibility="collapsed")
+           st.text_area("편집창", value=st.session_state.res_lyrics, key="lyrics_final_view", label_visibility="collapsed")
        if st.button("📋 가사 복사"):
            st.code(st.session_state.res_lyrics, language="text")
        st.divider()
        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
-       st.text_area("프롬프트 확인 (700~1000자)", value=st.session_state.res_prompt, height=1200, key="prompt_final_view")
+       st.text_area("프롬프트 확인 (700~1000자)", value=st.session_state.res_prompt, height=1500, key="prompt_final_view")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_prompt, language="text")
    else:
        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
