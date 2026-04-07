import streamlit as st
import utils

def render_tab1():
    # --- [변경사항: 구글 API 키 제거 및 무료 연동 UI 구축] ---
    st.header("📝 수노(Suno AI) 완벽 프롬프트 생성기 (무료 연동)")
    subject = st.text_input("🎯 곡의 주제/메시지 (예: 지친 하루의 위로, 십자가의 사랑)")
    
    col1, col2 = st.columns(2)
    with col1: s_pop = st.selectbox("🎧 대중음악", utils.suno_pop_list)
    with col2: s_ccm = st.selectbox("⛪ CCM", utils.suno_ccm_list)

    col3, col4, col5, col6 = st.columns(4)
    with col3: s_mood = st.selectbox("✨ 분위기", utils.suno_moods_list)
    with col4: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
    with col5: s_inst = st.selectbox("🎸 악기", utils.suno_inst_list)
    with col6: s_vocal = st.selectbox("🎤 보컬", utils.suno_vocals_list)

    if st.button("🚀 프롬프트 생성 및 무료 AI 연결", type="primary", use_container_width=True):
        if not subject: 
            st.error("주제를 입력하세요.")
            return
            
        style_parts = []
        if s_pop != '선택안함': style_parts.append(f"Genre: {s_pop}")
        if s_ccm != '선택안함': style_parts.append(f"CCM: {s_ccm}")
        if s_mood != '선택안함': style_parts.append(f"Mood: {s_mood}")
        if s_tempo != '선택안함': style_parts.append(f"Tempo: {s_tempo}")
        if s_inst != '선택안함': style_parts.append(f"Instruments: {s_inst}")
        if s_vocal != '선택안함': style_parts.append(f"Vocals: {s_vocal}")
        style_prompt = ", ".join(style_parts) if style_parts else "Any style"
        
        prompt_text = f"""You are a professional award-winning lyricist. 
Topic: {subject}
Style: {style_prompt}

Output EXACTLY 4 sections with these tags: [TITLE_KR], [TITLE_EN], [PROMPT], [LYRICS].
Prompt must be English, 800-1000 chars, extremely detailed. 
Lyrics must be long, deep Korean poetry with structure tags like [Verse], [Chorus]."""
        
        st.session_state.master_prompt = prompt_text
        st.success("✅ 완벽한 프롬프트가 생성되었습니다. 아래 텍스트를 복사하여 무료 AI에 붙여넣으세요.")

    if st.session_state.get('master_prompt'):
        st.code(st.session_state.master_prompt, language="markdown")
        
        st.divider()
        st.subheader("🔗 무료 AI 서비스로 이동 (복사한 프롬프트를 붙여넣으세요)")
        col_a, col_b, col_c = st.columns(3)
        with col_a: st.link_button("🤖 ChatGPT (무료)", "https://chatgpt.com", use_container_width=True)
        with col_b: st.link_button("🧠 Claude (무료)", "https://claude.ai", use_container_width=True)
        with col_c: st.link_button("🎵 Suno AI (음악 생성)", "https://suno.com", use_container_width=True)
        
        st.info("💡 외부 AI에서 생성된 결과물에서 제목([TITLE_KR], [TITLE_EN])과 가사([LYRICS])를 복사하여 다음 단계에서 활용하십시오.")
    # ---------------------------------------------------------------------------------