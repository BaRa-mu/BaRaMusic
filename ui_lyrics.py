import streamlit as st
import utils

def render_tab1():
    st.header("📝 곡 정보 및 가사 생성")
    st.write("원하시는 주제나 분위기를 입력하면 제목, 이미지 프롬프트, 가사를 한 번에 생성합니다.")
    
    theme = st.text_input("주제 입력 (예: 밤에 듣기 좋은 평안한 CCM 자장가)", "평안한 밤을 위한 은혜로운 CCM 자장가")
    
    if st.button("✨ 자동 생성하기", type="primary"):
        with st.spinner("제목, 프롬프트, 가사를 생성하고 있습니다..."):
            # utils.py의 AI 생성 함수 호출
            title, prompt, lyrics = utils.generate_all_text(theme)
            
            # 세션 상태에 저장하여 화면에 유지
            st.session_state.title = title
            st.session_state.prompt = prompt
            st.session_state.lyrics = lyrics

    # 생성된 데이터가 있으면 수정 및 복사 가능한 텍스트 박스로 출력
    if "title" in st.session_state:
        st.subheader("📌 생성 결과 (자유롭게 수정/복사하세요)")
        
        st.text_input("🎵 제목", st.session_state.title, key="edit_title")
        st.text_area("🎨 이미지 프롬프트", st.session_state.prompt, key="edit_prompt", height=100)
        st.text_area("🎤 가사", st.session_state.lyrics, key="edit_lyrics", height=300)