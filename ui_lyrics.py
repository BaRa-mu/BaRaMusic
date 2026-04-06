import streamlit as st
import google.generativeai as genai
import utils
import re

def render_tab1():
    st.header("📝 수노(Suno AI) 가사 & 프롬프트 팩토리")
    api_key = st.text_input("🔑 구글 Gemini API 키", type="password")
    subject = st.text_input("🎯 주제")
    
    col1, col2 = st.columns(2)
    with col1: s_pop = st.selectbox("🎧 대중음악", utils.suno_pop_list)
    with col2: s_ccm = st.selectbox("⛪ CCM", utils.suno_ccm_list)
    
    if st.button("🚀 생성 시작", type="primary"):
        if not api_key or not subject: st.error("키와 주제를 입력하세요."); return
        genai.configure(api_key=api_key)
        
        # 주신 모델 리스트를 순서대로 시도
        models = ['models/gemini-2.0-flash', 'models/gemini-2.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.5-flash']
        res_text = ""
        for m_name in models:
            try:
                model = genai.GenerativeModel(m_name)
                res = model.generate_content(f"Topic: {subject}, Genre: {s_pop if s_pop!='선택안함' else s_ccm}. 한글제목, 영문제목, 1000자 영문 프롬프트, [Intro]등 태그 포함된 장문의 가사를 아래 태그로 구분해서 써줘. [TITLE_KR], [TITLE_EN], [PROMPT], [LYRICS]")
                res_text = res.text; break
            except: continue
        
        if not res_text: st.error("지원되는 모델이 없거나 키가 잘못되었습니다."); return
        
        # 파싱
        try:
            st.session_state.gen_title_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip()
            st.session_state.gen_title_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip()
            st.session_state.gen_prompt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip()
            st.session_state.gen_lyrics = res_text.split("[LYRICS]")[1].strip()
            st.success("✅ 생성 완료!")
        except: st.write(res_text)

    # 복사존
    if 'gen_title_kr' in st.session_state:
        st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}", label="제목")
        st.code(st.session_state.gen_prompt, label="프롬프트")
        st.code(st.session_state.gen_lyrics, label="가사")