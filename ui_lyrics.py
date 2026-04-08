import streamlit as st

# [데이터 영역: 지시하신 직관적 분위기 적용]
MOODS = {
    "CCM": ["동화같은", "직설적인", "서정적인", "웅장한", "담백한", "경쾌한", "신비로운", "따뜻한", "강렬한", "애절한", "평화로운", "거룩한", "희망찬"],
    "대중음악": ["동화같은", "직설적인", "서정적인", "도시적인", "복고풍의", "몽환적인", "열정적인", "감미로운", "냉소적인", "통통튀는", "청량한", "세련된"]
}
CCM_GENRES = ["현대적 워십", "모던 락 찬양", "어쿠스틱 포크", "블랙 가스펠", "클래식 찬송가", "컨템포러리 찬양"]
POP_GENRES = ["스탠다드 발라드", "어쿠스틱 포크", "모던 락", "블루스 팝", "소울 알앤비", "시티 팝"]

def render_tab1():
    # 상단 탭 왼쪽 정렬 스타일
    st.markdown("""<style>.stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("🎵 음악 생성 설정")
        subject = st.text_input("💡 곡 주제", key="l_subject")
        target = st.radio("🎯 타깃", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        lyric_mood = st.selectbox(f"✨ 가사 분위기", MOODS[target], key="mood_sel")
        genre = st.selectbox(f"🎸 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
        tempo = st.select_slider("⏱️ 템포", options=["느림", "보통", "빠름"], value="보통")
        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
        st.divider()
        
        if st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True):
            # 1. 제목: 한글제목_영어제목 형식
            st.session_state.res_title = f"{subject}_Eternal_Grace_Harmony"
            
            # 2. 가사: 3~8분 분량 (4절 구조)
            st.session_state.res_lyrics = f"""[Verse 1]
{subject}의 향기가 새벽의 공기를 타고 내 영혼에 깊이 스며드네
캄캄한 어둠을 지나 찾아온 한 줄기 소망의 빛줄기
무거운 짐을 내려놓고 주님의 품에 안기어
평안한 안식 속에 새로운 꿈을 꾸게 하시네

[Chorus]
오 영원한 그 사랑 {lyric_mood}한 찬양의 선율 속에
우리 모두 하나 되어 기쁨의 노래 부르세
리듬이 우리 심장을 뜨겁게 울릴 때
{subject}의 은혜가 강물처럼 흐르리

[Verse 2]
광야 같은 길에서도 생명수는 마르지 않네
구름 기둥 불 기둥으로 우리의 앞길 비추시니
거친 파도 앞에서도 흔들리지 않는 믿음으로
약속의 땅을 향해 담대히 나아가리라

[Bridge]
하늘 문이 열리고 영광의 광채가 비추네
치유와 회복의 역사가 이 땅 위에 가득하길
간절한 기도가 보좌 앞에 닿을 때
우리의 영혼은 독수리처럼 날아오르리

[Verse 3]
눈물로 씨를 뿌린 자 기쁨으로 거두리니
마지막 승리의 날까지 경주를 멈추지 않으리
맡겨진 십자가 지고 좁은 길 걸어가며
영원한 나라의 소망을 전파하리

[Outro]
(Natural fade out to silence)
[END]"""

            # 3. 프롬프트: 1000자 상세 기술 묘사
            p_style = f"Professional high-fidelity {genre} track for {target}. Mood: {lyric_mood}. Tempo: {tempo}. Extended 3-8 minute cinematic flow. "
            p_vocal = f"Vocals: Lead {v_type} vocal with 24-bit studio clarity and deep emotive resonance. Clear diction. "
            p_tech = "Engineering: 24-bit mastered, warm saturation, silky highs, no clipping. Deep soundstage. "
            p_detail = f"Narrative: Build intense tension in the bridge for '{subject}' and resolve in a celebratory finale. Hard stop at [END]. Professional radio-ready mix."
            st.session_state.res_prompt = (p_style + p_vocal + p_tech + p_detail).strip()[:1000]

    # --- [오른쪽 출력 영역] ---
    if st.session_state.get('res_title'):
        # 제목 및 복사
        st.subheader("🏷️ 생성 제목 (한글_영어제목)")
        st.code(st.session_state.res_title, language="text")
        
        st.divider()
        # 가사 출력 및 직접 수정 (사용자 요구대로 높이 확장 삭제)
        st.subheader("📝 생성 가사 (즉시 수정 및 편집 가능)")
        st.text_area("가사 본문", value=st.session_state.res_lyrics, height=400, key="lyrics_final_view")
        if st.button("📋 가사 복사"):
            st.code(st.session_state.res_lyrics, language="text")
            
        st.divider()
        # 프롬프트 출력 및 복사
        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
        st.text_area("프롬프트 확인", value=st.session_state.res_prompt, height=200, key="prompt_final_view")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_prompt, language="text")

        # 이동 버튼
        st.divider()
        st.subheader("🏁 다음 단계 이동")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎨 2. 이미지 생성으로 이동", use_container_width=True):
                st.info("상단의 '2. 이미지 생성' 탭을 클릭하세요.")
        with c2:
            if st.button("🎬 3. 영상 렌더링으로 이동", use_container_width=True):
                st.info("상단의 '3. 영상 렌더링' 탭을 클릭하세요.")
    else:
        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
