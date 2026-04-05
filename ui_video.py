import streamlit as st
import os
import re
import random
import gc
import zipfile
import io
from datetime import datetime, timedelta, timezone
from moviepy.editor import AudioFileClip
import moviepy.audio.fx.all as afx
import utils

def render_tab3():
    st.header("🎬 비디오 렌더링 & 유튜브 업로드")
    st.write("2단계에서 다운받은 이미지와 음원을 올려서 최종 스크롤 영상을 만듭니다.")
    
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        st.subheader("1. 파일 업로드")
        v_audio = st.file_uploader("🎧 음원 (WAV/MP3)", type=['wav', 'mp3'], key="v_aud")
        
        st.divider()
        v_gen_main = st.checkbox("📺 유튜브 메인 생성", value=True)
        v_img_main = st.file_uploader("메인 이미지 (가로)", type=['png','jpg'], key="v_m") if v_gen_main else None
        
        v_gen_tiktok = st.checkbox("📱 틱톡 풀영상 생성", value=False)
        v_img_tiktok = st.file_uploader("틱톡 이미지 (세로)", type=['png','jpg'], key="v_t") if v_gen_tiktok else None
        
        st.divider()
        v_num_shorts = st.slider("✂️ 하이라이트 쇼츠 개수", 0, 6, 0)
        v_img_shorts = []
        for i in range(v_num_shorts):
            v_img_shorts.append(st.file_uploader(f"쇼츠 {i+1} 이미지", type=['png','jpg'], key=f"v_s_{i}"))

        st.divider()
        v_lyrics = st.text_area("📝 스크롤 가사 ([] 자동삭제)", value=st.session_state.get('gen_lyrics', ''), height=150)
        v_sync = st.text_input("⏱️ 가사 시작 시간 (예: 00:15)", placeholder="비워두면 AI가 분석")

    with col_v2:
        st.subheader("2. 렌더링 실행")
        if st.button("🚀 비디오 렌더링 시작", use_container_width=True, type="primary"):
            if v_audio is None: st.error("음원을 업로드하세요.")
            elif not v_gen_main and not v_gen_tiktok and v_num_shorts == 0: st.error("생성할 영상을 선택하세요.")
            elif v_gen_main and v_img_main is None: st.error("메인 이미지를 업로드하세요.")
            elif v_gen_tiktok and v_img_tiktok is None: st.error("틱톡 이미지를 업로드하세요.")
            elif v_num_shorts > 0 and None in v_img_shorts: st.error("모든 쇼츠 이미지를 업로드하세요.")
            else:
                status_box = st.container()
                with status_box:
                    st.markdown("### 📡 실시간 작업 모니터링")
                    step_title = st.empty()
                    progress_bar = st.progress(0)
                    progress_text = st.empty()

                try:
                    st.session_state.main_video_path = ""
                    st.session_state.tiktok_video_path = ""
                    st.session_state.shorts_paths = []
                    st.session_state.is_completed = False
                    
                    st.session_state.base_name = os.path.splitext(v_audio.name)[0]
                    final_clean_lyrics = re.sub(r'\[.*?\]', '', v_lyrics)
                    
                    step_title.markdown("#### 🎵 음원 분석 중...")
                    audio_path = "temp_audio.wav"
                    with open(audio_path, "wb") as f: f.write(v_audio.getbuffer())
                    
                    full_audio = AudioFileClip(audio_path)
                    audio_duration = full_audio.duration
                    
                    manual_start = utils.parse_time_to_sec(v_sync)
                    if manual_start >= 0: final_start_sec = manual_start
                    else: final_start_sec = utils.analyze_audio_start(full_audio)

                    if v_gen_main:
                        step_title.markdown("#### 🎬 [1단계] 메인 영상 렌더링 중...")
                        main_img_path = "temp_main_img.png"
                        utils.process_user_image(v_img_main, 1280, 720, main_img_path)
                        main_video_path = "output_main_video.mp4"
                        logger = utils.StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
                        utils.generate_video_with_lyrics(main_img_path, full_audio, final_clean_lyrics, main_video_path, logger, 1280, 720, final_start_sec)
                        st.session_state.main_video_path = main_video_path 
                        del logger; gc.collect() 

                    if v_gen_tiktok:
                        step_title.markdown("#### 📱 [2단계] 틱톡 영상 렌더링 중...")
                        tiktok_img_path = "temp_tiktok_img.png"
                        utils.process_user_image(v_img_tiktok, 720, 1280, tiktok_img_path)
                        tiktok_video_path = "output_tiktok_video.mp4"
                        logger = utils.StreamlitProgressLogger(progress_bar, progress_text, "틱톡 영상")
                        utils.generate_video_with_lyrics(tiktok_img_path, full_audio, final_clean_lyrics, tiktok_video_path, logger, 720, 1280, final_start_sec)
                        st.session_state.tiktok_video_path = tiktok_video_path 
                        del logger; gc.collect()

                    if v_num_shorts > 0:
                        step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 중...")
                        highlight_times = utils.find_highlights_lite(audio_duration, v_num_shorts)
                        for i, start_time in enumerate(highlight_times):
                            step_title.markdown(f"#### ✂️ [4단계] 쇼츠 {i+1}/{v_num_shorts} 렌더링 중...")
                            shorts_img_path = f"temp_shorts_img_{i}.png"
                            utils.process_user_image(v_img_shorts[i], 720, 1280, shorts_img_path)
                            
                            short_dur = min(random.randint(35, 55), audio_duration - start_time)
                            if short_dur < 5: short_dur = 5 
                            
                            sub_audio = full_audio.subclip(start_time, start_time + short_dur)
                            fade_dur = min(1.5, short_dur / 3.0)
                            sub_audio = sub_audio.fx(afx.audio_fadein, fade_dur).fx(afx.audio_fadeout, fade_dur)
                            
                            temp_wav_path = f"temp_short_{i}.wav"
                            sub_audio.write_audiofile(temp_wav_path, fps=44100, logger=None)
                            fresh_audio = AudioFileClip(temp_wav_path)
                            shorts_video_path = f"output_shorts_{i+1}.mp4"
                            logger = utils.StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                            
                            utils.generate_static_video(shorts_img_path, fresh_audio, shorts_video_path, logger)
                            
                            fresh_audio.close()
                            if os.path.exists(temp_wav_path): os.remove(temp_wav_path)
                            st.session_state.shorts_paths.append(shorts_video_path)
                            del logger, fresh_audio, sub_audio; gc.collect() 

                    full_audio.close()
                    st.session_state.is_completed = True
                    step_title.markdown("#### ✨ 모든 렌더링 완료! 아래에서 결과물을 다운로드하세요.")

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

        # ==========================================
        # 🎉 렌더링 완료 영상 다운로드 및 유튜브
        # ==========================================
        if st.session_state.is_completed:
            st.success("🎉 비디오 렌더링이 성공적으로 완료되었습니다!")
            
            # 🔥 [📦 전체 다운로드 (ZIP)]
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                if st.session_state.main_video_path and os.path.exists(st.session_state.main_video_path):
                    zf.write(st.session_state.main_video_path, f"{st.session_state.base_name}_Main.mp4")
                if st.session_state.tiktok_video_path and os.path.exists(st.session_state.tiktok_video_path):
                    zf.write(st.session_state.tiktok_video_path, f"{st.session_state.base_name}_TikTok.mp4")
                for i, p in enumerate(st.session_state.shorts_paths):
                    if os.path.exists(p):
                        zf.write(p, f"{st.session_state.base_name}_Short_{i+1}.mp4")
            
            st.download_button("📦 전체 영상 한 번에 다운로드 (ZIP)", zip_buffer.getvalue(), file_name=f"{st.session_state.base_name}_All_Videos.zip", mime="application/zip", type="primary", use_container_width=True)
            st.divider()

            tabs = st.tabs(["📺 메인", "📱 틱톡"] + [f"✂️ 쇼츠 {i+1}" for i in range(len(st.session_state.shorts_paths))])
            
            t_idx = 0
            if st.session_state.main_video_path:
                with tabs[t_idx]:
                    st.video(st.session_state.main_video_path)
                    with open(st.session_state.main_video_path, "rb") as f:
                        st.download_button("⬇️ 메인 영상 다운로드", f, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4", use_container_width=True)
                t_idx += 1
                
            if st.session_state.tiktok_video_path:
                with tabs[t_idx]:
                    col_vid, _ = st.columns([1, 1.5])
                    with col_vid: st.video(st.session_state.tiktok_video_path)
                    with open(st.session_state.tiktok_video_path, "rb") as f:
                        st.download_button("⬇️ 틱톡 풀영상 다운로드", f, file_name=f"{st.session_state.base_name}_TikTok.mp4", mime="video/mp4", use_container_width=True)
                t_idx += 1
                    
            for i, shorts_path in enumerate(st.session_state.shorts_paths):
                with tabs[t_idx]:
                    col_vid, _ = st.columns([1, 1.5])
                    with col_vid: st.video(shorts_path)
                    with open(shorts_path, "rb") as f:
                        st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드", f, file_name=f"{st.session_state.base_name}_Short_{i+1}.mp4", mime="video/mp4", use_container_width=True)
                t_idx += 1

            st.divider()
            st.header("🚀 유튜브 다이렉트 업로드")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1: client_file = st.file_uploader("🔑 client_secrets.json 업로드", type=['json'])
            with c_f2: token_file = st.file_uploader("🎫 token.json 업로드", type=['json'])

            if client_file and token_file:
                with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
                with open("token.json", "wb") as f: f.write(token_file.getbuffer())
                    
                up_opts = {}
                if st.session_state.main_video_path: up_opts["📺 메인 영상"] = st.session_state.main_video_path
                if st.session_state.tiktok_video_path: up_opts["📱 틱톡 풀영상"] = st.session_state.tiktok_video_path
                for i, p in enumerate(st.session_state.shorts_paths): up_opts[f"✂️ 쇼츠 {i+1}"] = p
                    
                if up_opts:
                    s_vid_key = st.selectbox("📌 업로드할 영상 선택", list(up_opts.keys()))
                    s_vid_path = up_opts[s_vid_key]
                    
                    yt_title_val = f"[{st.session_state.gen_title_kr or st.session_state.base_name}] 은혜로운 찬양 플레이리스트"
                    yt_title = st.text_input("📝 영상 제목", value=yt_title_val)
                    
                    ccm_desc_template = f"""할렐루야! 오늘 함께 나눌 찬양은 '{st.session_state.gen_title_kr or st.session_state.base_name}' 입니다. 🌿\n\n지치고 상한 마음, 예배의 자리를 사모하는 모든 분들께 이 찬양이 작은 위로와 평안이 되기를 소망합니다.\n가사를 묵상하며 주님의 크신 사랑과 은혜를 깊이 경험하는 귀한 시간 되시길 기도합니다. \n\n항상 주님 안에서 승리하시고, 오늘 하루도 말씀과 기도로 나아가는 복된 하루 되세요! 🙏\n\n🔔 구독과 좋아요는 은혜로운 찬양을 나누는 데 큰 힘이 됩니다. 💖\n\n#CCM #찬양 #예배 #은혜 #위로 #기도 #기독교 #교회 #찬양추천 #플레이리스트"""
                    yt_desc = st.text_area("📜 영상 설명", value=ccm_desc_template, height=300)
                    
                    ccm_tags = "CCM, 찬양, 예배, 은혜, 기독교, 교회, 찬송가, 워십, 복음성가, 기도, 묵상, 힐링찬양, 위로, 평안, 찬양추천, 플레이리스트, worship, praise, 주일예배, 특송, 은혜로운찬양, 아침찬양, 수면찬양"
                    yt_tags = st.text_input("🏷️ 검색 태그", value=ccm_tags)
                    
                    privacy_ui = st.selectbox("🔒 공개 상태", ["비공개 (Private)", "일부 공개 (Unlisted)", "공개 (Public)", "예약 업로드 (Scheduled)"])
                    
                    up_date = None; up_time = None
                    if privacy_ui == "예약 업로드 (Scheduled)":
                        cd, ct = st.columns(2)
                        with cd: up_date = st.date_input("🗓️ 날짜 선택")
                        with ct: up_time = st.time_input("⏰ 한국 시간(KST) 선택")
                    
                    if st.button("🔥 유튜브로 전송", type="primary", use_container_width=True):
                        with st.spinner("안전하게 업로드 중입니다..."):
                            p_map = {"비공개 (Private)": "private", "일부 공개 (Unlisted)": "unlisted", "공개 (Public)": "public", "예약 업로드 (Scheduled)": "private"}
                            final_pub = None
                            if privacy_ui == "예약 업로드 (Scheduled)":
                                dt_utc = datetime.combine(up_date, up_time, tzinfo=timezone(timedelta(hours=9))).astimezone(timezone.utc)
                                final_pub = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")
                                
                            success, msg = utils.upload_to_youtube(s_vid_path, yt_title, yt_desc, yt_tags, p_map[privacy_ui], final_pub)
                            if success: st.success(msg); st.balloons()
                            else: st.error(msg)