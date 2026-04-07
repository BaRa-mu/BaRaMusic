import streamlit as st
import utils

def render_tab1():
    st.header("📝 가사 및 프롬프트 기획")
    
    with st.form("lyrics_detail_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            genre = st.selectbox("음악 장르", ["CCM", "자장가", "워십", "클래식", "국악"])
            mood = st.selectbox("곡의 분위기", ["평안한", "웅장한", "슬픈", "밝은", "잔잔한"])
        with col2:
            target = st.selectbox("청취 대상", ["전체", "아기", "지친 영혼", "환우", "청년"])
            tempo = st.selectbox("템포", ["매우 느리게", "느리게", "보통", "약간 빠르게"])
        with col3:
            language = st.selectbox("언어", ["한국어", "영어", "한국어/영어 혼용"])
            verse_count = st.slider("절 구성", 1, 4, 2)
            
        keywords = st.text_input("핵심 키워드 (쉼표 구분)", "은혜, 안식, 주님")
        theme_details = st.text_area("상세 주제 내용", "고단한 하루를 마치고 주님 안에서 참된 평안을 얻는 밤")
        
        submit_btn = st.form_submit_button("✨ 곡 정보 생성 (제목/가사/프롬프트)", type="primary")

    if submit_btn:
        with st.spinner("AI가 상세 기획안을 작성 중입니다..."):
            # 입력값 취합
            query = f"{genre} {mood} {target} {tempo} {language} {verse_count}절 키워드:{keywords} 주제:{theme_details}"
            title, prompt, lyrics = utils.generate_all_text(query)
            
            st.session_state.title = title
            st.session_state.prompt = prompt
            st.session_state.lyrics = lyrics

    # 결과물 출력 (바로 복사 가능하도록 구성)
    if "title" in st.session_state:
        st.divider()
        st.subheader("📌 생성된 기획안 (수정/복사 가능)")
        st.text_input("🎵 최종 제목", st.session_state.title)
        st.text_area("🎨 이미지 생성용 프롬프트", st.session_state.prompt, height=80)
        st.text_area("🎤 전체 가사", st.session_state.lyrics, height=350)