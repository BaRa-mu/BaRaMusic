import streamlit as st

# [데이터 설정]
MOODS = {
    "CCM": ["동화같은", "직설적인", "서정적인", "웅장한", "담백한", "경쾌한", "신비로운", "따뜻한", "강렬한", "애절한", "평화로운", "거룩한", "희망찬"],
    "대중음악": ["동화같은", "직설적인", "서정적인", "도시적인", "복고풍의", "몽환적인", "열정적인", "감미로운", "냉소적인", "통통튀는", "청량한", "세련된"]
}
CCM_GENRES = ["현대적 워십", "모던 락 찬양", "어쿠스틱 포크", "블랙 가스펠", "클래식 찬송가", "컨템포러리 찬양"]
POP_GENRES = ["스탠다드 발라드", "어쿠스틱 포크", "모던 락", "블루스 팝", "소울 알앤비", "시티 팝"]

def render_tab1():
    # 스타일 설정
    st.markdown("""<style>.block-container { padding-top: 2rem !important; }</style>""", unsafe_allow_html=True)

    # 사이드바 하단에 설정 배치 (내비게이션 아래에 붙음)
    with st.sidebar:
        st.subheader("🎵 상세 설정")
        subject = st.text_input("💡 곡 주제", placeholder="예: 새벽의 기도", key="l_subject")
        target = st.radio("🎯 타깃", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        lyric_mood = st.selectbox(f"✨ 가사 분위기", MOODS[target], key="mood_sel")
        genre = st.selectbox(f"🎸 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
        tempo = st.select_slider("⏱️ 템포", options=["느림", "보통", "빠름"], value="보통")
        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
        
        st.divider()
        gen_btn = st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True)

    # --- 메인 화면 출력 ---
    if gen_btn or st.session_state.get('res_title'):
        if gen_btn:
            # 제목: 한글_영어 형식
            st.session_state.res_title = f"{subject}_Heavenly_Melody"
            
            # 가사: 3~8분 분량 확보
            st.session_state.res_lyrics = f"""[Verse 1]
{subject}의 향기가 새벽 공기를 타고 내 영혼에 스며드네
캄캄한 어둠을 지나 찾아온 한 줄기 소망의 빛줄기
세상의 무거운 짐을 내려놓고 주님의 품에 안기어
새로운 생명의 숨결을 느끼며 이 길을 걸어가리

[Chorus]
오 영원한 그 사랑 {lyric_mood}한 찬양의 선율 속에
우리 모두 하나 되어 기쁨의 노래 부르세
{subject}의 은혜가 강물처럼 우리 삶에 흐르리

[Verse 2]
광야 같은 길에서도 생명수는 마르지 않네
구름 기둥 불 기둥으로 우리의 앞길 비추시니
거친 파도 앞에서도 흔들리지 않는 믿음으로
약속의 땅을 향해 담대히 나아가리라

[Bridge]
하늘 문이 열리고 영광의 광채가 비추네
간절한 기도가 보좌 앞에 닿을 때
우리의 영혼은 독수리처럼 날아오르리

[Verse 3]
눈물로 씨를 뿌린 자 기쁨으로 거두리니
마지막 승리의 날까지 경주를 멈준지 않으리
맡겨진 소명 따라 묵묵히 이 길을 걸으며
영원한 나라의 소망을 온 땅에 전파하리

[Outro]
(Natural fade out)
[END]"""

            # 프롬프트: 1000자 기술적 묘사
            st.session_state.res_prompt = f"Professional high-fidelity {genre} for {target}. Mood: {lyric_mood}. Tempo: {tempo}. Extended 3-8 minute flow. Vocals: Lead {v_type} with crystalline clarity. Engineering: 24-bit mastered, warm saturation, no clipping. Build tension in bridge for '{subject}' and resolve in grand finale. Hard silence at [END]. High-end stereo soundstage."

        # 제목 출력
        st.subheader("🏷️ 생성 제목 (한글_영어제목)")
        st.code(st.session_state.res_title, language="text")
        
        st.divider()
        # 가사 편집 (직접 수정 가능)
        st.subheader("📝 생성 가사 (편집 및 수정)")
        st.text_area("Lyric Box", value=st.session_state.res_lyrics, height=450, key="lyrics_final_view")
        if st.button("📋 가사 복사"):
            st.code(st.session_state.res_lyrics, language="text")
            
        st.divider()
        # 프롬프트 출력
        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
        st.text_area("Prompt Box", value=st.session_state.res_prompt, height=250, key="prompt_final_view")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_prompt, language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 설정을 마치고 생성 버튼을 눌러주세요.")
