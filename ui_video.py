import streamlit as st
import os
import utils
from moviepy.editor import AudioFileClip
import moviepy.audio.fx.all as afx

def render_tab3():
    st.header("🎬 비디오 렌더링 & 업로드")
    aud = st.file_uploader("🎧 음원", type=['mp3','wav'])
    
    col1, col2 = st.columns(2)
    with col1:
        gen_m = st.checkbox("📺 메인 가로")
        img_m = st.file_uploader("메인 이미지", type=['png','jpg']) if gen_m else None
    with col2:
        gen_t = st.checkbox("📱 틱톡 세로")
        img_t = st.file_uploader("틱톡 이미지", type=['png','jpg']) if gen_t else None
        
    num_s = st.slider("✂️ 쇼츠 개수", 0, 6, 0)
    img_s = [st.file_uploader(f"쇼츠 {i+1}", type=['png','jpg'], key=f"v_s_{i}") for i in range(num_s)]
    
    lyr = st.text_area("📝 가사", value=st.session_state.get('gen_lyrics', ''))
    sync = st.text_input("⏱️ 시작 싱크 (예: 00:08)")

    if st.button("🚀 렌더링 시작", type="primary"):
        # 로직 시작
        audio_path = "temp_aud.wav"; open(audio_path, "wb").write(aud.getbuffer())
        full_aud = AudioFileClip(audio_path)
        start_s = utils.parse_time_to_sec(sync) if sync else utils.analyze_audio_start(full_aud)
        
        pb = st.progress(0); pt = st.empty()
        
        if gen_m:
            utils.process_user_image(img_m, 1280, 720, "m.png")
            utils.generate_video_with_lyrics("m.png", full_aud, lyr, "main.mp4", utils.StreamlitProgressLogger(pb, pt, "메인"), 1280, 720, start_s)
            st.session_state.main_video_path = "main.mp4"
            
        if gen_t:
            utils.process_user_image(img_t, 720, 1280, "t.png")
            utils.generate_video_with_lyrics("t.png", full_aud, lyr, "tiktok.mp4", utils.StreamlitProgressLogger(pb, pt, "틱톡"), 720, 1280, start_s)
            st.session_state.tiktok_video_path = "tiktok.mp4"

        # 쇼츠는 하이라이트 분석 및 렌더링 (생략 - utils 함수 사용)
        st.session_state.is_completed = True
        st.success("✅ 완료!")