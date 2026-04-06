import streamlit as st
import re
import google.generativeai as genai
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    user_api_key = st.text_input("🔑 구글 Gemini API 키", type="password")
    subject = st.text_input("🎯 곡의 주제/메시지 (예: 지친 하루의 위로, 십자가의 사랑)")
    
    col1, col2 = st.columns(2)
    with col1: s_pop = st.selectbox("🎧 대중음악", utils.suno_pop_list)
    with col2: s_ccm = st.selectbox("⛪ CCM", utils.suno_ccm_list)

    col3, col4, col5, col6 = st.columns(4)
    with col3: s_mood = st.selectbox("✨ 분위기", utils.suno_moods_list)
    with col4: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
    with col5: s_inst = st.selectbox("🎸 악기", utils.suno_inst_list)
    with col6: s_vocal = st.selectbox("🎤 보컬", utils.suno_vocals_list)

    if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
        if not user_api_key or not subject: 
            st.error("키와 주제를 입력하세요.")
            return
            
        genai.configure(api_key=user_api_key)
        
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_models = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash', 'models/gemini-pro']
            valid_models = [m for m in target_models if m in available_models]
            
            style_parts = []
            if s_pop != '선택안함': style_parts.append(f"Genre: {s_pop}")
            if s_ccm != '선택안함': style_parts.append(f"CCM: {s_ccm}")
            if s_mood != '선택안함': style_parts.append(f"Mood: {s_mood}")
            if s_tempo != '선택안함': style_parts.append(f"Tempo: {s_tempo}")
            if s_inst != '선택안함': style_parts.append(f"Instruments: {s_inst}")
            if s_vocal != '선택안함': style_parts.append(f"Vocals: {s_vocal}")
            style_prompt = ", ".join(style_parts) if style_parts else "Any style"
            
            query = f"""You are a professional award-winning lyricist. Topic: {subject}, Style: {style_prompt}. 
            Output EXACTLY 4 sections with these tags: [TITLE_KR], [TITLE_EN], [PROMPT], [LYRICS]. 
            Prompt must be English, 800-1000 chars, extremely detailed. Lyrics must be long, deep Korean poetry with structure tags."""
            
            with st.spinner("AI가 데이터를 생성 중..."):
                res_text = ""
                for m_name in valid_models:
                    try:
                        model = genai.GenerativeModel(m_name)
                        res = model.generate_content(query)
                        res_text = res.text
                        break
                    except: 
                        continue
                
                if not res_text: 
                    st.error("생성 실패.")
                    return
                
                st.session_state.gen_title_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip().replace('"','')
                st.session_state.gen_title_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip().replace('"','')
                st.session_state.gen_prompt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip().replace("\n"," ")[:995]
                st.session_state.gen_lyrics = res_text.split("[LYRICS]")[1].strip()
                st.success("✅ 생성 완료!")
                
        except Exception as e: 
            st.error(f"오류: {e}")

    if st.session_state.get('gen_title_kr'):
        st.divider()
        st.write("**1. 🎵 Title (한글_영어)**")
        st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
        st.write("**2. 🎸 Style of Music (프롬프트)**")
        st.code(st.session_state.gen_prompt)
        st.write("**3. 📝 Lyrics (가사)**")
        st.code(st.session_state.gen_lyrics)