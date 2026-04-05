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

st.set_page_config(page_title="AI 뮤직비디오 팩토리 (3-Step)", page_icon="🎬", layout="wide")

# ==========================================
# 💾 세션 상태 및 메모리 유지
# ==========================================
if 'audio_path' not in st.session_state: st.session_state.audio_path = ""
if 'title_kr' not in st.session_state: st.session_state.title_kr = ""
if 'title_en' not in st.session_state: st.session_state.title_en = ""
if 'img_main' not in st.session_state: st.session_state.img_main = None
if 'img_tiktok' not in st.session_state: st.session_state.img_tiktok = None
if 'img_shorts' not in st.session_state: st.session_state.img_shorts = []
if 'clean_lyrics' not in st.session_state: st.session_state.clean_lyrics = ""

# ==========================================
# 🔠 폰트 다운로드 세팅 (3가지 스타일)
# ==========================================
font_links = {
    "나눔고딕 (깔끔/기본)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강렬/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (세련/모던)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

for name, (file_name, url) in font_links.items():
    if not os.path.exists(file_name):
        try:
            with open(file_name, "wb") as f: f.write(requests.get(url).content)
        except: pass

# ==========================================
# 🌟 유틸리티 함수 모음
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
# 🖼️ 이미지 렌더링 & 제목 디자인 함수
# ==========================================
def create_designed_image(width, height, prompt, seed, custom_file, title_kr, title_en, font_choice, title_size, y_pos_percent, line_spacing):
    # 1. 배경 이미지 확보 (업로드 vs AI)
    if custom_file is not None:
        img = Image.open(custom_file).convert("RGBA")
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
    else:
        safe_prompt = re.sub(r'\s+', ' ', prompt).strip()
        encoded_prompt = urllib.parse.quote(safe_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            response.raise_for_status()
            img_path = f"temp_ai_{seed}.jpg"
            with open(img_path, "wb") as f: f.write(response.content)
            img = Image.open(img_path).convert("RGBA")
        except:
            img = Image.new("RGBA", (width, height), (35, 35, 40, 255))
            
    # 2. 텍스트 디자인 그리기
    draw = ImageDraw.Draw(img)
    font_file = font_links[font_choice][0]
    
    font_kr = ImageFont.truetype(font_file, title_size)
    font_en = ImageFont.truetype(font_file, int(title_size * 0.65)) # 영문은 한글의 65% 크기
    
    y_center = height * (y_pos_percent / 100.0)
    
    # 높이 계산
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
        
    out_path = f"final_img_{width}x{height}_{seed}.png"
    img.convert("RGB").save(out_path)
    img.close()
    return out_path

# ==========================================
# 🎬 비디오 렌더링 엔진 (메인/틱톡/쇼츠)
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
        
    lyric_font = ImageFont.truetype(font_links["나눔고딕 (깔끔/기본)"][0], lyric_font_size)
    line_spacing = 2.0
    
    try:
        h_dummy = ImageDraw.Draw(Image.new("RGB",(10,10))).textbbox((0,0), "A", font=lyric_font)[3]
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

# ==========================================
# 🚀 유튜브 업로드 함수
# ==========================================
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
        else: return False, "토큰이 만료되었거나 유효하지 않습니다."

    try:
        youtube = build("youtube", "v3", credentials=creds)
        body = {"snippet": {"title": title, "description": description, "tags": [t.strip() for t in tags.split(",") if t.strip()], "categoryId": "10"}, "status": {"privacyStatus": privacy_status}}
        if publish_at: body["status"]["publishAt"] = publish_at
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        return True, f"🎉 업로드 성공! 링크: https://youtu.be/{response.get('id')}"
    except Exception as e: return False, f"업로드 중 오류 발생: {e}"

# ==========================================
# 🖥️ 앱 UI 및 탭 구성
# ==========================================
tab1, tab2, tab3 = st.tabs(["📝 1. 수노(Suno) 가사/프롬프트 생성", "🖼️ 2. 이미지 팩토리 (커스텀 디자인)", "🎬 3. 비디오 렌더링 & 업로드"])

# ------------------------------------------
# TAB 1: 수노 가사/프롬프트 생성
# ------------------------------------------
with tab1:
    st.header("📝 수노(Suno AI) 메타태그 & 가사 생성기")
    st.write("Suno AI에 입력할 스타일 프롬프트와 가사 구조를 쉽게 짜보세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        suno_genre = st.text_input("🎸 장르/스타일 (예: K-pop, Acoustic Ballad, CCM Worship)")
        suno_mood = st.text_input("✨ 분위기 (예: emotional, uplifting, holy)")
        suno_voice = st.selectbox("🎤 보컬 스타일", ["male vocal", "female vocal", "choir", "duet"])
    
    st.info(f"💡 **Suno Style Prompt 추천:**\n\n`{suno_genre}, {suno_mood}, {suno_voice}`")
    
    st.subheader("가사 에디터 (메타태그 삽입)")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("[Intro] 추가"): st.session_state.suno_lyrics = st.session_state.get('suno_lyrics', '') + "\n[Intro]\n"
    if c2.button("[Verse] 추가"): st.session_state.suno_lyrics = st.session_state.get('suno_lyrics', '') + "\n[Verse]\n"
    if c3.button("[Chorus] 추가"): st.session_state.suno_lyrics = st.session_state.get('suno_lyrics', '') + "\n[Chorus]\n"
    if c4.button("[Bridge] 추가"): st.session_state.suno_lyrics = st.session_state.get('suno_lyrics', '') + "\n[Bridge]\n"
    if c5.button("[Outro] 추가"): st.session_state.suno_lyrics = st.session_state.get('suno_lyrics', '') + "\n[Outro]\n"
    
    suno_lyrics = st.text_area("여기에 가사를 작성하고 Suno AI에 복사하세요.", value=st.session_state.get('suno_lyrics', ''), height=300)
    st.session_state.suno_lyrics = suno_lyrics

# ------------------------------------------
# TAB 2: 이미지 팩토리
# ------------------------------------------
with tab2:
    st.header("🖼️ 이미지 팩토리 (제목 디자인 & 다운로드)")
    st.write("수노에서 만든 음원을 올리면 제목이 자동 파싱됩니다. 이미지를 커스텀하고 다운로드하세요.")
    
    uploaded_audio = st.file_uploader("🎧 수노 음원 업로드 (필수, WAV/MP3)", type=['wav', 'mp3'])
    
    if uploaded_audio:
        # 파일 임시 저장 및 제목 파싱
        audio_path = "temp_factory_audio.wav"
        with open(audio_path, "wb") as f: f.write(uploaded_audio.getbuffer())
        st.session_state.audio_path = audio_path
        
        base_name = os.path.splitext(uploaded_audio.name)[0]
        st.session_state.base_name = base_name
        
        parts = base_name.split('_')
        st.session_state.title_kr = parts[0] if len(parts) > 0 else base_name
        st.session_state.title_en = parts[1] if len(parts) > 1 else ""
        
    col_t1, col_t2 = st.columns(2)
    with col_t1: title_kr = st.text_input("📌 한글 제목 (Title 1)", value=st.session_state.title_kr)
    with col_t2: title_en = st.text_input("📌 영문 제목 (Title 2)", value=st.session_state.title_en)
    
    st.divider()
    st.subheader("🎨 제목 디자인 옵션")
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1: font_choice = st.selectbox("폰트 스타일", list(font_links.keys()))
    with col_d2: title_size = st.slider("폰트 크기 (메인 기준)", 30, 150, 70)
    with col_d3: y_pos_percent = st.slider("Y축 위치 (%) - 50이 정중앙", 0, 100, 20)
    with col_d4: line_spacing = st.slider("한글/영문 줄간격", 0, 50, 15)
    
    st.divider()
    st.subheader("🖼️ 생성할 이미지 설정 (AI 프롬프트 OR 직접 업로드)")
    ai_prompt = st.text_input("🤖 AI 이미지 프롬프트 (업로드 파일이 없으면 이걸로 그립니다)", "beautiful sunlight, cinematic landscape, masterpiece")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        gen_main = st.checkbox("📺 메인 (가로 16:9)", value=True)
        img_up_main = st.file_uploader("메인 배경 업로드 (선택)", type=['jpg','png'])
    with col_i2:
        gen_tiktok = st.checkbox("📱 틱톡 (세로 9:16)", value=False)
        img_up_tiktok = st.file_uploader("틱톡 배경 업로드 (선택)", type=['jpg','png'])
    with col_i3:
        num_shorts = st.slider("✂️ 쇼츠 이미지 (세로) 개수", 0, 6, 0)
        img_up_shorts = []
        for i in range(num_shorts):
            img_up_shorts.append(st.file_uploader(f"쇼츠 {i+1} 배경 (선택)", type=['jpg','png'], key=f"s_img_{i}"))

    if st.button("✨ 이미지 생성 및 디자인 적용", type="primary", use_container_width=True):
        if not uploaded_audio: st.error("음원 파일을 먼저 업로드해주세요!")
        else:
            with st.spinner("이미지를 생성하고 제목을 디자인하는 중입니다..."):
                if gen_main:
                    path = create_designed_image(1280, 720, ai_prompt, 111, img_up_main, title_kr, title_en, font_choice, title_size, y_pos_percent, line_spacing)
                    st.session_state.img_main = path
                if gen_tiktok:
                    # 세로는 폰트크기 자동비례 조정 (약 75%)
                    path = create_designed_image(720, 1280, ai_prompt, 222, img_up_tiktok, title_kr, title_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing)
                    st.session_state.img_tiktok = path
                
                st.session_state.img_shorts = []
                for i in range(num_shorts):
                    path = create_designed_image(720, 1280, ai_prompt, 333+i, img_up_shorts[i], title_kr, title_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing)
                    st.session_state.img_shorts.append(path)
                    
            st.success("🎉 이미지 디자인 완료! 아래에서 확인하고 다운로드하세요.")
            
    # 이미지 결과 및 다운로드 버튼 표시
    if st.session_state.img_main or st.session_state.img_tiktok or st.session_state.img_shorts:
        st.subheader("📥 완성된 이미지 미리보기 & 다운로드")
        res_cols = st.columns(3)
        col_idx = 0
        
        if st.session_state.img_main:
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_main, caption="📺 메인 이미지 (16:9)")
                with open(st.session_state.img_main, "rb") as f:
                    st.download_button("⬇️ 메인 다운로드", f, file_name=f"{title_kr}_Main.png", mime="image/png")
            col_idx += 1
            
        if st.session_state.img_tiktok:
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_tiktok, caption="📱 틱톡 이미지 (9:16)")
                with open(st.session_state.img_tiktok, "rb") as f:
                    st.download_button("⬇️ 틱톡 다운로드", f, file_name=f"{title_kr}_TikTok.png", mime="image/png")
            col_idx += 1
            
        for i, s_path in enumerate(st.session_state.img_shorts):
            with res_cols[col_idx % 3]:
                st.image(s_path, caption=f"✂️ 쇼츠 {i+1} 이미지 (9:16)")
                with open(s_path, "rb") as f:
                    st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드", f, file_name=f"{title_kr}_Short_{i+1}.png", mime="image/png", key=f"dl_s_{i}")
            col_idx += 1

# ------------------------------------------
# TAB 3: 비디오 렌더링 & 업로드
# ------------------------------------------
with tab3:
    st.header("🎬 비디오 렌더링 & 다이렉트 업로드")
    st.write("2단계에서 만들어진 이미지를 바탕으로 영상을 제작합니다.")
    
    lyrics_input = st.text_area("📝 스크롤용 가사 입력 (메인/틱톡 적용, [] 자동삭제)", height=150)
    sync_start = st.text_input("⏱️ 스크롤 시작 싱크 (예: 00:15)", placeholder="비워두면 AI가 맞춥니다.")
    
    if st.button("🚀 비디오 팩토리 가동", type="primary", use_container_width=True):
        if not st.session_state.audio_path: st.error("2단계 탭에서 음원 파일을 업로드해주세요.")
        elif not (st.session_state.img_main or st.session_state.img_tiktok or st.session_state.img_shorts):
            st.error("2단계 탭에서 먼저 이미지를 생성해주세요.")
        else:
            status_box = st.container()
            with status_box:
                st.markdown("### 📡 렌더링 모니터링")
                step_title = st.empty()
                progress_bar = st.progress(0)
                progress_text = st.empty()

            try:
                st.session_state.main_video_path = ""
                st.session_state.tiktok_video_path = ""
                st.session_state.shorts_paths = []
                st.session_state.is_completed = False
                
                final_clean_lyrics = re.sub(r'\[.*?\]', '', lyrics_input)
                st.session_state.clean_lyrics = final_clean_lyrics 
                
                full_audio = AudioFileClip(st.session_state.audio_path)
                audio_dur = full_audio.duration
                
                manual_start = parse_time_to_sec(sync_start)
                if manual_start >= 0: final_start_sec = manual_start
                else: final_start_sec = analyze_audio_start(full_audio)

                # 메인 비디오
                if st.session_state.img_main:
                    step_title.markdown(f"#### 🎬 [1단계] 메인 영상 렌더링 중...")
                    v_path = "output_main.mp4"
                    logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
                    generate_video_with_lyrics(st.session_state.img_main, full_audio, final_clean_lyrics, v_path, logger, 1280, 720, final_start_sec)
                    st.session_state.main_video_path = v_path
                    del logger; gc.collect()

                # 틱톡 비디오
                if st.session_state.img_tiktok:
                    step_title.markdown(f"#### 📱 [2단계] 틱톡 풀영상 렌더링 중...")
                    v_path = "output_tiktok.mp4"
                    logger = StreamlitProgressLogger(progress_bar, progress_text, "틱톡 영상")
                    generate_video_with_lyrics(st.session_state.img_tiktok, full_audio, final_clean_lyrics, v_path, logger, 720, 1280, final_start_sec)
                    st.session_state.tiktok_video_path = v_path
                    del logger; gc.collect()

                # 쇼츠 비디오
                num_s = len(st.session_state.img_shorts)
                if num_s > 0:
                    step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 구간 계산 중...")
                    h_times = find_highlights_lite(audio_dur, num_s)
                    
                    for i, s_time in enumerate(h_times):
                        step_title.markdown(f"#### ✂️ 하이라이트 쇼츠 {i+1}/{num_s} 제작 중...")
                        dur = min(random.randint(35, 55), audio_dur - s_time)
                        if dur < 5: dur = 5
                        
                        sub_audio = full_audio.subclip(s_time, s_time + dur)
                        fade = min(1.5, dur / 3.0)
                        sub_audio = sub_audio.fx(afx.audio_fadein, fade).fx(afx.audio_fadeout, fade)
                        
                        temp_wav = f"temp_short_{i}.wav"
                        sub_audio.write_audiofile(temp_wav, fps=44100, logger=None)
                        fresh_audio = AudioFileClip(temp_wav)
                        
                        v_path = f"output_short_{i+1}.mp4"
                        logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                        generate_static_video(st.session_state.img_shorts[i], fresh_audio, v_path, logger)
                        
                        fresh_audio.close()
                        if os.path.exists(temp_wav): os.remove(temp_wav)
                        st.session_state.shorts_paths.append(v_path)
                        del logger, fresh_audio, sub_audio; gc.collect()

                full_audio.close()
                st.session_state.is_completed = True
                step_title.markdown("#### ✨ 모든 영상 렌더링 완료!")

            except Exception as e: st.error(f"오류 발생: {e}")

    # 결과 및 유튜브 업로드
    if st.session_state.is_completed:
        st.divider()
        st.success("🎉 모든 영상이 성공적으로 생성되었습니다!")
        
        tab_names = []
        if st.session_state.main_video_path: tab_names.append("📺 메인 영상")
        if st.session_state.tiktok_video_path: tab_names.append("📱 틱톡 풀영상")
        for i in range(len(st.session_state.shorts_paths)): tab_names.append(f"✂️ 쇼츠 {i+1}")
            
        v_tabs = st.tabs(tab_names)
        
        t_idx = 0
        if st.session_state.main_video_path:
            with v_tabs[t_idx]:
                st.video(st.session_state.main_video_path)
                with open(st.session_state.main_video_path, "rb") as f:
                    st.download_button("⬇️ 메인 영상 다운로드", f, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")
            t_idx += 1
        if st.session_state.tiktok_video_path:
            with v_tabs[t_idx]:
                st.video(st.session_state.tiktok_video_path)
                with open(st.session_state.tiktok_video_path, "rb") as f:
                    st.download_button("⬇️ 틱톡 영상 다운로드", f, file_name=f"{st.session_state.base_name}_TikTok.mp4", mime="video/mp4")
            t_idx += 1
        for i, path in enumerate(st.session_state.shorts_paths):
            with v_tabs[t_idx]:
                st.video(path)
                with open(path, "rb") as f:
                    st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드", f, file_name=f"{st.session_state.base_name}_Short_{i+1}.mp4", mime="video/mp4")
            t_idx += 1

        st.divider()
        st.header("🚀 유튜브 다이렉트 업로드")
        
        c_f1, c_f2 = st.columns(2)
        with c_f1: client_file = st.file_uploader("🔑 client_secrets.json", type=['json'])
        with c_f2: token_file = st.file_uploader("🎫 token.json", type=['json'])

        if client_file and token_file:
            with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
            with open("token.json", "wb") as f: f.write(token_file.getbuffer())
                
            upload_opts = {}
            if st.session_state.main_video_path: upload_opts["📺 메인 영상"] = st.session_state.main_video_path
            if st.session_state.tiktok_video_path: upload_opts["📱 틱톡 영상"] = st.session_state.tiktok_video_path
            for i, p in enumerate(st.session_state.shorts_paths): upload_opts[f"✂️ 쇼츠 {i+1}"] = p
                
            if upload_opts:
                sel_vid_key = st.selectbox("📌 업로드할 영상 선택", list(upload_opts.keys()))
                sel_vid_path = upload_opts[sel_vid_key]
                yt_title = st.text_input("📝 영상 제목", value=f"[{st.session_state.title_kr}] 은혜로운 찬양")
                yt_desc = st.text_area("📜 영상 설명", value="할렐루야! 은혜로운 찬양입니다.\n#CCM #찬양", height=150)
                yt_tags = st.text_input("🏷️ 태그", value="CCM, 찬양, 예배")
                privacy_ui = st.selectbox("🔒 상태", ["비공개", "일부 공개", "공개", "예약 업로드"])
                
                up_d = None; up_t = None
                if privacy_ui == "예약 업로드":
                    cd, ct = st.columns(2)
                    with cd: up_d = st.date_input("🗓️ 날짜")
                    with ct: up_t = st.time_input("⏰ KST 시간")
                
                if st.button("🔥 유튜브로 전송", type="primary"):
                    with st.spinner("업로드 중입니다..."):
                        p_map = {"비공개":"private", "일부 공개":"unlisted", "공개":"public", "예약 업로드":"private"}
                        pub_at = None
                        if privacy_ui == "예약 업로드":
                            dt_utc = datetime.combine(up_d, up_t, tzinfo=timezone(timedelta(hours=9))).astimezone(timezone.utc)
                            pub_at = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")
                            
                        success, msg = upload_to_youtube(sel_vid_path, yt_title, yt_desc, yt_tags, p_map[privacy_ui], pub_at)
                        if success: st.success(msg); st.balloons()
                        else: st.error(msg)