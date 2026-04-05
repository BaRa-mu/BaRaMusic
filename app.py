import streamlit as st
import requests
import os
import re
import random
import gc
import numpy as np
import urllib.parse
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

# AI 가사/프롬프트 생성용 세션
if 'gen_title_kr' not in st.session_state: st.session_state.gen_title_kr = ""
if 'gen_title_en' not in st.session_state: st.session_state.gen_title_en = ""
if 'gen_lyrics' not in st.session_state: st.session_state.gen_lyrics = ""
if 'gen_prompt' not in st.session_state: st.session_state.gen_prompt = ""

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
# 🌟 유틸리티 함수
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

def generate_ai_text(prompt):
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        response = requests.get(url, timeout=30)
        return response.text
    except Exception as e:
        return f"생성 오류: {e}"

def extract_eng(text):
    if "(" in text and ")" in text: return text.split("(")[1].replace(")", "").strip()
    return text.strip()

# ==========================================
# 🖼️ 이미지 팩토리: 디자인 생성 함수
# ==========================================
def design_and_save_image(width, height, prompt, seed, title_kr, title_en, font_choice, title_size, y_pos_percent, line_spacing, output_path, custom_file=None):
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
# 🎬 완벽 비디오 렌더링 엔진
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
    
    try: h_dummy = ImageDraw.Draw(Image.new("RGB", (10,10))).textbbox((0,0), "A", font=lyric_font)[3]
    except: h_dummy = lyric_font_size
        
    step_y = int(h_dummy * line_spacing)
    total_text_height = int(len(lines) * step_y)
    window_bottom = int(height * 0.95) 
    window_height = window_bottom - window_top

    fade_height = int(step_y * 1.5)
    if fade_height * 2 > window_height: fade_height = window_height // 2 
    text_start_y = window_height - int(step_y * 0.8)

    long_img_height = text_start_y + total_text_height + window_height
    long_lyrics_img = Image.new("RGBA", (width, int(long_img_height)), (0, 0, 0, 0))
    draw_long = ImageDraw.Draw(long_lyrics_img)
    
    for i, line in enumerate(lines):
        draw_long.text((width / 2, text_start_y + (i * step_y)), line, font=lyric_font, fill="white", stroke_width=2, stroke_fill="black", anchor="ma")

    long_lyrics_np = np.array(long_lyrics_img)
    long_lyrics_img.close()

    fade_mask = np.ones((window_height, width, 1), dtype=np.float32)
    for y in range(fade_height): fade_mask[y, :, 0] = y / fade_height
    for y in range(window_height - fade_height, window_height): fade_mask[y, :, 0] = (window_height - y) / fade_height

    bg_slice = base_img_np[window_top:window_bottom, :, :].astype(np.float32)
    max_scroll = text_start_y + total_text_height

    def make_frame(t):
        if t < start_sec: 
            progress = 0.0; global_alpha = 0.0 
        else:
            scroll_dur = duration - start_sec
            progress = 1.0 if scroll_dur <= 0 else min(1.0, max(0.0, (t - start_sec) / scroll_dur))
            global_alpha = min(1.0, (t - start_sec) / 1.0) 
            
        viewport_y = int(progress * max_scroll)
        src_np = long_lyrics_np[viewport_y : viewport_y + window_height, :, :]
        alpha = (src_np[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis] * fade_mask * global_alpha
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
tab1, tab2, tab3 = st.tabs(["📝 1. 수노(Suno) 원클릭 프롬프트", "🎨 2. 이미지 팩토리 (디자인)", "🎬 3. 비디오 렌더링 & 업로드"])

# ------------------------------------------
# [탭 1] 수노 전용 가사 프롬프트 복사기
# ------------------------------------------
with tab1:
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("메뉴를 선택하고 생성 버튼을 누르면 수노(Suno)에 바로 붙여넣기 할 수 있는 완벽한 텍스트가 만들어집니다.")
    
    suno_subject = st.text_input("🎯 곡의 주제/메시지 (필수 입력, 예: 지친 하루의 위로, 첫사랑의 설렘)")
    
    # 🎸 20개 이상의 장르 리스트
    suno_pop_list = ["선택안함", "K-pop (케이팝)", "팝 발라드 (Pop Ballad)", "어쿠스틱 포크 (Acoustic Folk)", "인디 팝 (Indie Pop)", "R&B / Soul (알앤비/소울)", "모던 락 (Modern Rock)", "로파이 힙합 (Lo-Fi Hip Hop)", "시티팝 (City Pop)", "신스팝 (Synthpop)", "재즈 (Jazz)", "보사노바 (Bossa Nova)", "블루스 (Blues)", "컨트리 (Country)", "트로트 (Trot)", "일렉트로닉 (EDM)", "펑크 (Funk)", "디스코 (Disco)", "드림팝 (Dream Pop)", "얼터너티브 락 (Alt Rock)", "앰비언트 (Ambient)", "클래식 크로스오버 (Classical Crossover)"]
    suno_ccm_list = ["선택안함", "모던 워십 (Modern Worship)", "전통 찬송가 편곡 (Traditional Hymns)", "가스펠 콰이어 (Gospel Choir)", "CCM 발라드 (CCM Ballad)", "워십 락 (Christian Rock)", "어쿠스틱 찬양 (Acoustic Worship)", "로파이 워십 (Lofi Worship)", "피아노 묵상 (Piano Prayer)", "시네마틱 워십 (Cinematic Worship)", "어린이 찬양 (Children's Worship)", "흑인 영가 (Black Gospel)", "소울 CCM (Soul CCM)", "재즈 워십 (Jazz Worship)", "컨트리 가스펠 (Country Gospel)", "아카펠라 (A Cappella)", "켈틱 워십 (Celtic Worship)", "일렉트로닉 워십 (EDM Worship)", "레게 CCM (Reggae CCM)", "라틴 가스펠 (Latin Gospel)", "스포큰 워드 기도 (Spoken Word)"]
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: s_pop = st.selectbox("🎧 대중음악 장르 (CCM 선택 시 무시됨)", suno_pop_list)
    with col_s2: s_ccm = st.selectbox("⛪ CCM / 예배음악 장르", suno_ccm_list)

    # ✨ 15개 이상의 분위기, 템포, 보컬, 악기 리스트
    suno_moods_list = ["선택안함", "감성적인 (Emotional)", "경건하고 거룩한 (Holy, Reverent)", "기쁘고 희망찬 (Joyful, Uplifting)", "평화롭고 차분한 (Peaceful, Calm)", "에너지 넘치는 (Energetic)", "어둡고 무거운 (Dark, Heavy)", "몽환적인 (Dreamy, Ethereal)", "웅장한 (Epic, Majestic)", "쓸쓸하고 우울한 (Melancholic, Sad)", "따뜻하고 포근한 (Warm, Comforting)", "신비로운 (Mysterious)", "향수를 부르는 (Nostalgic)", "사랑스러운 (Romantic, Sweet)", "결연하고 비장한 (Determined)", "치유되는 (Healing, Soothing)", "흥겨운 (Groovy, Fun)"]
    suno_tempo_list = ["선택안함", "매우 느린 (Very Slow)", "느린 (Slow tempo)", "중간 느린 (Moderately Slow)", "중간 (Medium tempo)", "조금 빠른 (Allegretto)", "빠른 (Fast tempo)", "매우 빠른 (Very Fast)", "경쾌한 업템포 (Up-tempo)", "점점 빠르게 (Accelerando)", "점점 느리게 (Ritardando)", "자유로운 템포 (Rubato)", "안정적인 8비트 (Steady 8-beat)", "그루비한 16비트 (Groovy 16-beat)", "다이나믹 박자 (Dynamic Tempo)", "바운스 템포 (Bounce Tempo)", "왈츠풍 3/4박자 (Waltz Time)"]
    suno_inst_list = ["선택안함", "어쿠스틱 기타 (Acoustic Guitar)", "피아노 (Piano)", "신디사이저 (Synthesizer)", "일렉기타 (Electric Guitar)", "웅장한 오케스트라 (Orchestra)", "아름다운 현악기 (Strings)", "금관악기 (Brass)", "무거운 베이스 (Heavy Bass)", "어쿠스틱 밴드 (Acoustic Band)", "로파이 비트 (Lo-Fi Beats)", "808 드럼 (808 Drum Machine)", "파이프 오르간 (Pipe Organ)", "하프 (Harp)", "첼로 (Cello)"]
    suno_vocals_list = [
        "선택안함",
        "--- [ 👨 남성 보컬 ] ---",
        "남성 솔로 (Male vocal)", "허스키한 남성 (Husky male vocal)", "맑고 청아한 남성 (Clear male vocal)", "깊고 중후한 저음 남성 (Deep bass male vocal)", "따뜻한 중저음 남성 (Warm baritone male vocal)", "파워풀한 고음 남성 (Powerful high-pitch male vocal)", "부드럽고 감미로운 남성 (Soft and sweet male vocal)", "소울풀한 흑인 남성 (Soulful black male vocal)", "속삭이는 듯한 남성 (Whispering male vocal)", "거칠고 락적인 남성 (Gritty rock male vocal)", "소년 보컬 (Boy vocal)",
        "--- [ 👩 여성 보컬 ] ---",
        "여성 솔로 (Female vocal)", "허스키한 여성 (Husky female vocal)", "맑고 청아한 여성 (Clear female vocal)", "깊고 풍부한 저음 여성 (Deep rich female vocal)", "따뜻한 중저음 여성 (Warm alto female vocal)", "파워풀한 고음 여성 (Powerful belting female vocal)", "부드럽고 감미로운 여성 (Soft and sweet female vocal)", "소울풀한 흑인 여성 (Soulful black female vocal)", "속삭이는 듯한 여성 (Whispering female vocal)", "몽환적인 에테리얼 여성 (Ethereal dreamy female vocal)", "소녀 보컬 (Girl vocal)",
        "--- [ 👩‍❤️‍👨 듀엣 보컬 ] ---",
        "남녀 듀엣 (Male and female duet)", "감미로운 남녀 듀엣 (Sweet male and female duet)", "파워풀한 남녀 듀엣 (Powerful male and female duet)", "애절한 남녀 듀엣 (Sorrowful male and female duet)", "속삭이는 남녀 듀엣 (Whispering male and female duet)", "웅장한 남녀 듀엣 (Epic male and female duet)", "어쿠스틱 남녀 듀엣 (Acoustic male and female duet)", "남남 듀엣 (Male to male duet)", "감미로운 남남 듀엣 (Sweet male to male duet)", "파워풀한 남남 듀엣 (Powerful male to male duet)", "화음 위주 남남 듀엣 (Harmonious male to male duet)", "여여 듀엣 (Female to female duet)", "맑은 여여 듀엣 (Clear female to female duet)", "파워풀한 여여 듀엣 (Powerful female to female duet)", "화음 위주 여여 듀엣 (Harmonious female to female duet)", "소년 소녀 듀엣 (Boy and girl duet)", "중저음 남녀 듀엣 (Low pitch male and female duet)", "허스키 보컬 듀엣 (Husky vocal duet)", "소울풀 듀엣 (Soulful vocal duet)", "R&B 스타일 듀엣 (R&B style duet)", "팝 스타일 듀엣 (Pop style duet)",
        "--- [ 🎼 합창 및 기타 ] ---",
        "대규모 가스펠 합창 (Massive gospel choir)", "어린이 합창단 (Children's choir)", "장엄한 클래식 합창 (Majestic classical choir)", "잔잔한 아카펠라 합창 (Calm a cappella choir)", "남성 합창단 (Male choir)", "여성 합창단 (Female choir)", "천상의 목소리 합창 (Angelic ethereal choir)", "아프리칸 소울 합창 (African soul choir)", "현대 워십 코러스 (Modern worship chorus)", "보컬 없음 / 연주곡 (Instrumental only)"
    ]

    col_s3, col_s4 = st.columns(2)
    with col_s3: s_mood = st.selectbox("✨ 곡의 분위기", suno_moods_list)
    with col_s4: s_tempo = st.selectbox("🥁 템포 (속도)", suno_tempo_list)
    
    col_s5, col_s6 = st.columns(2)
    with col_s5: s_inst = st.selectbox("🎹 주요 악기", suno_inst_list)
    with col_s6: s_vocal = st.selectbox("🎤 보컬 구성", [v for v in suno_vocals_list if not v.startswith("---")])

    # Suno 프롬프트 영문 조합
    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    prompt_parts = []
    if s_selected_genre: prompt_parts.append(extract_eng(s_selected_genre))
    if s_mood != "선택안함": prompt_parts.append(extract_eng(s_mood))
    if s_tempo != "선택안함": prompt_parts.append(extract_eng(s_tempo))
    if s_inst != "선택안함": prompt_parts.append(extract_eng(s_inst))
    if s_vocal != "선택안함": prompt_parts.append(extract_eng(s_vocal))
    final_suno_prompt = ", ".join(prompt_parts)[:1000] # 수노 글자수 1000자 제한 방지

    if st.button("✨ 수노 전용 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 수노 양식에 맞춰 완벽한 가사를 작성하고 있습니다..."):
                query = f"주제: '{suno_subject}', 장르: {s_selected_genre}, 분위기: {s_mood}, 템포: {s_tempo}, 보컬: {s_vocal}. 이 곡의 한글제목, 영문제목, 그리고 수노(Suno)에 바로 복사해서 쓸 가사를 써줘. 가사에는 반드시 [Intro], [Verse 1], [Chorus], [Verse 2], [Bridge], [Guitar Solo], [Outro] 같은 대괄호 메타태그를 곡의 흐름에 맞게 적재적소에 넣어줘. 응답형식:\n한글제목:\n영문제목:\n가사:\n"
                res_text = generate_ai_text(query)
                
                match_kr = re.search(r"한글제목:\s*(.+)", res_text)
                match_en = re.search(r"영문제목:\s*(.+)", res_text)
                match_lyrics = re.search(r"가사:\s*(.*)", res_text, re.DOTALL)
                
                st.session_state.gen_title_kr = match_kr.group(1).strip() if match_kr else "제목 생성 실패"
                st.session_state.gen_title_en = match_en.group(1).strip() if match_en else ""
                st.session_state.gen_lyrics = match_lyrics.group(1).strip() if match_lyrics else res_text
                st.session_state.gen_prompt = final_suno_prompt
                
            st.success("🎉 작사가 완료되었습니다! 아래 박스 우측 상단의 📋 아이콘을 클릭하여 수노에 바로 붙여넣기 하세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 원클릭 복사존")
    st.write("오직 복사만을 위해 준비된 깔끔한 공간입니다.")

    st.write("**1. 🎵 Title (곡 제목)**")
    combined_title = f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}" if st.session_state.gen_title_en else st.session_state.gen_title_kr
    st.code(combined_title if combined_title.strip('_') else "주제를 적고 생성 버튼을 누르세요.", language="text")
    
    st.write("**2. 🎸 Style of Music (음악 스타일)**")
    st.code(st.session_state.get('gen_prompt', final_suno_prompt) if st.session_state.get('gen_prompt', final_suno_prompt) else "옵션을 선택하세요.", language="text")

    st.write("**3. 📝 Lyrics (가사)**")
    st.code(st.session_state.get('gen_lyrics', '생성된 가사가 여기에 표시됩니다.'), language="text")

# ------------------------------------------
# [탭 2] 이미지 팩토리 (초대형 이미지 프롬프트)
# ------------------------------------------
img_pop_genres = {"선택안함": "", "팝 (Pop)": "pop music vibe", "감성 발라드": "emotional ballad vibe", "정통 발라드": "classic korean ballad", "어쿠스틱 발라드": "acoustic guitar ballad", "인디 팝": "indie pop aesthetic", "인디 포크": "indie folk", "인디 라틴": "indie latin", "모던 락": "modern rock band", "얼터너티브 락": "alternative rock", "드림팝": "dream pop", "신스팝": "synthpop", "시티팝": "retro city pop", "알앤비 / 소울": "smooth R&B soul", "네오 소울": "neo soul", "재즈": "classic jazz club", "보사노바": "bossa nova relaxing", "로파이": "lofi hip hop aesthetic", "시네마틱 / OST": "cinematic soundtrack", "EDM / 일렉트로닉": "EDM festival vibe", "레트로 펑크": "retro funk groove", "컨트리": "country music vibe", "블루스": "blues club vibe", "클래식 크로스오버": "classical crossover elegant", "레게": "reggae beach vibe"}
img_ccm_genres = {"선택안함": "", "전통 찬송가": "traditional hymns", "모던 워십": "modern christian worship", "라이브 워십": "live worship concert", "어쿠스틱 찬양": "acoustic worship", "가스펠 콰이어": "joyful gospel choir", "CCM 발라드": "emotional christian ballad", "워십 락": "christian rock", "로파이 워십": "lofi christian worship", "피아노 묵상곡": "peaceful piano worship", "시네마틱 오케스트라 찬양": "epic orchestral worship", "어린이 찬양": "joyful children sunday school", "흑인 영가": "black gospel soulful", "재즈 워십": "jazz worship elegant", "컨트리 가스펠": "country gospel peaceful", "아카펠라": "a cappella worship choir", "켈틱 워십": "celtic christian worship", "EDM 워십": "youth worship energetic", "라틴 워십": "latin worship joyful", "스포큰 워드 기도": "deep prayer spoken word"}
img_moods = {"선택안함": "", "경건하고 홀리한": "holy, reverent, divine presence", "은혜롭고 따뜻한": "graceful, warm, comforting", "몽환적이고 신비로운": "ethereal, dreamy, magical", "차분하고 서정적인": "lyrical, poetic, calm", "우울하고 쓸쓸한": "melancholic, somber, lonely", "밝고 희망찬": "joyful, uplifting, bright", "에너지 넘치는 (파워풀)": "energetic, dynamic", "웅장하고 에픽한": "epic, majestic, awe-inspiring", "아련한 (향수를 부르는)": "nostalgic, longing, sentimental", "사랑스럽고 포근한": "romantic, sweet, cozy", "비장하고 결연한": "determined, resolute, cinematic", "위로가 되는 (힐링)": "healing, soothing, peaceful therapy", "신비롭고 어두운": "dark fantasy, mysterious, eerie", "생동감 넘치는": "lively, vibrant, animated", "고독한 (혼자인)": "solitary, isolated, quiet"}
img_styles = {"선택안함": "", "실사 사진 (초고화질)": "photorealistic, 8k resolution", "수채화 (감성적인)": "soft watercolor painting", "유화 (명화 느낌)": "classic oil painting", "지브리 애니메이션 풍": "studio ghibli style, anime art", "신카이 마코토 풍 (빛의 마술)": "makoto shinkai style, breathtaking sky", "픽사/디즈니 3D 풍": "3D render, pixar style", "빈티지 일러스트": "vintage 1950s illustration", "스테인드글라스 아트": "beautiful stained glass art", "미니멀리즘 (깔끔한)": "minimalist, clean lines, flat design", "레트로 픽셀 아트": "16-bit retro pixel art", "연필 스케치 / 드로잉": "detailed pencil sketch", "동양화 / 수묵화": "traditional korean painting", "사이버펑크 네온 아트": "cyberpunk digital art", "팝아트 (강렬한)": "pop art style, bold colors", "페이퍼 크래프트 (종이공예)": "paper craft, origami style 3d"}
img_lightings = {"선택안함": "", "성스러운 빛 (God Rays)": "god rays, volumetric lighting", "따스한 자연광 (오후)": "natural sunlight, bright afternoon", "눈부신 역광 (실루엣 강조)": "backlit, strong silhouette, lens flare", "부드러운 스튜디오 조명": "soft studio lighting, diffuse light", "어두운 밤 (달빛/별빛)": "nighttime, soft moonlight, starlight", "골든 아워 (노을빛)": "golden hour lighting, warm glow", "블루 아워 (새벽빛)": "blue hour lighting, cool dusk", "화려한 네온사인": "vibrant neon lighting, cyberpunk glow", "안개 낀 빛 (산란광)": "foggy, soft diffused light through mist", "영화 같은 극적 조명": "cinematic lighting, chiaroscuro, high contrast", "촛불 조명 (따뜻한)": "candlelight, warm glowing illumination", "스테인드글라스 투과광": "colorful light filtered through stained glass", "스포트라이트 (집중조명)": "single dramatic spotlight in darkness", "햇살 비치는 창가": "sunlight streaming through a window", "오로라 빛": "aurora borealis lighting, magical glow"}
img_colors = {"선택안함": "", "황금빛 톤 (성스러운)": "golden color palette", "따뜻한 웜톤 (가을 느낌)": "warm color palette, autumn colors", "차가운 쿨톤 (새벽/겨울)": "cool color palette, winter blues", "흑백 / 모노톤": "black and white, monochrome", "부드러운 파스텔": "soft pastel colors", "빈티지 (빛바랜 느낌)": "vintage colors, sepia tone", "강렬하고 쨍한 색감": "vivid colors, high contrast, vibrant", "어둡고 칙칙한 무드": "muted colors, dark palette", "에메랄드/그린 톤": "emerald green tones, lush nature", "모노크로매틱 블루": "monochromatic blue, deep sea", "로즈 골드/핑크 톤": "rose gold palette, soft pinks", "네온/사이버펑크 색감": "neon pink, cyan, cyberpunk palette", "어스 톤 (자연의 색)": "earth tones, brown, green, beige", "레드/오렌지 (석양)": "fiery red and orange sunset palette", "홀로그래픽 (무지개빛)": "holographic, iridescent colors"}
img_cameras = {"선택안함": "", "클로즈업 (사물/표정)": "extreme close-up shot", "바스트 샷 (상반신)": "medium shot, bust shot", "전신 샷 (Full body)": "full body shot", "풍경 위주 (Wide shot)": "wide landscape shot", "로우 앵글 (아래에서 위로)": "low angle shot, looking up", "하이 앵글 (위에서 아래로)": "high angle shot, looking down", "드론 뷰 (하늘에서)": "bird's eye view, drone shot", "어안 렌즈 (왜곡된 뷰)": "fisheye lens effect", "실루엣 샷": "silhouette shot against light", "1인칭 시점 (POV)": "first person view, POV shot", "파노라마 (넓은 시야)": "panoramic shot, ultra wide angle", "매크로 (초접사)": "macro photography, extreme detail", "어깨 너머 샷": "over the shoulder shot", "대칭 구도 (Symmetrical)": "perfectly symmetrical composition", "더치 앵글 (기울어진)": "dutch angle, tilted horizon"}
img_times = {"선택안함": "", "이른 새벽 (동틀 무렵)": "early dawn, breaking light", "밝은 아침": "bright morning", "화창한 정오": "midday, clear bright sky", "늦은 오후 (나른한)": "late afternoon", "해질녘 (골든아워)": "sunset, beautiful evening sky", "푸른 저녁 (블루아워)": "blue hour, twilight", "별이 뜨는 초저녁": "early evening, first stars", "깊은 밤 (자정)": "midnight, dark night sky", "비현실적인 우주/은하수": "ethereal night, glowing galaxy sky", "시간 불상 (초현실)": "timeless, surreal dimension", "비 오는 밤": "rainy night, wet reflections", "눈 내리는 아침": "snowy morning, winter daylight", "태양이 작열하는 한낮": "scorching sun, heatwave noon", "보름달이 뜬 밤": "full moon night, bright lunar light", "일식/월식의 순간": "solar eclipse, rare celestial event"}
img_weathers = {"선택안함": "", "맑고 쾌청한": "clear weather, sunny", "구름이 예쁜 날": "fluffy white clouds", "비 내리는 (촉촉한)": "raining, wet streets", "폭우 / 천둥번개": "heavy rain, thunderstorm, lightning", "눈 내리는 (포근한)": "snowing, winter wonderland", "거친 눈보라": "blizzard, heavy snowstorm", "안개 낀 (몽환적인)": "thick fog, mysterious mist", "바람 부는 (흩날리는)": "windy, blowing hair and clothes", "흩날리는 벚꽃잎": "falling cherry blossom petals", "흩날리는 가을 낙엽": "falling autumn leaves", "무지개가 뜬 날": "beautiful rainbow after rain", "황사/모래폭풍": "sandstorm, dusty wind", "흐리고 우중충한": "overcast, cloudy gloomy sky", "반짝이는 햇살 조각": "sun glints, sparkling light", "우박/얼음비": "hailstorm, freezing rain"}
img_eras = {"선택안함": "", "현대 / 도심 (2020년대)": "modern day, contemporary", "근미래 / 사이버펑크": "futuristic, cyberpunk city", "90년대 / Y2K 레트로": "1990s retro aesthetic, y2k", "80년대 / 카세트 감성": "1980s aesthetic, vaporwave", "중세 판타지 (기사/마법)": "medieval fantasy world", "고대 / 성서 시대": "ancient times, biblical era, historical", "빅토리아 시대 (19세기)": "victorian era, 19th century", "일제강점기 / 개화기": "1920s to 1930s vintage korean aesthetic", "르네상스 시대": "renaissance era, classic", "포스트 아포칼립스 (폐허)": "post-apocalyptic, overgrown ruins", "선사시대 / 원시 자연": "prehistoric, untouched pristine nature", "스팀펑크 (기계/증기)": "steampunk aesthetic, gears and brass", "우주 시대 (우주선/행성)": "space age, sci-fi, distant planet", "서부 개척 시대 (카우보이)": "wild west era, western", "로코코/바로크 시대": "rococo era, extravagant luxury"}
img_effects = {"선택안함": "", "필름 노이즈 (거친 느낌)": "heavy film grain, 35mm film", "빛 번짐 (렌즈 플레어)": "lens flare, light leak", "아웃포커싱 (배경 흐림)": "shallow depth of field, bokeh", "글리치 (디지털 깨짐)": "digital glitch effect, distortion", "몽환적인 블러 (소프트포커스)": "soft focus, dreamlike blur", "비네팅 (가장자리 어두움)": "vignette, dark edges", "이중 노출 (오버랩)": "double exposure art", "세피아 필터 (옛날 사진)": "sepia filter, aged photo", "프리즘 / 무지개 반사": "prism light leak, rainbow reflections", "빛바랜 폴라로이드 느낌": "polaroid effect, instant camera", "스피드 블러 (움직임 강조)": "motion blur, high speed", "만화책 느낌 (하프톤)": "comic book halftone effect", "수채화 번짐 효과": "watercolor bleed effect", "네온 글로우 (발광)": "neon glowing effect", "컬러 스플래시 (특정색 강조)": "color splash effect, selective color"}

with tab2:
    st.header("🎨 이미지 팩토리 (자동 제목 파싱 및 렌더링)")
    st.write("수노에서 완성한 음원(`한글제목_영문제목.mp3`)을 올리면 제목이 자동으로 분리되어 입력됩니다.")
    
    audio_for_parsing = st.file_uploader("🎧 수노 다운로드 음원 업로드", type=['wav', 'mp3'])
    
    t_kr = st.session_state.gen_title_kr
    t_en = st.session_state.gen_title_en
    if audio_for_parsing:
        base = os.path.splitext(audio_for_parsing.name)[0]
        parts = base.split('_')
        t_kr = parts[0]
        t_en = parts[1] if len(parts) > 1 else ""
        
    c_t1, c_t2 = st.columns(2)
    with c_t1: t_kr = st.text_input("📌 렌더링용 한글 제목 (수정 가능)", value=t_kr)
    with c_t2: t_en = st.text_input("📌 렌더링용 영문 제목 (수정 가능)", value=t_en)
    
    st.divider()
    st.subheader("⚙️ 2-1. 제목 텍스트 디자인 옵션")
    d1, d2, d3, d4 = st.columns(4)
    with d1: font_choice = st.selectbox("글씨체", list(font_links.keys()))
    with d2: title_size = st.slider("메인 글씨 크기", 30, 120, 60)
    with d3: y_pos_percent = st.slider("Y축 위치 (%)", 5, 95, 15)
    with d4: line_spacing = st.slider("한영 줄간격", 0, 50, 15)
    
    st.divider()
    st.subheader("🎨 2-2. AI 배경 이미지 자동 생성 옵션")
    st.write("직접 이미지를 업로드하지 않으면 아래 설정대로 초고화질 AI 그림을 그려줍니다.")
    img_subject = st.text_input("🎯 배경에 그릴 사물/주제 (예: 창밖을 바라보는 고양이)")

    col_ig1, col_ig2 = st.columns(2)
    with col_ig1: img_pop_choice = st.selectbox("🎧 대중음악 느낌 이미지", list(img_pop_genres.keys()))
    with col_ig2: img_ccm_choice = st.selectbox("⛪ CCM/홀리한 느낌 이미지", list(img_ccm_genres.keys()))

    col_is1, col_is2 = st.columns(2)
    with col_is1:
        img_mood_choice = st.selectbox("✨ 그림 분위기", list(img_moods.keys()))
        img_style_choice = st.selectbox("🖌️ 그림 스타일", list(img_styles.keys()))
    with col_is2:
        img_light_choice = st.selectbox("💡 조명 느낌", list(img_lightings.keys()))
        img_color_choice = st.selectbox("🌈 색감", list(img_colors.keys()))

    with st.expander("🎬 카메라/날씨/시대 디테일 설정"):
        col_is3, col_is4 = st.columns(2)
        with col_is3:
            img_camera_choice = st.selectbox("🎥 카메라 앵글", list(img_cameras.keys()))
            img_time_choice = st.selectbox("⏰ 시간대", list(img_times.keys()))
            img_weather_choice = st.selectbox("☁️ 날씨", list(img_weathers.keys()))
        with col_is4:
            img_era_choice = st.selectbox("🏰 시대/배경", list(img_eras.keys()))
            img_effect_choice = st.selectbox("✨ 특수효과", list(img_effects.keys()))

    st.divider()
    st.subheader("🖼️ 2-3. 생성할 이미지 수량 및 직접 업로드")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        gen_main = st.checkbox("📺 메인 (가로 16:9)", value=True)
        img_up_main = st.file_uploader("직접 배경 올리기 (가로)", type=['jpg','png'])
    with col_i2:
        gen_tiktok = st.checkbox("📱 틱톡 풀영상 (세로 9:16)", value=False)
        img_up_tiktok = st.file_uploader("직접 배경 올리기 (세로)", type=['jpg','png'])
    with col_i3:
        num_s_img = st.slider("✂️ 쇼츠 이미지 (세로) 개수", 0, 6, 0)
        img_up_shorts = []
        for i in range(num_s_img):
            img_up_shorts.append(st.file_uploader(f"쇼츠 {i+1} 직접 올리기", type=['jpg','png'], key=f"s_img_{i}"))

    if st.button("✨ 선택한 이미지 모두 렌더링", type="primary", use_container_width=True):
        if not audio_for_parsing and not t_kr: st.error("제목이 비어있습니다. 음원을 올리거나 제목을 직접 적어주세요!")
        else:
            with st.spinner("이미지를 생성하고 텍스트를 정밀하게 입히고 있습니다..."):
                st.session_state.img_res_main = None
                st.session_state.img_res_tiktok = None
                st.session_state.img_res_shorts = []
                
                img_sel_genre = img_ccm_genres[img_ccm_choice] if img_ccm_choice != "선택안함" else img_pop_genres[img_pop_choice]
                prompt_parts = [
                    img_subject, img_sel_genre, img_moods[img_mood_choice], img_styles[img_style_choice], 
                    img_lightings[img_light_choice], img_colors[img_color_choice], img_cameras[img_camera_choice],
                    img_times[img_time_choice], img_weathers[img_weather_choice], img_eras[img_era_choice], img_effects[img_effect_choice],
                    "masterpiece", "best quality", "4k resolution"
                ]
                final_img_prompt = ", ".join([p for p in prompt_parts if p])
                
                if gen_main:
                    st.session_state.img_res_main = design_and_save_image(1280, 720, final_img_prompt, 111, t_kr, t_en, font_choice, title_size, y_pos_percent, line_spacing, "designed_main.png", img_up_main)
                if gen_tiktok:
                    st.session_state.img_res_tiktok = design_and_save_image(720, 1280, final_img_prompt, 222, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, "designed_tiktok.png", img_up_tiktok)
                for i in range(num_s_img):
                    path = design_and_save_image(720, 1280, final_img_prompt, 333+i, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, f"designed_short_{i+1}.png", img_up_shorts[i])
                    st.session_state.img_res_shorts.append(path)
                    
            st.success("🎉 디자인 완료! 아래에서 이미지를 미리보고 다운로드하세요.")
            
    if st.session_state.get('img_res_main') or st.session_state.get('img_res_tiktok') or st.session_state.get('img_res_shorts'):
        st.subheader("📥 완성된 이미지 미리보기 및 다운로드")
        res_cols = st.columns(3)
        col_idx = 0
        
        if st.session_state.get('img_res_main'):
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_res_main, caption="메인 (16:9)")
                with open(st.session_state.img_res_main, "rb") as f: st.download_button("⬇️ 가로 이미지 다운로드", f, "Main_Cover.png", "image/png", use_container_width=True)
            col_idx += 1
            
        if st.session_state.get('img_res_tiktok'):
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_res_tiktok, caption="틱톡 (9:16)")
                with open(st.session_state.img_res_tiktok, "rb") as f: st.download_button("⬇️ 세로 이미지 다운로드", f, "TikTok_Cover.png", "image/png", use_container_width=True)
            col_idx += 1
            
        if st.session_state.get('img_res_shorts'):
            for i, p in enumerate(st.session_state.img_res_shorts):
                with res_cols[col_idx % 3]:
                    st.image(p, caption=f"쇼츠 {i+1} (9:16)")
                    with open(p, "rb") as f: st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드", f, f"Shorts_{i+1}_Cover.png", "image/png", use_container_width=True, key=f"btn_s_{i}")
                col_idx += 1

# ------------------------------------------
# [탭 3] 비디오 팩토리 (기존 무적 렌더링 유지)
# ------------------------------------------
with tab3:
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
                    step_title.markdown("#### ✨ 모든 렌더링 완료! 아래에서 결과물을 다운로드하세요.")

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

        # ==========================================
        # 🎉 렌더링 완료 영상 미리보기 및 유튜브 업로드
        # ==========================================
        if st.session_state.is_completed:
            st.success("🎉 비디오 렌더링이 성공적으로 완료되었습니다!")
            
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
                if st.session_state.tiktok_video_path: up_opts["📱 틱톡 영상"] = st.session_state.tiktok_video_path
                for i, p in enumerate(st.session_state.shorts_paths): up_opts[f"✂️ 쇼츠 {i+1}"] = p
                    
                if up_opts:
                    s_vid_key = st.selectbox("📌 업로드할 영상 선택", list(up_opts.keys()))
                    s_vid_path = up_opts[s_vid_key]
                    
                    yt_title = st.text_input("📝 영상 제목", value=f"[{st.session_state.base_name}] 은혜로운 찬양")
                    yt_desc = st.text_area("📜 영상 설명", value=f"할렐루야! 은혜로운 찬양입니다.\n\n#CCM #찬양", height=150)
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