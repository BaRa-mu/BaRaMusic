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
    lyr = st.text_area("📝 가사 (AI에서 복사한 가사를 붙여넣으세요)", height=150)
    sync = st.text_input("⏱️ 시작 싱크 (예: 00:08)", placeholder="비워두면 AI 자동 분석")
    
    st.divider()
    
    # --- [변경사항: 탭2 연동 여부 검증 및 누락 시 단독 텍스트 설정 UI 팝업 전개] ---
    def render_video_target_options(label, res_key, w, h):
        has_tab2_img = st.session_state.get(res_key) and os.path.exists(st.session_state.get(res_key))
        if has_tab2_img:
            st.success(f"✅ 이미지 탭에서 디자인된 '{label}' 이미지를 상속받아 사용합니다.")
            return st.session_state.get(res_key)
        else:
            st.info(f"💡 '{label}' 이미지가 생성되지 않았습니다. 사용할 이미지를 업로드하고 옵션을 설정하세요.")
            up_img = st.file_uploader(f"{label} 이미지 파일", type=['png','jpg'], key=f"upv_{res_key}")
            if up_img:
                with st.expander(f"🎨 {label} 텍스트 및 효과 설정", expanded=True):
                    tk = st.text_input("한글 제목", key=f"vtk_{res_key}")
                    te = st.text_input("영문 제목", key=f"vte_{res_key}")
                    c1, c2 = st.columns(2)
                    with c1: fnt = st.selectbox("글씨체", list(utils.font_links.keys()), key=f"vfnt_{res_key}")
                    with c2: fx = st.selectbox("효과", utils.effects_list, key=f"vfx_{res_key}")
                    sz = st.slider("크기", 30, 150, 60 if w>h else 45, key=f"vsz_{res_key}")
                    yp = st.slider("위치(%)", 5, 95, 15, key=f"vyp_{res_key}")
                return {"file": up_img, "tk":tk, "te":te, "fnt":fnt, "fx":fx, "sz":sz, "yp":yp, "w":w, "h":h}
            return None

    c_m, c_t = st.columns(2)
    with c_m:
        st.subheader("📺 메인 영상(16:9)")
        gen_m = st.checkbox("메인 생성", value=True)
        opt_m = render_video_target_options("메인", 'res_m', 1280, 720) if gen_m else None
    with c_t:
        st.subheader("📱 틱톡 영상(9:16)")
        gen_t = st.checkbox("틱톡 생성", value=False)
        opt_t = render_video_target_options("틱톡", 'res_t', 720, 1280) if gen_t else None

    st.subheader("✂️ 하이라이트 쇼츠(9:16)")
    num_s = st.slider("쇼츠 개수", 0, 6, 0)
    opts_s = []
    for i in range(num_s):
        opts_s.append(render_video_target_options(f"쇼츠 {i+1}", f'res_s_{i}', 720, 1280))
    # --------------------------------------------------------------------------------
    
    if st.button("🚀 렌더링 시작", type="primary", use_container_width=True):
        if not aud: 
            st.error("음원을 올려주세요.")
            return
        audio_path = "temp_v.wav"
        with open(audio_path, "wb") as f:
            f.write(aud.getbuffer())
            
        full_aud = AudioFileClip(audio_path)
        start_s = utils.parse_time_to_sec(sync) if sync else utils.analyze_audio_start(full_aud)
        pb = st.progress(0)
        pt = st.empty()
        
        # --- [변경사항: 딕셔너리로 넘어온 단독 텍스트 설정값 동적 렌더링 처리] ---
        def process_opt(opt_data, key_suffix):
            if isinstance(opt_data, str): return opt_data
            if isinstance(opt_data, dict) and opt_data["file"]:
                bg = utils.prepare_background(opt_data["w"], opt_data["h"], "", 0, f"vbg_{key_suffix}.png", opt_data["file"])
                return utils.apply_text_to_image(bg, opt_data["tk"], opt_data["te"], opt_data["fnt"], opt_data["sz"], opt_data["yp"], 15, opt_data["fx"], f"vres_{key_suffix}.png")
            return None

        final_m = process_opt(opt_m, "m") if gen_m else None
        final_t = process_opt(opt_t, "t") if gen_t else None
        final_s = [process_opt(opt, f"s_{i}") for i, opt in enumerate(opts_s)]
        # ----------------------------------------------------------------------
        
        if gen_m and final_m:
            utils.generate_video_with_lyrics(final_m, full_aud, lyr, "main.mp4", utils.StreamlitProgressLogger(pb, pt, "메인"), 1280, 720, start_s)
            st.session_state.v_main = "main.mp4"
            
        if gen_t and final_t:
            utils.generate_video_with_lyrics(final_t, full_aud, lyr, "tiktok.mp4", utils.StreamlitProgressLogger(pb, pt, "틱톡"), 720, 1280, start_s)
            st.session_state.v_tiktok = "tiktok.mp4"
        
        st.session_state.v_shorts = []
        if num_s > 0:
            h_times = utils.find_highlights_lite(full_aud.duration, num_s)
            for i, stime in enumerate(h_times):
                if not final_s[i]: continue
                sub_a = full_aud.subclip(stime, min(stime+45, full_aud.duration))
                utils.generate_video_with_lyrics(final_s[i], sub_a, "", f"s_{i}.mp4", utils.StreamlitProgressLogger(pb, pt, f"쇼츠{i+1}"), 720, 1280)
                st.session_state.v_shorts.append(f"s_{i}.mp4")
        
        st.session_state.is_completed = True
        st.success("✅ 모든 영상 생성 완료!")

    if st.session_state.get('is_completed'):
        st.divider()
        st.subheader("📦 결과물 다운로드")
        z_buf = io.BytesIO()
        with zipfile.ZipFile(z_buf, "w") as zf:
            for key, arcname in [('v_main', "Main.mp4"), ('v_tiktok', "TikTok.mp4")]:
                path = st.session_state.get(key)
                if path and os.path.exists(path):
                    zf.write(path, arcname)
            for i, p in enumerate(st.session_state.get('v_shorts', [])):
                if os.path.exists(p):
                    zf.write(p, f"Short_{i+1}.mp4")
        st.download_button("🎁 전체 영상 ZIP 다운로드", z_buf.getvalue(), "All_Videos.zip", type="primary", use_container_width=True)

        tabs = st.tabs(["📺 메인", "📱 틱톡"] + [f"✂️ 쇼츠 {i+1}" for i in range(len(st.session_state.get('v_shorts', [])))])
        with tabs[0]: 
            if st.session_state.get('v_main') and os.path.exists(st.session_state.v_main): st.video(st.session_state.v_main)
        with tabs[1]:
            if st.session_state.get('v_tiktok') and os.path.exists(st.session_state.v_tiktok): 
                col_v, _ = st.columns([1, 1.5])
                col_v.video(st.session_state.v_tiktok)
        
        st.divider()
        st.header("🚀 유튜브 업로드")
        c1, c2 = st.columns(2)
        with c1: client_file = st.file_uploader("🔑 client_secrets.json", type=['json'])
        with c2: token_file = st.file_uploader("🎫 token.json", type=['json'])
        
        if client_file and token_file:
            with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
            with open("token.json", "wb") as f: f.write(token_file.getbuffer())
            
            yt_title = st.text_input("📝 제목", value="은혜로운 찬양")
            yt_desc = st.text_area("📜 설명", value="할렐루야! 위로가 되길 소망합니다.\n#CCM #찬양 #예배", height=200)
            yt_tags = st.text_input("🏷️ 태그", value="CCM, 찬양, 예배, 은혜")
            privacy = st.selectbox("🔒 공개설정", ["private", "unlisted", "public", "scheduled"])
            
            if st.button("🔥 유튜브 전송"):
                success, msg = utils.upload_to_youtube(st.session_state.v_main, yt_title, yt_desc, yt_tags, "private" if privacy=="scheduled" else privacy)
                if success: 
                    st.success(msg)
                    st.balloons()
                else: 
                    st.error(msg)