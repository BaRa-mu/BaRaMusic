import streamlit as st
import requests
import os
import re
import random
import gc
import numpy as np
from datetime import datetime, timedelta, timezone
from moviepy.editor import AudioFileClip, ImageClip, VideoClip
import moviepy.audio.fx.all as afx
from PIL import Image, ImageDraw, ImageFont, ImageChops
from proglog import ProgressBarLogger

st.set_page_config(page_title="은혜로운 찬양 팩토리", page_icon="🕊️", layout="wide")

# --- 💾 메모리 유지 ---
if 'is_completed' not in st.session_state: st.session_state.is_completed = False
if 'main_video_path' not in st.session_state: st.session_state.main_video_path = ""
if 'tiktok_video_path' not in st.session_state: st.session_state.tiktok_video_path = ""
if 'shorts_paths' not in st.session_state: st.session_state.shorts_paths = []
if 'clean_lyrics' not in st.session_state: st.session_state.clean_lyrics = ""
if 'base_name' not in st.session_state: st.session_state.base_name = ""

# --- 🔠 가사용 폰트 다운로드 ---
font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
font_path = "NanumGothicBold.ttf"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f: f.write(requests.get(font_url).content)

st.title("🕊️ 은혜로운 찬양 영상 팩토리")
st.write("유튜브(가로), 틱톡/릴스(세로 풀영상), 쇼츠(하이라이트)를 한 번에 제작하고 업로드하세요.")

# ==========================================
# 🌟 진행률 로거
# ==========================================
class StreamlitProgressLogger(ProgressBarLogger):
    def __init__(self, st_bar, st_text, prefix):
        super().__init__()
        self.st_bar = st_bar
        self.st_text = st_text
        self.prefix = prefix

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percent = min(1.0, value / total)
            self.st_bar.progress(percent)
            task_type = "오디오 합성 중" if bar == 'chunk' else "비디오 렌더링 중"
            self.st_text.text(f"⏳ {self.prefix} - {task_type}: {int(percent * 100)}%")

# ==========================================
# ⚙️ 시간 변환 유틸리티
# ==========================================
def parse_time_to_sec(time_str):
    try:
        time_str = time_str.strip()
        if not time_str:
            return -1 
        if ":" in time_str:
            m, s = time_str.split(":")
            return int(m) * 60 + int(s)
        else:
            return int(time_str)
    except:
        return -1

# ==========================================
# ⚙️ 핵심 알고리즘 
# ==========================================
def find_highlights_lite(duration_sec, num_highlights=0): 
    if num_highlights <= 0: return []
    highlights = []
    if duration_sec < 60: return [random.randint(5, max(5, int(duration_sec) - 30)) for _ in range(num_highlights)]
    section_length = (duration_sec - 30) / num_highlights
    for i in range(num_highlights):
        hit_time = (i * section_length) + (section_length * random.uniform(0.5, 0.8))
        highlights.append(int(hit_time))
    return highlights

def process_user_image(uploaded_file, width, height, output_path):
    img = Image.open(uploaded_file).convert("RGBA")
    target_ratio = width / height
    img_ratio = img.width / img.height
    
    # 🌟 자동 크롭: 가로 이미지를 세로(틱톡) 렌더링에 넣어도 자동으로 예쁘게 중앙이 잘립니다.
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
        
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.convert("RGB").save(output_path)
    img.close()

def analyze_audio_start(audio_clip):
    duration = audio_clip.duration
    default_start = min(15.0, duration * 0.1)
    
    try:
        snd_array = audio_clip.to_soundarray(fps=2)
        if len(snd_array.shape) > 1:
            snd_array = snd_array.mean(axis=1)
            
        rms = np.abs(snd_array)
        threshold = np.max(rms) * 0.15 
        
        start_idx = 0
        for i in range(len(rms)):
            if rms[i] > threshold:
                start_idx = i
                break
                
        start_sec = start_idx / 2.0
        start_sec = max(0, start_sec - 4.0) 
        
        if start_sec < 0 or start_sec > 40: 
            start_sec = default_start
            
        return start_sec
    except:
        return default_start

def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height, start_sec=0):
    base_img = Image.open(image_path).convert("RGBA")
    duration = audio_clip.duration
    lines = lyrics_text.rstrip().split('\n') 
    
    if not lyrics_text.strip():
        clip = ImageClip(np.array(base_img.convert("RGB"))).set_duration(duration).set_audio(audio_clip)
        clip.write_videofile(output_path, fps=1, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
        clip.close()
        base_img.close()
        return

    lyric_font_size = 22 if width == 1280 else 20
    lyric_font = ImageFont.truetype(font_path, lyric_font_size)
    line_spacing = 2.0
    
    try:
        dummy_bbox = ImageDraw.Draw(base_img).textbbox((0,0), "A", font=lyric_font)
        line_height = dummy_bbox[3] - dummy_bbox[1]
    except:
        line_height = lyric_font_size
        
    step_y = line_height * line_spacing
    total_text_height = int(len(lines) * step_y)
    
    window_top = int(height * 0.40)   
    window_bottom = int(height * 0.95) 
    window_height = window_bottom - window_top

    gradient_mask = Image.new("L", (width, window_height), 255)
    draw_grad = ImageDraw.Draw(gradient_mask)
    fade_height = int(window_height * 0.4) 

    for y in range(fade_height):
        alpha = int((y / fade_height) * 255)
        draw_grad.line((0, y, width, y), fill=alpha)
        
    for y in range(window_height - fade_height, window_height):
        dist_from_bottom = window_height - y
        alpha = int((dist_from_bottom / fade_height) * 255)
        draw_grad.line((0, y, width, y), fill=alpha)

    long_img_height = window_height + total_text_height + window_height
    long_lyrics_img = Image.new("RGBA", (width, int(long_img_height)), (0, 0, 0, 0))
    draw_long = ImageDraw.Draw(long_lyrics_img)
    
    for i, line in enumerate(lines):
        lyric_y = window_height + (i * step_y)
        draw_long.text((width / 2, lyric_y), line, font=lyric_font, fill="white", stroke_width=2, stroke_fill="black", align="center", anchor="ma")

    def make_frame(t):
        frame_img = base_img.copy()
        
        if t < start_sec:
            progress = 0.0 
        else:
            scroll_duration = duration - start_sec
            if scroll_duration <= 0:
                progress = 1.0
            else:
                progress = (t - start_sec) / scroll_duration
                progress = min(1.0, max(0.0, progress)) 
            
        viewport_y = int(progress * (window_height + total_text_height))
        visible_lyrics = long_lyrics_img.crop((0, viewport_y, width, viewport_y + window_height))
        
        current_alpha = visible_lyrics.getchannel('A')
        blended_alpha = ImageChops.multiply(current_alpha, gradient_mask)
        visible_lyrics.putalpha(blended_alpha)
        
        frame_img.paste(visible_lyrics, (0, window_top), visible_lyrics)
        result_array = np.array(frame_img.convert("RGB"))
        
        frame_img.close()
        visible_lyrics.close()
        return result_array

    video_clip = VideoClip(make_frame, duration=duration).set_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
    
    video_clip.close()
    base_img.close()
    long_lyrics_img.close()
    gradient_mask.close()

# ==========================================
# 🚀 유튜브 예약 및 다이렉트 업로드 함수
# ==========================================
def upload_to_youtube(video_path, title, description, tags, privacy_status, publish_at=None):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        return False, "구글 API 라이브러리가 없습니다."

    if not os.path.exists("token.json"):
        return False, "token.json 파일이 업로드되지 않았습니다."

    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        else:
            return False, "토큰이 만료되었거나 유효하지 않습니다."

    try:
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "categoryId": "10" 
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }
        
        if publish_at:
            body["status"]["publishAt"] = publish_at

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        return True, f"🎉 업로드 성공! 영상 링크: https://youtu.be/{response.get('id')}"
    except Exception as e:
        return False, f"업로드 중 오류 발생: {e}"

# ==========================================
# 🖥️ 사이드바 & 파일 업로드 UI 구성
# ==========================================
st.sidebar.header("1. 파일 업로드 (필수)")
uploaded_audio = st.sidebar.file_uploader("🎧 음원 파일 (WAV, MP3)", type=['wav', 'mp3'])

st.sidebar.divider()
st.sidebar.header("2. 생성 항목 선택")

# 📺 1. 메인 영상 (가로)
generate_main = st.sidebar.checkbox("📺 유튜브 메인 (가로 16:9) 생성", value=True)
uploaded_main_img = None
if generate_main:
    uploaded_main_img = st.sidebar.file_uploader("📺 가로 메인용 배경", type=['jpg', 'jpeg', 'png'])

# 📱 2. 메인 2 (틱톡/릴스용 세로)
generate_tiktok = st.sidebar.checkbox("📱 틱톡 풀영상 (세로 9:16) 생성", value=False)
uploaded_tiktok_img = None
if generate_tiktok:
    st.sidebar.info("💡 가로 이미지를 올려도 틱톡용(세로)으로 알아서 중앙이 잘립니다.")
    uploaded_tiktok_img = st.sidebar.file_uploader("📱 틱톡 풀영상 배경", type=['jpg', 'jpeg', 'png'])

st.sidebar.divider()
# ✂️ 3. 쇼츠 추출 (하이라이트)
num_shorts = st.sidebar.slider("✂️ 하이라이트 쇼츠 (가사X) 개수", min_value=0, max_value=4, value=0)

uploaded_shorts_imgs = []
if num_shorts > 0:
    for i in range(num_shorts):
        upl = st.sidebar.file_uploader(f"✂️ 쇼츠 {i+1} 배경", type=['jpg', 'jpeg', 'png'], key=f"short_upload_{i}")
        uploaded_shorts_imgs.append(upl)

st.sidebar.divider()
lyrics = st.sidebar.text_area("📝 가사 입력 (메인 및 틱톡 풀영상에 스크롤됨)", height=150)

st.sidebar.write("⏱️ 가사 스크롤 시작 시간")
sync_start = st.sidebar.text_input("시작 (예: 00:15)", placeholder="비워두면 AI가 자동으로 맞춥니다.")

# ==========================================
# 🚀 렌더링 시작 및 실시간 모니터링
# ==========================================
if st.button("🚀 비디오 렌더링 시작", use_container_width=True):
    if uploaded_audio is None:
        st.error("⚠️ 음원 파일을 업로드해주세요.")
    elif not generate_main and not generate_tiktok and num_shorts == 0:
        st.error("⚠️ 최소 하나 이상의 영상을 생성하도록 선택해주세요.")
    elif generate_main and uploaded_main_img is None:
        st.error("⚠️ 가로 메인 영상을 생성하려면 배경 이미지를 업로드해야 합니다.")
    elif generate_tiktok and uploaded_tiktok_img is None:
        st.error("⚠️ 틱톡 풀영상을 생성하려면 배경 이미지를 업로드해야 합니다.")
    elif num_shorts > 0 and None in uploaded_shorts_imgs:
        st.error("⚠️ 설정한 쇼츠 개수만큼 쇼츠 배경 이미지를 모두 업로드해주세요.")
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
            
            base_name = os.path.splitext(uploaded_audio.name)[0]
            st.session_state.base_name = base_name
            final_clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)
            st.session_state.clean_lyrics = final_clean_lyrics 

            step_title.markdown("#### 🎵 음원 분석 및 이미지 준비 중...")
            audio_path = "temp_audio.wav"
            with open(audio_path, "wb") as f: f.write(uploaded_audio.getbuffer())
            
            full_audio = AudioFileClip(audio_path)
            audio_duration = full_audio.duration
            
            manual_start = parse_time_to_sec(sync_start)
            if manual_start >= 0:
                final_start_sec = manual_start
                st.toast(f"✅ 사용자 설정: {int(final_start_sec)}초 부터 가사가 올라옵니다.")
            else:
                final_start_sec = analyze_audio_start(full_audio)
                st.toast(f"🤖 AI 분석 완료: {int(final_start_sec)}초 부터 가사가 올라옵니다.")

            # [작업 1] 메인 영상 렌더링 (가로)
            if generate_main:
                step_title.markdown(f"#### 🎬 [1단계] 메인 가로 영상(16:9) 렌더링 중... (가사 시작: {int(final_start_sec)}초)")
                main_img_path = "temp_main_img.png"
                process_user_image(uploaded_main_img, 1280, 720, main_img_path)
                
                main_video_path = "output_main_video.mp4"
                main_logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
                
                generate_video_with_lyrics(main_img_path, full_audio, final_clean_lyrics, main_video_path, main_logger, 1280, 720, start_sec=final_start_sec)
                
                st.session_state.main_video_path = main_video_path 
                del main_logger
                gc.collect() 

            # [작업 1-2] 틱톡 풀영상 렌더링 (세로)
            if generate_tiktok:
                step_title.markdown(f"#### 📱 [2단계] 틱톡 풀영상(9:16) 렌더링 중... (가사 시작: {int(final_start_sec)}초)")
                tiktok_img_path = "temp_tiktok_img.png"
                # 가로 이미지가 들어와도 720x1280에 맞춰 예쁘게 크롭됩니다.
                process_user_image(uploaded_tiktok_img, 720, 1280, tiktok_img_path)
                
                tiktok_video_path = "output_tiktok_video.mp4"
                tiktok_logger = StreamlitProgressLogger(progress_bar, progress_text, "틱톡 영상")
                
                # 메인 영상과 완벽히 동일한 가사와 스크롤 효과 적용
                generate_video_with_lyrics(tiktok_img_path, full_audio, final_clean_lyrics, tiktok_video_path, tiktok_logger, 720, 1280, start_sec=final_start_sec)
                
                st.session_state.tiktok_video_path = tiktok_video_path 
                del tiktok_logger
                gc.collect()

            # [작업 2] 쇼츠 추출 및 렌더링 (가사 없음)
            if num_shorts > 0:
                progress_bar.progress(0)
                progress_text.empty()
                step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 구간 계산 중...")
                highlight_times = find_highlights_lite(audio_duration, num_shorts)
                
                for i, start_time in enumerate(highlight_times):
                    progress_bar.progress(0)
                    step_title.markdown(f"#### ✂️ [4단계] 하이라이트 쇼츠 {i+1}/{num_shorts} 제작 중... (구간: {int(start_time)}초 부터)")
                    
                    shorts_img_path = f"temp_shorts_img_{i}.png"
                    process_user_image(uploaded_shorts_imgs[i], 720, 1280, shorts_img_path)
                    
                    short_dur = min(random.randint(35, 55), audio_duration - start_time)
                    if short_dur < 5: short_dur = 5 
                    
                    shorts_audio = full_audio.subclip(start_time, start_time + short_dur)
                    fade_dur = min(1.5, shorts_audio.duration / 3.0)
                    shorts_audio = shorts_audio.fx(afx.audio_fadein, fade_dur).fx(afx.audio_fadeout, fade_dur)
                    
                    shorts_video_path = f"output_shorts_{i+1}.mp4"
                    shorts_logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                    
                    # 쇼츠에는 가사 빈 문자열("") 전송 -> 스크롤 없이 초고속 렌더링
                    generate_video_with_lyrics(shorts_img_path, shorts_audio, "", shorts_video_path, shorts_logger, 720, 1280)
                    
                    shorts_audio.close()
                    st.session_state.shorts_paths.append(shorts_video_path)
                    del shorts_logger, shorts_audio
                    gc.collect() 

            full_audio.close()
            st.session_state.is_completed = True
            step_title.markdown("#### ✨ 모든 작업 완료! 아래에서 확인하세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# ==========================================
# 🎉 완료 화면 및 유튜브 다이렉트 업로드
# ==========================================
if st.session_state.is_completed:
    st.divider()
    
    valid_files_exist = False
    if st.session_state.main_video_path and os.path.exists(st.session_state.main_video_path):
        valid_files_exist = True
    if st.session_state.tiktok_video_path and os.path.exists(st.session_state.tiktok_video_path):
        valid_files_exist = True
    for p in st.session_state.shorts_paths:
        if os.path.exists(p):
            valid_files_exist = True
            
    if not valid_files_exist:
        st.error("🚨 서버 메모리 부족으로 생성된 파일이 유실되었습니다. 새로고침 후 다시 시도해주세요.")
        st.session_state.is_completed = False
    else:
        st.success("🎉 요청하신 영상 렌더링이 성공적으로 완료되었습니다!")
        
        tab_names = []
        if st.session_state.main_video_path: tab_names.append("📺 메인 영상")
        if st.session_state.tiktok_video_path: tab_names.append("📱 틱톡 풀영상")
        for i in range(len(st.session_state.shorts_paths)): tab_names.append(f"✂️ 쇼츠 {i+1}")
            
        tabs = st.tabs(tab_names)
        
        tab_idx = 0
        if st.session_state.main_video_path:
            with tabs[tab_idx]:
                st.video(st.session_state.main_video_path)
                with open(st.session_state.main_video_path, "rb") as file:
                    st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")
            tab_idx += 1
            
        if st.session_state.tiktok_video_path:
            with tabs[tab_idx]:
                st.video(st.session_state.tiktok_video_path)
                with open(st.session_state.tiktok_video_path, "rb") as file:
                    st.download_button("⬇️ 틱톡 풀영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_TikTok.mp4", mime="video/mp4")
            tab_idx += 1
                
        for i, shorts_path in enumerate(st.session_state.shorts_paths):
            with tabs[tab_idx]:
                st.video(shorts_path)
                with open(shorts_path, "rb") as file:
                    st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Shorts_{i+1}.mp4", mime="video/mp4")
            tab_idx += 1

        st.divider()
        
        st.header("🚀 유튜브 다이렉트 업로드")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            client_file = st.file_uploader("🔑 client_secrets.json 업로드", type=['json'])
        with col_f2:
            token_file = st.file_uploader("🎫 token.json 업로드 (PC에서 생성한 파일)", type=['json'])

        if client_file and token_file:
            with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
            with open("token.json", "wb") as f: f.write(token_file.getbuffer())
                
            upload_options = {}
            if st.session_state.main_video_path and os.path.exists(st.session_state.main_video_path):
                upload_options["📺 메인 영상 (가로)"] = st.session_state.main_video_path
            if st.session_state.tiktok_video_path and os.path.exists(st.session_state.tiktok_video_path):
                upload_options["📱 틱톡 풀영상 (세로)"] = st.session_state.tiktok_video_path
            for i, p in enumerate(st.session_state.shorts_paths):
                if os.path.exists(p):
                    upload_options[f"✂️ 쇼츠 {i+1} (세로)"] = p
                
            if upload_options:
                selected_vid_key = st.selectbox("📌 업로드할 영상 선택", list(upload_options.keys()))
                selected_vid_path = upload_options[selected_vid_key]
                
                yt_title = st.text_input("📝 영상 제목", value=f"[{st.session_state.base_name}] 은혜로운 찬양 플레이리스트")
                
                ccm_desc_template = f"""할렐루야! 오늘 함께 나눌 찬양은 '{st.session_state.base_name}' 입니다. 🌿

지치고 상한 마음, 예배의 자리를 사모하는 모든 분들께 이 찬양이 작은 위로와 평안이 되기를 소망합니다.
가사를 묵상하며 주님의 크신 사랑과 은혜를 깊이 경험하는 귀한 시간 되시길 기도합니다. 

항상 주님 안에서 승리하시고, 오늘 하루도 말씀과 기도로 나아가는 복된 하루 되세요! 🙏

🔔 구독과 좋아요는 은혜로운 찬양을 나누는 데 큰 힘이 됩니다. 💖

#CCM #찬양 #예배 #은혜 #위로 #기도 #기독교 #교회 #찬양추천 #플레이리스트"""
                
                yt_desc = st.text_area("📜 영상 설명", value=ccm_desc_template, height=300)
                
                ccm_tags = "CCM, 찬양, 예배, 은혜, 기독교, 교회, 찬송가, 워십, 복음성가, 기도, 묵상, 힐링찬양, 위로, 평안, 찬양추천, 플레이리스트, worship, praise, 주일예배, 특송, 은혜로운찬양, 아침찬양, 수면찬양"
                yt_tags = st.text_input("🏷️ 검색 태그 (쉼표로 구분)", value=ccm_tags)
                
                privacy_ui = st.selectbox("🔒 공개 상태", ["비공개 (Private)", "일부 공개 (Unlisted)", "공개 (Public)", "예약 업로드 (Scheduled)"])
                
                upload_date = None
                upload_time = None
                if privacy_ui == "예약 업로드 (Scheduled)":
                    st.info("💡 예약 시간은 반드시 '현재 시각보다 미래'여야 합니다.")
                    col_d, col_t = st.columns(2)
                    with col_d: upload_date = st.date_input("🗓️ 날짜 선택")
                    with col_t: upload_time = st.time_input("⏰ 한국 시간(KST) 기준 시간 선택")
                
                if st.button("🔥 유튜브 채널로 전송", type="primary"):
                    with st.spinner("유튜브 서버로 안전하게 업로드 중입니다... (영상 크기에 따라 수 분 소요됨)"):
                        privacy_map = {
                            "비공개 (Private)": "private",
                            "일부 공개 (Unlisted)": "unlisted",
                            "공개 (Public)": "public",
                            "예약 업로드 (Scheduled)": "private"
                        }
                        final_privacy = privacy_map[privacy_ui]
                        final_publish_at = None
                        
                        if privacy_ui == "예약 업로드 (Scheduled)":
                            kst_tz = timezone(timedelta(hours=9))
                            dt_kst = datetime.combine(upload_date, upload_time, tzinfo=kst_tz)
                            dt_utc = dt_kst.astimezone(timezone.utc)
                            final_publish_at = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")
                            
                        success, msg = upload_to_youtube(
                            selected_vid_path, 
                            yt_title, 
                            yt_desc, 
                            yt_tags, 
                            final_privacy, 
                            publish_at=final_publish_at
                        )
                        
                        if success:
                            st.success(msg)
                            st.balloons()
                        else:
                            st.error(msg)
        else:
            st.warning("위 2개의 인증 파일(client_secrets.json, token.json)을 모두 업로드해야 업로드 버튼이 나타납니다.")