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

st.set_page_config(page_title="AI 뮤직비디오 자동화 팩토리", page_icon="🎬", layout="wide")

# ==========================================
# 💾 세션 상태 유지
# ==========================================
if 'is_completed' not in st.session_state: st.session_state.is_completed = False
if 'main_video_path' not in st.session_state: st.session_state.main_video_path = ""
if 'tiktok_video_path' not in st.session_state: st.session_state.tiktok_video_path = ""
if 'shorts_paths' not in st.session_state: st.session_state.shorts_paths = []
if 'base_name' not in st.session_state: st.session_state.base_name = ""

# ==========================================
# 🔠 폰트 다운로드 (디자인용 3종 세트)
# ==========================================
font_links = {
    "나눔고딕 (기본/깔끔)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강조/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (모던/세련)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

for name, (file_name, url) in font_links.items():
    if not os.path.exists(file_name):
        try:
            with open(file_name, "wb") as f: f.write(requests.get(url).content)
        except: pass

# ==========================================
# 🌟 (그대로 복원된) 진행률 로거 및 유틸리티
# ==========================================
class StreamlitProgressLogger(ProgressBarLogger):
    def __init__(self, st_bar, st_text, prefix):
        super().__init__()
        self.st_bar = st_bar
        self.st_text = st_text
        self.prefix = prefix
        self.last_percent = 0.0 

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percent = value / total
            if percent - self.last_percent >= 0.01 or percent >= 1.0:
                self.st_bar.progress(min(1.0, percent))
                task_type = "오디오 합성 중" if bar == 'chunk' else "비디오 렌더링 중"
                self.st_text.text(f"⏳ {self.prefix} - {task_type}: {int(percent * 100)}%")
                self.last_percent = percent

def parse_time_to_sec(time_str):
    try:
        time_str = time_str.strip()
        if not time_str: return -1 
        if ":" in time_str:
            m, s = time_str.split(":")
            return int(m) * 60 + int(s)
        else: return int(time_str)
    except: return -1

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
    img = Image.open(uploaded_file).convert("RGB")
    target_ratio = width / height
    img_ratio = img.width / img.height
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(output_path)
    img.close()

def analyze_audio_start(audio_clip):
    duration = audio_clip.duration
    default_start = min(15.0, duration * 0.1)
    try:
        snd_array = audio_clip.to_soundarray(fps=2)
        if len(snd_array.shape) > 1: snd_array = snd_array.mean(axis=1)
        rms = np.abs(snd_array)
        threshold = np.max(rms) * 0.15 
        start_idx = 0
        for i in range(len(rms)):
            if rms[i] > threshold:
                start_idx = i; break
        start_sec = max(0, (start_idx / 2.0) - 4.0) 
        if start_sec < 0 or start_sec > 40: start_sec = default_start
        del snd_array
        return start_sec
    except: return default_start

# ==========================================
# 🖼️ 이미지 팩토리: 디자인 생성 함수
# ==========================================
def design_and_save_image(width, height, prompt, seed, title_kr, title_en, font_choice, title_size, y_pos_percent, line_spacing, output_path):
    # AI 이미지 생성 (또는 기본 다크배경)
    safe_prompt = re.sub(r'\s+', ' ', prompt).strip()
    encoded_prompt = urllib.parse.quote(safe_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        with open(output_path, "wb") as f: f.write(response.content)
        img = Image.open(output_path).convert("RGBA")
    except:
        img = Image.new("RGBA", (width, height), (35, 35, 40, 255))
        
    draw = ImageDraw.Draw(img)
    font_file = font_links[font_choice][0]
    
    font_kr = ImageFont.truetype(font_file, title_size)
    font_en = ImageFont.truetype(font_file, int(title_size * 0.65))
    
    y_center = height * (y_pos_percent / 100.0)
    
    try:
        h_kr = draw.textbbox((0,0), title_kr if title_kr else "A", font=font_kr)[3]
        h_en = draw.textbbox((0,0), title_en if title_en else "A", font=font_en)[3]
    except:
        h_kr = title_size
        h_en = int(title_size * 0.65)
        
    total_h = h_kr + (line_spacing if title_en else 0) + (h_en if title_en else 0)
    start_y = y_center - (total_h / 2)
    
    if title_kr:
        draw.text((width/2, start_y), title_kr, font=font_kr, fill="white", stroke_width=3, stroke_fill="black", anchor="ma")
    if title_en:
        draw.text((width/2, start_y + h_kr + line_spacing), title_en, font=font_en, fill="lightgray", stroke_width=2, stroke_fill="black", anchor="ma")
        
    img.convert("RGB").save(output_path)
    img.close()
    return output_path

# ==========================================
# 🎬 (그대로 복원된) 완벽 비디오 렌더링 엔진
# ==========================================
def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height, start_sec=0):
    base_img = Image.open(image_path).convert("RGB")
    base_img_np = np.array(base_img)
    base_img.close()
    
    duration = audio_clip.duration
    lines = lyrics_text.rstrip().split('\n') 
    
    if not lyrics_text.strip():
        clip = ImageClip(base_img_np).set_duration(duration).set_audio(audio_clip)
        clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
        clip.close()
        return

    if width == 720 and height == 1280:
        lyric_font_size = 24  
        window_top = int(height * 0.60) 
    else:
        lyric_font_size = 22  
        window_top = int(height * 0.40) 
        
    lyric_font = ImageFont.truetype(font_links["나눔고딕 (기본/깔끔)"][0], lyric_font_size)
    line_spacing = 2.0
    
    try:
        h_dummy = ImageDraw.Draw(Image.new("RGB", (10,10))).textbbox((0,0), "A", font=lyric_font)[3]
    except: h_dummy = lyric_font_size
        
    step_y = h_dummy * line_spacing
    total_text_height = int(len(lines) * step_y)
    
    window_bottom = int(height * 0.95) 
    window_height = window_bottom - window_top

    long_img_height = window_height + total_text_height + window_height
    long_lyrics_img = Image.new("RGBA", (width, int(long_img_height)), (0, 0, 0, 0))
    draw_long = ImageDraw.Draw(long_lyrics_img)
    
    for i, line in enumerate(lines):
        draw_long.text((width / 2, window_height + (i * step_y)), line, font=lyric_font, fill="white", stroke_width=2, stroke_fill="black", anchor="ma")

    long_lyrics_np = np.array(long_lyrics_img)
    long_lyrics_img.close()

    fade_mask = np.ones((window_height, width, 1), dtype=np.float32)
    fade_height = int(window_height * 0.4) 
    for y in range(fade_height): fade_mask[y, :, 0] = y / fade_height
    for y in range(window_height - fade_height, window_height): fade_mask[y, :, 0] = (window_height - y) / fade_height

    bg_slice = base_img_np[window_top:window_bottom, :, :].astype(np.float32)

    def make_frame(t):
        if t < start_sec: progress = 0.0 
        else:
            scroll_dur = duration - start_sec
            progress = 1.0 if scroll_dur <= 0 else min(1.0, max(0.0, (t - start_sec) / scroll_dur))
            
        viewport_y = int(progress * (window_height + total_text_height))
        src_np = long_lyrics_np[viewport_y : viewport_y + window_height, :, :]
        alpha = (src_np[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis] * fade_mask
        blended = src_np[:, :, :3] * alpha + bg_slice * (1.0 - alpha)
        
        out_frame = base_img_np.copy()
        out_frame[window_top:window_bottom, :, :] = blended.astype(np.uint8)
        return out_frame

    video_clip = VideoClip(make_frame, duration=duration).set_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
    video_clip.close()

def generate_static_video(image_path, audio_clip, output_path, logger):
    clip = ImageClip(image_path).set_duration(audio_clip.duration).set_audio(audio_clip)
    clip.write_videofile(output_path, fps=2, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
    clip.close()

def upload_to_youtube(video_path, title, description, tags, privacy_status, publish_at=None):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError: return False, "구글 API 라이브러리가 없습니다."

    if not os.path.exists("token.json"): return False, "token.json 파일이 없습니다."
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as token: token.write(creds.to_json())
        else: return False, "토큰 만료됨"

    try:
        youtube = build("youtube", "v3", credentials=creds)
        body = {"snippet": {"title": title, "description": description, "tags": [t.strip() for t in tags.split(",") if t.strip()], "categoryId": "10"}, "status": {"privacyStatus": privacy_status}}
        if publish_at: body["status"]["publishAt"] = publish_at
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        return True, f"🎉 성공! 링크: https://youtu.be/{response.get('id')}"
    except Exception as e: return False, f"오류: {e}"

# ==========================================
# 🖥️ 3-Step 앱 UI 구성
# ==========================================
tab1, tab2, tab3 = st.tabs(["📝 1. 수노(Suno) 가사 생성", "🎨 2. 이미지 팩토리 (디자인)", "🎬 3. 비디오 렌더링 & 업로드"])

# ------------------------------------------
# [탭 1] 수노 가사 프롬프트 생성기
# ------------------------------------------
with tab1:
    st.header("📝 수노(Suno AI) 맞춤형 프롬프트 & 가사 생성")
    col1, col2 = st.columns(2)
    with col1:
        s_genre = st.text_input("🎸 장르/스타일 (예: Acoustic Ballad, CCM)")
        s_mood = st.text_input("✨ 분위기 (예: emotional, holy, peaceful)")
        s_vocal = st.text_input("🎤 보컬 (예: male vocal, warm choir)")
    
    st.info(f"💡 **Suno Style Prompt 복사용:**\n\n`{s_genre}, {s_mood}, {s_vocal}`")
    
    st.write("📌 가사 구조 태그 삽입 (클릭 시 하단에 추가됨)")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("[Intro]"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Intro]\n"
    if c2.button("[Verse]"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Verse]\n"
    if c3.button("[Chorus]"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Chorus]\n"
    if c4.button("[Bridge]"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Bridge]\n"
    if c5.button("[Outro]"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Outro]\n"
    
    st.session_state.s_lyrics = st.text_area("가사 작성칸", value=st.session_state.get('s_lyrics', ''), height=200)

# ------------------------------------------
# [탭 2] 이미지 팩토리 (타이틀 디자인 및 다운로드)
# ------------------------------------------
with tab2:
    st.header("🎨 이미지 팩토리 (자동 제목 디자인)")
    st.write("수노에서 완성한 음원(`한글제목_EngTitle.mp3`)을 올리면 제목을 파싱하여 AI가 이미지를 그려줍니다.")
    
    audio_for_parsing = st.file_uploader("🎧 음원 업로드 (제목 파싱용)", type=['wav', 'mp3'])
    
    t_kr = ""; t_en = ""
    if audio_for_parsing:
        base = os.path.splitext(audio_for_parsing.name)[0]
        parts = base.split('_')
        t_kr = parts[0]
        t_en = parts[1] if len(parts) > 1 else ""
        
    c_t1, c_t2 = st.columns(2)
    with c_t1: t_kr = st.text_input("📌 한글 제목", value=t_kr)
    with c_t2: t_en = st.text_input("📌 영문 제목", value=t_en)
    
    st.divider()
    st.subheader("⚙️ 제목 디자인 세부 옵션")
    d1, d2, d3, d4 = st.columns(4)
    with d1: font_choice = st.selectbox("글씨체", list(font_links.keys()))
    with d2: title_size = st.slider("메인 글씨 크기", 30, 120, 60)
    with d3: y_pos_percent = st.slider("Y축 위치 (%)", 5, 95, 15)
    with d4: line_spacing = st.slider("한영 줄간격", 0, 50, 15)
    
    st.divider()
    st.subheader("🖼️ 이미지 생성 옵션")
    ai_prompt = st.text_input("🤖 AI 배경 프롬프트 (영어로 입력)", "cinematic beautiful sky, peaceful, masterpiece, 4k")
    
    img_m = st.checkbox("📺 유튜브 메인 (16:9)", value=True)
    img_t = st.checkbox("📱 틱톡 풀영상 (9:16)", value=False)
    num_s_img = st.slider("✂️ 쇼츠 이미지 (9:16) 개수", 0, 6, 0)
    
    if st.button("✨ 디자인 이미지 렌더링", type="primary", use_container_width=True):
        with st.spinner("AI가 이미지를 생성하고 제목을 입히고 있습니다..."):
            st.session_state.img_res_main = None
            st.session_state.img_res_tiktok = None
            st.session_state.img_res_shorts = []
            
            if img_m:
                st.session_state.img_res_main = design_and_save_image(1280, 720, ai_prompt, 111, t_kr, t_en, font_choice, title_size, y_pos_percent, line_spacing, "designed_main.png")
            if img_t:
                st.session_state.img_res_tiktok = design_and_save_image(720, 1280, ai_prompt, 222, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, "designed_tiktok.png")
            for i in range(num_s_img):
                path = design_and_save_image(720, 1280, ai_prompt, 333+i, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, f"designed_short_{i+1}.png")
                st.session_state.img_res_shorts.append(path)
            st.success("🎉 이미지 생성 완료! 아래에서 다운로드 하세요.")
            
    # 결과 보여주기 및 다운로드
    if st.session_state.get('img_res_main') or st.session_state.get('img_res_tiktok') or st.session_state.get('img_res_shorts'):
        cols = st.columns(3)
        idx = 0
        if st.session_state.get('img_res_main'):
            with cols[idx%3]:
                st.image(st.session_state.img_res_main, caption="메인 (16:9)")
                with open(st.session_state.img_res_main, "rb") as f: st.download_button("⬇️ 다운로드", f, "Main_Cover.png", "image/png", use_container_width=True)
            idx+=1
        if st.session_state.get('img_res_tiktok'):
            with cols[idx%3]:
                st.image(st.session_state.img_res_tiktok, caption="틱톡 (9:16)")
                with open(st.session_state.img_res_tiktok, "rb") as f: st.download_button("⬇️ 다운로드", f, "TikTok_Cover.png", "image/png", use_container_width=True)
            idx+=1
        if st.session_state.get('img_res_shorts'):
            for i, p in enumerate(st.session_state.img_res_shorts):
                with cols[idx%3]:
                    st.image(p, caption=f"쇼츠 {i+1} (9:16)")
                    with open(p, "rb") as f: st.download_button(f"⬇️ 다운로드", f, f"Shorts_{i+1}_Cover.png", "image/png", use_container_width=True, key=f"btn_s_{i}")
                idx+=1

# ------------------------------------------
# [탭 3] 비디오 팩토리 (기존 100% 원상복구)
# ------------------------------------------
with tab3:
    st.header("🎬 비디오 렌더링 & 업로드")
    st.write("2단계에서 다운받은 이미지와 음원을 올려서 최종 영상을 렌더링합니다.")
    
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        st.subheader("1. 파일 업로드")
        v_audio = st.file_uploader("🎧 음원 (WAV/MP3)", type=['wav', 'mp3'], key="v_aud")
        
        st.divider()
        v_gen_main = st.checkbox("📺 메인 영상 생성", value=True)
        v_img_main = st.file_uploader("메인 이미지 (16:9)", type=['png','jpg'], key="v_m") if v_gen_main else None
        
        v_gen_tiktok = st.checkbox("📱 틱톡 풀영상 생성", value=False)
        v_img_tiktok = st.file_uploader("틱톡 이미지 (9:16)", type=['png','jpg'], key="v_t") if v_gen_tiktok else None
        
        st.divider()
        v_num_shorts = st.slider("✂️ 쇼츠 개수", 0, 6, 0)
        v_img_shorts = []
        for i in range(v_num_shorts):
            v_img_shorts.append(st.file_uploader(f"쇼츠 {i+1} 이미지", type=['png','jpg'], key=f"v_s_{i}"))

        st.divider()
        v_lyrics = st.text_area("📝 스크롤 가사 ([] 자동삭제)", height=150)
        v_sync = st.text_input("⏱️ 시작 싱크 (예: 00:15)")

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
                    st.session_state.clean_lyrics = final_clean_lyrics 

                    step_title.markdown("#### 🎵 음원 분석 중...")
                    audio_path = "temp_audio.wav"
                    with open(audio_path, "wb") as f: f.write(v_audio.getbuffer())
                    
                    full_audio = AudioFileClip(audio_path)
                    audio_duration = full_audio.duration
                    
                    manual_start = parse_time_to_sec(v_sync)
                    if manual_start >= 0: final_start_sec = manual_start
                    else: final_start_sec = analyze_audio_start(full_audio)

                    if v_gen_main:
                        step_title.markdown("#### 🎬 [1단계] 메인 영상 렌더링 중...")
                        main_img_path = "temp_main_img.png"
                        process_user_image(v_img_main, 1280, 720, main_img_path)
                        main_video_path = "output_main_video.mp4"
                        logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
                        generate_video_with_lyrics(main_img_path, full_audio, final_clean_lyrics, main_video_path, logger, 1280, 720, final_start_sec)
                        st.session_state.main_video_path = main_video_path 
                        del logger; gc.collect() 

                    if v_gen_tiktok:
                        step_title.markdown("#### 📱 [2단계] 틱톡 영상 렌더링 중...")
                        tiktok_img_path = "temp_tiktok_img.png"
                        process_user_image(v_img_tiktok, 720, 1280, tiktok_img_path)
                        tiktok_video_path = "output_tiktok_video.mp4"
                        logger = StreamlitProgressLogger(progress_bar, progress_text, "틱톡 영상")
                        generate_video_with_lyrics(tiktok_img_path, full_audio, final_clean_lyrics, tiktok_video_path, logger, 720, 1280, final_start_sec)
                        st.session_state.tiktok_video_path = tiktok_video_path 
                        del logger; gc.collect()

                    if v_num_shorts > 0:
                        step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 중...")
                        highlight_times = find_highlights_lite(audio_duration, v_num_shorts)
                        for i, start_time in enumerate(highlight_times):
                            step_title.markdown(f"#### ✂️ [4단계] 쇼츠 {i+1}/{v_num_shorts} 렌더링 중...")
                            shorts_img_path = f"temp_shorts_img_{i}.png"
                            process_user_image(v_img_shorts[i], 720, 1280, shorts_img_path)
                            
                            short_dur = min(random.randint(35, 55), audio_duration - start_time)
                            if short_dur < 5: short_dur = 5 
                            
                            sub_audio = full_audio.subclip(start_time, start_time + short_dur)
                            fade_dur = min(1.5, short_dur / 3.0)
                            sub_audio = sub_audio.fx(afx.audio_fadein, fade_dur).fx(afx.audio_fadeout, fade_dur)
                            
                            temp_wav_path = f"temp_short_{i}.wav"
                            sub_audio.write_audiofile(temp_wav_path, fps=44100, logger=None)
                            fresh_audio = AudioFileClip(temp_wav_path)
                            shorts_video_path = f"output_shorts_{i+1}.mp4"
                            logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                            
                            generate_static_video(shorts_img_path, fresh_audio, shorts_video_path, logger)
                            
                            fresh_audio.close()
                            if os.path.exists(temp_wav_path): os.remove(temp_wav_path)
                            st.session_state.shorts_paths.append(shorts_video_path)
                            del logger, fresh_audio, sub_audio; gc.collect() 

                    full_audio.close()
                    st.session_state.is_completed = True
                    step_title.markdown("#### ✨ 모든 작업 완료! 아래에서 결과물을 다운로드하세요.")

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

        # ==========================================
        # 🎉 렌더링 완료 영상 미리보기 및 다운로드
        # ==========================================
        if st.session_state.is_completed:
            st.success("🎉 비디오 렌더링이 성공적으로 완료되었습니다!")
            
            # 🔥 각 영상에 다운로드 버튼 추가
            tabs = st.tabs(["📺 메인", "📱 틱톡"] + [f"✂️ 쇼츠 {i+1}" for i in range(len(st.session_state.shorts_paths))])
            
            t_idx = 0
            if st.session_state.main_video_path:
                with tabs[t_idx]:
                    st.video(st.session_state.main_video_path)
                    with open(st.session_state.main_video_path, "rb") as f:
                        st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", f, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4", use_container_width=True)
                t_idx += 1
                
            if st.session_state.tiktok_video_path:
                with tabs[t_idx]:
                    st.video(st.session_state.tiktok_video_path)
                    with open(st.session_state.tiktok_video_path, "rb") as f:
                        st.download_button("⬇️ 틱톡 풀영상 다운로드 (.mp4)", f, file_name=f"{st.session_state.base_name}_TikTok.mp4", mime="video/mp4", use_container_width=True)
                t_idx += 1
                    
            for i, shorts_path in enumerate(st.session_state.shorts_paths):
                with tabs[t_idx]:
                    st.video(shorts_path)
                    with open(shorts_path, "rb") as f:
                        st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드 (.mp4)", f, file_name=f"{st.session_state.base_name}_Short_{i+1}.mp4", mime="video/mp4", use_container_width=True)
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
                    yt_title = st.text_input("📝 영상 제목", value=f"[{st.session_state.base_name}] 은혜로운 찬양")
                    yt_desc = st.text_area("📜 영상 설명", value="할렐루야! 은혜로운 찬양입니다.\n#CCM #찬양", height=150)
                    yt_tags = st.text_input("🏷️ 검색 태그", value="CCM, 찬양, 예배")
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
                                
                            success, msg = upload_to_youtube(s_vid_path, yt_title, yt_desc, yt_tags, p_map[privacy_ui], final_pub)
                            if success: st.success(msg); st.balloons()
                            else: st.error(msg)