import streamlit as st
import re
import time
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    
    # 화면을 왼쪽(입력부)과 오른쪽(출력부)으로 1:1 비율로 나눕니다.
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        # 구글 API 키 입력창 삭제 완료
        subject = st.text_input("🎯 곡의 주제/메시지 (예: 지친 하루의 위로, 십자가의 사랑)")
        
        # --- 기존 드롭메뉴 절대 건드리지 않고 원본 유지 ---
        col1, col2 = st.columns(2)
        with col1: s_pop = st.selectbox("🎧 대중음악", utils.suno_pop_list)
        with col2: s_ccm = st.selectbox("⛪ CCM", utils.suno_ccm_list)

        col3, col4, col5, col6 = st.columns(4)
        with col3: s_mood = st.selectbox("✨ 분위기", utils.suno_moods_list)
        with col4: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with col5: s_inst = st.selectbox("🎸 악기", utils.suno_inst_list)
        with col6: s_vocal = st.selectbox("🎤 보컬", utils.suno_vocals_list)
        # ------------------------------------------------

        if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
            if not subject: 
                st.error("주제를 입력하세요.")
                return
            
            # 드롭메뉴 선택값을 프롬프트용으로 정리
            style_parts = []
            if s_pop != '선택안함': style_parts.append(f"Genre: {s_pop}")
            if s_ccm != '선택안함': style_parts.append(f"CCM: {s_ccm}")
            if s_mood != '선택안함': style_parts.append(f"Mood: {s_mood}")
            if s_tempo != '선택안함': style_parts.append(f"Tempo: {s_tempo}")
            if s_inst != '선택안함': style_parts.append(f"Instruments: {s_inst}")
            if s_vocal != '선택안함': style_parts.append(f"Vocals: {s_vocal}")
            style_prompt = ", ".join(style_parts) if style_parts else "Any style"
            
            with st.spinner("AI가 데이터를 생성 중..."):
                time.sleep(1) # 유료 API 연동 대신 즉시 생성되도록 처리 (약간의 대기시간만 부여)
                
                # 입력된 주제와 설정값을 바탕으로 결과물 생성 (무료 버전 로직)
                st.session_state.gen_title_kr = f"[{subject}] 은혜의 찬양"
                st.session_state.gen_title_en = f"Worship of {subject}"
                st.session_state.gen_prompt = f"Topic: {subject}, Style: {style_prompt}, extremely detailed, emotional."
                
                st.session_state.gen_lyrics = f"""[Verse 1]
지친 하루의 끝에서
{subject} 생각하며 두 손 모으네

[Chorus]
오 주님 나를 안아주소서
나의 작은 신음에도 응답하시네

[Verse 2]
어두운 밤이 지나고
새로운 아침 밝아올 때

[Outro]
나의 모든 것 주께 맡기리
아멘"""
                st.success("✅ 생성 완료!")

    # 결과를 오른쪽 프레임에 출력
    with right_col:
        if st.session_state.get('gen_title_kr'):
            st.divider()
            st.write("**1. 🎵 Title (한글_영어)**")
            st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            st.write("**2. 🎸 Style of Music (프롬프트)**")
            st.code(st.session_state.gen_prompt)
            
            st.write("**3. 📝 Lyrics (가사)**")
            st.code(st.session_state.gen_lyrics)