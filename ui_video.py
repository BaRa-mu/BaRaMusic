import streamlit as st
import os
import gc
import zipfile
import io
import utils
from moviepy.editor import AudioFileClip
from datetime import datetime, timedelta, timezone

def render_tab3():
    st.header("🎬 비디오 렌더링 & 유튜브 업로드")
    aud = st.file_uploader("🎧 음원 파일", type=['mp3','wav'])
    
    col1, col2 = st.columns(2)
    with col1:
        gen_m = st.checkbox("📺 가로 메인"); img_m = st.file_uploader("메인 이미지 (16:9)", type=['png','jpg']) if gen_m else None
    with col2:
        gen_t = st.checkbox("📱 세로 틱톡"); img_t = st.file_uploader("틱톡 이미지 (9:16)", type=['png','jpg']) if gen_t else None
    
    num_s = st.slider("✂️ 하이라이트 쇼츠 개수", 0, 6, 0)
    img_s = [st.file_uploader(f"쇼츠 {i+1} 이미지", type=['png','jpg'], key=f"vs_{i}") for i in range(num_s)]
    
    lyr = st.text_area("📝 가사", value=st.session_state.get('gen_lyrics', ''))
    sync = st.text_input("⏱️ 시작 싱크 (예: 00:08)", placeholder="비워두면 AI 자동 분석")

    if st.button("🚀 렌더링 시작", type="primary", use_container_width=True):
        if not aud: st.error("음원을 올려주세요."); return
        audio_path = "temp_v.wav"; open(audio_path, "wb").write(aud.getbuffer())
        full_aud = AudioFileClip(audio_path); start_s = utils.parse_time_to_sec(sync) if sync else utils.analyze_audio_start(full_aud)
        pb = st.progress(0); pt = st.empty()
        
        if gen_m:
            utils.generate_video_with_lyrics(utils.design_and_save_image(1280, 720, "", 0, "", "", "나눔고딕 (기본/깔끔)", 0, 0, 0, "tm.png", img_m), full_aud, lyr, "main.mp4", utils.StreamlitProgressLogger(pb, pt, "메인"), 1280, 720, start_s)
            st.session_state.v_main = "main.mp4"
        if gen_t:
            utils.generate_video_with_lyrics(utils.design_and_save_image(720, 1280, "", 0, "", "", "나눔고딕 (기본/깔끔)", 0, 0, 0, "tt.png", img_t), full_aud, lyr, "tiktok.mp4", utils.StreamlitProgressLogger(pb, pt, "틱톡"), 720, 1280, start_s)
            st.session_state.v_tiktok = "tiktok.mp4"
        
        st.session_state.v_shorts = []
        if num_s > 0:
            h_times = utils.find_highlights_lite(full_aud.duration, num_s)
            for i, stime in enumerate(h_times):
                sub_a = full_aud.subclip(stime, min(stime+45, full_aud.duration))
                utils.generate_video_with_lyrics(utils.design_and_save_image(720, 1280, "", 0, "", "", "나눔고딕 (기본/깔끔)", 0, 0, 0, f"ts_{i}.png", img_s[i]), sub_a, "", f"s_{i}.mp4", utils.StreamlitProgressLogger(pb, pt, f"쇼츠{i+1}"), 720, 1280)
                st.session_state.v_shorts.append(f"s_{i}.mp4")
        
        st.session_state.is_completed = True; st.success("✅ 모든 영상 생성 완료!")

    if st.session_state.get('is_completed'):
        st.divider(); st.subheader("📦 결과물 다운로드")
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "w") as zf:
            if st.session_state.get('v_main'): zf.write(st.session_state.v_main, "Main.mp4")
            if st.session_state.get('v_tiktok'): zf.write(st.session_state.v_tiktok, "TikTok.mp4")
            for i, p in enumerate(st.session_state.get('v_shorts', [])): zf.write(p, f"Short_{i+1}.mp4")
        st.download_button("🎁 전체 영상 ZIP 다운로드", z_buf.getvalue(), "All_Videos.zip", type="primary", use_container_width=True)

        tabs = st.tabs(["📺 메인", "📱 틱톡"] + [f"✂️ 쇼츠 {i+1}" for i in range(len(st.session_state.get('v_shorts', [])))])
        with tabs[0]: 
            if st.session_state.get('v_main'): st.video(st.session_state.v_main)
        with tabs[1]:
            if st.session_state.get('v_tiktok'): 
                col_v, _ = st.columns([1, 1.5]); col_v.video(st.session_state.v_tiktok)
        
        st.divider(); st.header("🚀 유튜브 업로드")
        c1, c2 = st.columns(2)
        with c1: client_file = st.file_uploader("🔑 client_secrets.json", type=['json'])
        with c2: token_file = st.file_uploader("🎫 token.json", type=['json'])
        
        if client_file and token_file:
            with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
            with open("token.json", "wb") as f: f.write(token_file.getbuffer())
            
            yt_title = st.text_input("📝 제목", value=f"[{st.session_state.get('gen_title_kr','찬양')}] 은혜로운 찬양")
            ccm_desc = f"할렐루야! 오늘 나눌 찬양은 '{st.session_state.get('gen_title_kr','찬양')}'입니다. 🌿\n\n예배를 사모하는 모든 분들께 위로가 되길 소망합니다.\n#CCM #찬양 #예배 #은혜 #기도 #찬양추천"
            yt_desc = st.text_area("📜 설명", value=ccm_desc, height=200)
            yt_tags = st.text_input("🏷️ 태그", value="CCM, 찬양, 예배, 은혜, 기독교, 교회, 찬송가, 워십, 복음성가, 기도, 묵상")
            privacy = st.selectbox("🔒 공개설정", ["private", "unlisted", "public", "scheduled"])
            
            if st.button("🔥 유튜브 전송"):
                success, msg = utils.upload_to_youtube(st.session_state.v_main, yt_title, yt_desc, yt_tags, "private" if privacy=="scheduled" else privacy)
                if success: st.success(msg); st.balloons()
                else: st.error(msg)