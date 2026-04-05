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

# --- 🔠 폰트 다운로드 ---
font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
font_path = "NanumGothicBold.ttf"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f: f.write(requests.get(font_url).content)

st.title("🕊️ 은혜로운 찬양 영상 팩토리 (AI 자동 생성판)")
st.write("이미지를 업로드하지 않으면 AI가 자동으로 앨범 커버를 생성하고 제목을 그려줍니다.")

# ==========================================
# 🌟 진행률 로거
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

# ==========================================
# 🎯 AI 초정밀 프롬프트 사전 (부활!)
# ==========================================
pop_genres = {"선택안함": "", "팝 (Pop)": "pop music vibe", "감성 발라드": "emotional ballad vibe", "정통 발라드": "classic korean ballad", "어쿠스틱 발라드": "acoustic guitar ballad", "인디 팝": "indie pop aesthetic", "인디 포크": "indie folk", "인디 라틴": "indie latin", "모던 락": "modern rock band", "얼터너티브 락": "alternative rock", "드림팝": "dream pop", "신스팝": "synthpop", "시티팝": "retro city pop", "알앤비 / 소울": "smooth R&B soul", "네오 소울": "neo soul", "재즈": "classic jazz", "보사노바": "bossa nova", "로파이": "lofi hip hop", "시네마틱 / OST": "cinematic soundtrack"}
ccm_genres = {"선택안함": "", "전통 찬송가": "traditional hymns", "모던 워십": "modern christian worship", "라이브 워십": "live worship concert", "어쿠스틱 찬양": "acoustic worship", "가스펠 콰이어": "joyful gospel choir", "CCM 발라드": "emotional christian ballad", "워십 락": "christian rock", "로파이 워십": "lofi christian worship", "피아노 묵상곡": "peaceful piano worship", "시네마틱 오케스트라 찬양": "epic orchestral worship"}
moods = {"선택안함": "", "경건하고 홀리한": "holy, reverent", "은혜롭고 따뜻한": "graceful, warm", "몽환적이고 신비로운": "ethereal, dreamy", "차분하고 서정적인": "lyrical, calm", "우울하고 쓸쓸한": "melancholic", "밝고 희망찬": "joyful, uplifting", "에너지 넘치는": "energetic"}
styles = {"선택안함": "", "실사 사진 (초고화질)": "photorealistic, 8k resolution", "수채화": "soft watercolor", "유화": "classic oil painting", "지브리 애니메이션 풍": "studio ghibli style", "신카이 마코토 풍": "makoto shinkai style", "픽사/디즈니 3D 풍": "3D render, pixar style", "빈티지 일러스트": "vintage illustration"}
lightings = {"선택안함": "", "성스러운 빛": "god rays, volumetric lighting", "따스한 자연광": "natural sunlight", "눈부신 역광": "backlit, lens flare", "부드러운 스튜디오 조명": "soft studio lighting", "어두운 밤": "nighttime, soft moonlight", "화려한 네온사인": "vibrant neon lighting", "골든 아워 (노을빛)": "golden hour lighting"}
colors = {"선택안함": "", "황금빛 톤": "golden color palette", "따뜻한 웜톤": "warm color palette", "차가운 쿨톤": "cool color palette", "흑백 / 모노톤": "black and white", "부드러운 파스텔": "soft pastel colors", "빈티지": "vintage colors"}
cameras = {"선택안함": "", "클로즈업": "extreme close-up shot", "바스트 샷": "medium shot", "전신 샷": "full body shot", "풍경 위주": "wide landscape shot", "로우 앵글": "low angle shot", "하이 앵글": "high angle shot", "드론 뷰": "bird's eye view"}
times = {"선택안함": "", "이른 새벽": "early dawn", "밝은 아침": "bright morning", "화창한 정오": "midday", "늦은 오후": "late afternoon", "해질녘 (골든아워)": "sunset", "푸른 저녁 (블루아워)": "blue hour", "깊은 밤 (자정)": "midnight"}
weathers = {"선택안함": "", "맑고 쾌청한": "clear weather", "구름이 예쁜 날": "fluffy white clouds", "비 내리는": "raining", "눈 내리는": "snowing", "안개 낀": "thick fog", "흩날리는 벚꽃잎": "falling cherry blossom petals", "무지개가 뜬 날": "beautiful rainbow"}
eras = {"선택안함": "", "현대 / 도심": "modern day", "근미래 / 사이버펑크": "futuristic, cyberpunk city", "90년대 / Y2K": "1990s retro aesthetic", "80년대": "1980s aesthetic", "중세 판타지": "medieval fantasy world", "빅토리아 시대": "victorian era"}
effects = {"선택안함": "", "필름 노이즈": "heavy film grain", "빛 번짐": "lens flare", "아웃포커싱": "shallow depth of field", "세피아 필터": "sepia filter", "빛바랜 폴라로이드": "polaroid effect"}

# ==========================================
# ⚙️ 시간 변환 및 분석 유틸리티
# ==========================================
def parse_time_to_sec(time_str):
    try:
        time_str = time_str.strip()
        if not time_str: return -1 
        if ":" in time_str:
            m, s = time_str.split(":")
            return int(m) * 60 + int(s)
        else:
            return int(time_str)
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
# 🖼️ 하이브리드 이미지/제목 생성 함수 (업로드 OR AI 생성)
# ==========================================
def create_cover_image(prompt, width, height, title_text, output_path, seed, custom_img_file=None):
    if custom_img_file is not None:
        # 사용자 업로드 이미지 처리
        img = Image.open(custom_img_file).convert("RGBA")
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
        # AI 이미지 생성
        safe_prompt = re.sub(r'\s+', ' ', prompt).strip()
        encoded_prompt = urllib.parse.quote(safe_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            with open(output_path, "wb") as f: f.write(response.content)
            img = Image.open(output_path).convert("RGBA")
        except Exception:
            # AI 서버 에러 시 기본 다크 배경 생성
            img = Image.new("RGBA", (width, height), (35, 35, 40, 255))
            
    # 🔥 이미지 위에 제목(Title) 쓰기
    draw = ImageDraw.Draw(img)
    title_font_size = 45 if width == 1280 else 35
    title_font = ImageFont.truetype(font_path, title_font_size)
    x = width / 2
    y = height * 0.15 # 상단 15% 위치에 고정
    
    draw.multiline_text((x, y), title_text, font=title_font, fill="white", stroke_width=4, stroke_fill="black", align="center", anchor="ma")
    img.convert("RGB").save(output_path)
    img.close()

# ==========================================
# 🔥 1. 메인/틱톡 가사 스크롤 엔진 (순수 NumPy)
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

    # 🌟 틱톡(세로)일 경우 폰트 확대 & 하단 스크롤
    if width == 720 and height == 1280:
        lyric_font_size = 24  
        window_top = int(height * 0.60) 
    else:
        lyric_font_size = 22  
        window_top = int(height * 0.40) 
        
    lyric_font = ImageFont.truetype(font_path, lyric_font_size)
    line_spacing = 2.0
    
    try:
        dummy_bbox = ImageDraw.Draw(Image.new("RGB", (10,10))).textbbox((0,0), "A", font=lyric_font)
        line_height = dummy_bbox[3] - dummy_bbox[1]
    except:
        line_height = lyric_font_size
        
    step_y = line_height * line_spacing
    total_text_height = int(len(lines) * step_y)
    
    window_bottom = int(height * 0.95) 
    window_height = window_bottom - window_top

    long_img_height = window_height + total_text_height + window_height
    long_lyrics_img = Image.new("RGBA", (width, int(long_img_height)), (0, 0, 0, 0))
    draw_long = ImageDraw.Draw(long_lyrics_img)
    
    for i, line in enumerate(lines):
        lyric_y = window_height + (i * step_y)
        draw_long.text((width / 2, lyric_y), line, font=lyric_font, fill="white", stroke_width=2, stroke_fill="black", align="center", anchor="ma")

    long_lyrics_np = np.array(long_lyrics_img)
    long_lyrics_img.close()

    fade_mask = np.ones((window_height, width, 1), dtype=np.float32)
    fade_height = int(window_height * 0.4) 
    for y in range(fade_height):
        fade_mask[y, :, 0] = y / fade_height
    for y in range(window_height - fade_height, window_height):
        fade_mask[y, :, 0] = (window_height - y) / fade_height

    bg_slice = base_img_np[window_top:window_bottom, :, :].astype(np.float32)

    def make_frame(t):
        if t < start_sec: progress = 0.0 
        else:
            scroll_duration = duration - start_sec
            if scroll_duration <= 0: progress = 1.0
            else: progress = min(1.0, max(0.0, (t - start_sec) / scroll_duration))
            
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

# ==========================================
# 🔥 2. 쇼츠 전용 초경량 엔진 
# ==========================================
def generate_static_video(image_path, audio_clip, output_path, logger):
    clip = ImageClip(image_path).set_duration(audio_clip.duration).set_audio(audio_clip)
    clip.write_videofile(output_path, fps=2, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
    clip.close()

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

    if not os.path.exists("token.json"): return False, "token.json 파일이 없습니다."

    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as token: token.write(creds.to_json())
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
            "status": {"privacyStatus": privacy_status}
        }
        if publish_at: body["status"]["publishAt"] = publish_at

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        return True, f"🎉 업로드 성공! 링크: https://youtu.be/{response.get('id')}"
    except Exception as e:
        return False, f"업로드 중 오류 발생: {e}"

# ==========================================
# 🖥️ 사이드바 & 파일 업로드 UI 구성
# ==========================================
st.sidebar.header("1. 기본 설정 (음원/가사)")
uploaded_audio = st.sidebar.file_uploader("🎧 음원 파일 (WAV, MP3)", type=['wav', 'mp3'])
lyrics = st.sidebar.text_area("📝 가사 입력 (메인 및 틱톡 풀영상 스크롤 적용)", height=150)
sync_start = st.sidebar.text_input("⏱️ 시작 싱크 (예: 00:15)", placeholder="비워두면 AI가 맞춥니다.")

st.sidebar.divider()
st.sidebar.header("2. 영상 생성 항목 및 배경 업로드")
st.sidebar.info("💡 이미지를 업로드하지 않으면 AI가 자동으로 생성합니다.")

generate_main = st.sidebar.checkbox("📺 유튜브 메인 (가로 16:9) 생성", value=True)
uploaded_main_img = None
if generate_main:
    uploaded_main_img = st.sidebar.file_uploader("📺 가로 메인용 배경 (선택)", type=['jpg', 'jpeg', 'png'])

generate_tiktok = st.sidebar.checkbox("📱 틱톡 풀영상 (세로 9:16) 생성", value=False)
uploaded_tiktok_img = None
if generate_tiktok:
    uploaded_tiktok_img = st.sidebar.file_uploader("📱 틱톡 풀영상 전용 배경 (선택)", type=['jpg', 'jpeg', 'png'])

num_shorts = st.sidebar.slider("✂️ 하이라이트 쇼츠 (가사X) 개수", min_value=0, max_value=4, value=0)
uploaded_shorts_imgs = []
if num_shorts > 0:
    for i in range(num_shorts):
        upl = st.sidebar.file_uploader(f"✂️ 쇼츠 {i+1} 전용 배경 (선택)", type=['jpg', 'jpeg', 'png'], key=f"short_upload_{i}")
        uploaded_shorts_imgs.append(upl)

# ==========================================
# 🎨 앨범 커버 AI 초정밀 연출 옵션 (부활)
# ==========================================
st.header("🎨 AI 앨범 커버 자동 생성 옵션")
st.write("이미지를 직접 업로드하지 않은 영상은 아래 설정에 맞춰 AI가 그려줍니다.")
subject = st.text_input("🎯 메인 주제/사물 (선택)", placeholder="예: 창밖을 바라보는 고양이 (영어로 쓰면 더 정확합니다)")

col_g1, col_g2 = st.columns(2)
with col_g1: pop_choice = st.selectbox("🎧 대중음악 장르 (CCM 선택 시 무시됨)", list(pop_genres.keys()))
with col_g2: ccm_choice = st.selectbox("⛪ CCM 장르", list(ccm_genres.keys()))

col1, col2 = st.columns(2)
with col1:
    mood_choice = st.selectbox("✨ 분위기", list(moods.keys()))
    style_choice = st.selectbox("🖌️ 그림 스타일", list(styles.keys()))
with col2:
    light_choice = st.selectbox("💡 조명 느낌", list(lightings.keys()))
    color_choice = st.selectbox("🌈 색감", list(colors.keys()))

with st.expander("🎬 디테일 연출 설정 (선택사항)"):
    col3, col4 = st.columns(2)
    with col3:
        camera_choice = st.selectbox("🎥 카메라 앵글", list(cameras.keys()))
        time_choice = st.selectbox("⏰ 시간대", list(times.keys()))
        weather_choice = st.selectbox("☁️ 날씨", list(weathers.keys()))
    with col4:
        era_choice = st.selectbox("🏰 배경 시대", list(eras.keys()))
        effect_choice = st.selectbox("✨ 특수효과", list(effects.keys()))

# ==========================================
# 🚀 렌더링 시작 및 실시간 모니터링
# ==========================================
if st.button("🚀 비디오 렌더링 시작", use_container_width=True):
    if uploaded_audio is None:
        st.error("⚠️ 음원 파일을 업로드해주세요.")
    elif not generate_main and not generate_tiktok and num_shorts == 0:
        st.error("⚠️ 최소 하나 이상의 영상을 생성하도록 선택해주세요.")
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
            display_title = f"{base_name.split('_')[0]}\n{base_name.split('_')[1]}" if '_' in base_name else base_name
            st.session_state.base_name = base_name
            
            final_clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)
            st.session_state.clean_lyrics = final_clean_lyrics 

            # AI 프롬프트 생성
            selected_genre = ccm_genres[ccm_choice] if ccm_choice != "선택안함" else pop_genres[pop_choice]
            prompt_parts = [
                subject, selected_genre, moods[mood_choice], styles[style_choice], 
                lightings[light_choice], colors[color_choice], cameras[camera_choice],
                times[time_choice], weathers[weather_choice], eras[era_choice], effects[effect_choice],
                "masterpiece", "best quality", "4k resolution"
            ]
            final_prompt = ", ".join([p for p in prompt_parts if p])

            step_title.markdown("#### 🎵 음원 분석 및 준비 중...")
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

            # [작업 1] 메인 영상 렌더링
            if generate_main:
                step_title.markdown(f"#### 🎬 [1단계] 유튜브 메인 영상(16:9) 렌더링 중...")
                main_img_path = "temp_main_img.jpg"
                create_cover_image(final_prompt, 1280, 720, display_title, main_img_path, seed=123, custom_img_file=uploaded_main_img)
                
                main_video_path = "output_main_video.mp4"
                main_logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
                generate_video_with_lyrics(main_img_path, full_audio, final_clean_lyrics, main_video_path, main_logger, 1280, 720, start_sec=final_start_sec)
                
                st.session_state.main_video_path = main_video_path 
                del main_logger; gc.collect() 

            # [작업 2] 틱톡 풀영상 렌더링
            if generate_tiktok:
                step_title.markdown(f"#### 📱 [2단계] 틱톡 풀영상(9:16) 렌더링 중...")
                tiktok_img_path = "temp_tiktok_img.jpg"
                create_cover_image(final_prompt, 720, 1280, display_title, tiktok_img_path, seed=456, custom_img_file=uploaded_tiktok_img)
                
                tiktok_video_path = "output_tiktok_video.mp4"
                tiktok_logger = StreamlitProgressLogger(progress_bar, progress_text, "틱톡 영상")
                generate_video_with_lyrics(tiktok_img_path, full_audio, final_clean_lyrics, tiktok_video_path, tiktok_logger, 720, 1280, start_sec=final_start_sec)
                
                st.session_state.tiktok_video_path = tiktok_video_path 
                del tiktok_logger; gc.collect()

            # [작업 3] 쇼츠 추출 및 렌더링
            if num_shorts > 0:
                progress_bar.progress(0)
                progress_text.empty()
                step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 구간 계산 중...")
                highlight_times = find_highlights_lite(audio_duration, num_shorts)
                
                for i, start_time in enumerate(highlight_times):
                    progress_bar.progress(0)
                    step_title.markdown(f"#### ✂️ [4단계] 하이라이트 쇼츠 {i+1}/{num_shorts} 제작 중...")
                    
                    shorts_img_path = f"temp_shorts_img_{i}.jpg"
                    create_cover_image(final_prompt, 720, 1280, display_title, shorts_img_path, seed=random.randint(1000, 9999), custom_img_file=uploaded_shorts_imgs[i])
                    
                    short_dur = min(random.randint(35, 55), audio_duration - start_time)
                    if short_dur < 5: short_dur = 5 
                    
                    sub_audio = full_audio.subclip(start_time, start_time + short_dur)
                    fade_dur = min(1.5, short_dur / 3.0)
                    sub_audio = sub_audio.fx(afx.audio_fadein, fade_dur).fx(afx.audio_fadeout, fade_dur)
                    
                    temp_wav_path = f"temp_short_{i}.wav"
                    sub_audio.write_audiofile(temp_wav_path, fps=44100, logger=None)
                    
                    fresh_audio = AudioFileClip(temp_wav_path)
                    shorts_video_path = f"output_shorts_{i+1}.mp4"
                    shorts_logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                    
                    generate_static_video(shorts_img_path, fresh_audio, shorts_video_path, shorts_logger)
                    
                    fresh_audio.close()
                    if os.path.exists(temp_wav_path): os.remove(temp_wav_path)
                        
                    st.session_state.shorts_paths.append(shorts_video_path)
                    del shorts_logger, fresh_audio, sub_audio; gc.collect() 

            full_audio.close()
            st.session_state.is_completed = True
            step_title.markdown("#### ✨ 모든 작업 완료! 아래에서 확인하세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# ==========================================
# 🎉 완료 화면 및 다운로드 / 유튜브 업로드
# ==========================================
if st.session_state.is_completed:
    st.divider()
    
    valid_files_exist = False
    if st.session_state.main_video_path and os.path.exists(st.session_state.main_video_path): valid_files_exist = True
    if st.session_state.tiktok_video_path and os.path.exists(st.session_state.tiktok_video_path): valid_files_exist = True
    for p in st.session_state.shorts_paths:
        if os.path.exists(p): valid_files_exist = True
            
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
                    st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4", use_container_width=True)
            tab_idx += 1
            
        if st.session_state.tiktok_video_path:
            with tabs[tab_idx]:
                st.video(st.session_state.tiktok_video_path)
                with open(st.session_state.tiktok_video_path, "rb") as file:
                    st.download_button("⬇️ 틱톡 풀영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_TikTok.mp4", mime="video/mp4", use_container_width=True)
            tab_idx += 1
                
        for i, shorts_path in enumerate(st.session_state.shorts_paths):
            with tabs[tab_idx]:
                st.video(shorts_path)
                with open(shorts_path, "rb") as file:
                    st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Shorts_{i+1}.mp4", mime="video/mp4", use_container_width=True)
            tab_idx += 1

        st.divider()
        st.header("🚀 유튜브 다이렉트 업로드")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1: client_file = st.file_uploader("🔑 client_secrets.json 업로드", type=['json'])
        with col_f2: token_file = st.file_uploader("🎫 token.json 업로드 (PC에서 생성한 파일)", type=['json'])

        if client_file and token_file:
            with open("client_secrets.json", "wb") as f: f.write(client_file.getbuffer())
            with open("token.json", "wb") as f: f.write(token_file.getbuffer())
                
            upload_options = {}
            if st.session_state.main_video_path and os.path.exists(st.session_state.main_video_path):
                upload_options["📺 메인 영상 (가로)"] = st.session_state.main_video_path
            if st.session_state.tiktok_video_path and os.path.exists(st.session_state.tiktok_video_path):
                upload_options["📱 틱톡 풀영상 (세로)"] = st.session_state.tiktok_video_path
            for i, p in enumerate(st.session_state.shorts_paths):
                if os.path.exists(p): upload_options[f"✂️ 쇼츠 {i+1} (세로)"] = p
                
            if upload_options:
                selected_vid_key = st.selectbox("📌 업로드할 영상 선택", list(upload_options.keys()))
                selected_vid_path = upload_options[selected_vid_key]
                yt_title = st.text_input("📝 영상 제목", value=f"[{st.session_state.base_name}] 은혜로운 찬양 플레이리스트")
                ccm_desc_template = f"""할렐루야! 오늘 함께 나눌 찬양은 '{st.session_state.base_name}' 입니다. 🌿\n\n지치고 상한 마음, 예배의 자리를 사모하는 모든 분들께 이 찬양이 작은 위로와 평안이 되기를 소망합니다.\n가사를 묵상하며 주님의 크신 사랑과 은혜를 깊이 경험하는 귀한 시간 되시길 기도합니다. \n\n항상 주님 안에서 승리하시고, 오늘 하루도 말씀과 기도로 나아가는 복된 하루 되세요! 🙏\n\n🔔 구독과 좋아요는 은혜로운 찬양을 나누는 데 큰 힘이 됩니다. 💖\n\n#CCM #찬양 #예배 #은혜 #위로 #기도 #기독교 #교회 #찬양추천 #플레이리스트"""
                yt_desc = st.text_area("📜 영상 설명", value=ccm_desc_template, height=300)
                ccm_tags = "CCM, 찬양, 예배, 은혜, 기독교, 교회, 찬송가, 워십, 복음성가, 기도, 묵상, 힐링찬양, 위로, 평안, 찬양추천, 플레이리스트, worship, praise, 주일예배, 특송, 은혜로운찬양, 아침찬양, 수면찬양"
                yt_tags = st.text_input("🏷️ 검색 태그 (쉼표로 구분)", value=ccm_tags)
                privacy_ui = st.selectbox("🔒 공개 상태", ["비공개 (Private)", "일부 공개 (Unlisted)", "공개 (Public)", "예약 업로드 (Scheduled)"])
                
                upload_date = None; upload_time = None
                if privacy_ui == "예약 업로드 (Scheduled)":
                    st.info("💡 예약 시간은 반드시 '현재 시각보다 미래'여야 합니다.")
                    col_d, col_t = st.columns(2)
                    with col_d: upload_date = st.date_input("🗓️ 날짜 선택")
                    with col_t: upload_time = st.time_input("⏰ 한국 시간(KST) 기준 시간 선택")
                
                if st.button("🔥 유튜브 채널로 전송", type="primary"):
                    with st.spinner("유튜브 서버로 안전하게 업로드 중입니다... (수 분 소요됨)"):
                        privacy_map = {"비공개 (Private)": "private", "일부 공개 (Unlisted)": "unlisted", "공개 (Public)": "public", "예약 업로드 (Scheduled)": "private"}
                        final_privacy = privacy_map[privacy_ui]
                        final_publish_at = None
                        if privacy_ui == "예약 업로드 (Scheduled)":
                            kst_tz = timezone(timedelta(hours=9))
                            dt_kst = datetime.combine(upload_date, upload_time, tzinfo=kst_tz)
                            dt_utc = dt_kst.astimezone(timezone.utc)
                            final_publish_at = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")
                            
                        success, msg = upload_to_youtube(selected_vid_path, yt_title, yt_desc, yt_tags, final_privacy, publish_at=final_publish_at)
                        if success:
                            st.success(msg)
                            st.balloons()
                        else: st.error(msg)
        else: st.warning("위 2개의 인증 파일을 모두 업로드해야 버튼이 나타납니다.")