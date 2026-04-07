import os
import re
import random
import requests
import numpy as np
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageChops
from moviepy.editor import ImageClip, VideoClip, AudioFileClip
from proglog import ProgressBarLogger

# --- 공통 데이터 리스트 ---
font_links = {
    "나눔고딕 (기본/깔끔)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강조/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (모던/세련)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

suno_pop_list = ["선택안함", "K-pop", "팝 발라드", "어쿠스틱 포크", "인디 팝", "R&B / Soul", "모던 락", "로파이 힙합", "시티팝", "신스팝", "재즈", "보사노바", "블루스", "컨트리", "트로트", "EDM", "펑크", "디스코", "드림팝", "얼터너티브 락", "앰비언트", "클래식 크로스오버"]
suno_ccm_list = ["선택안함", "모던 워십", "전통 찬송가", "가스펠 콰이어", "CCM 발라드", "워십 락", "어쿠스틱 찬양", "로파이 워십", "피아노 묵상", "시네마틱 워십", "어린이 찬양", "흑인 영가", "소울 CCM", "재즈 워십", "컨트리 가스펠", "아카펠라", "켈틱 워십", "일렉트로닉 워십", "레게 CCM", "라틴 가스펠", "스포큰 워드 기도"]
suno_moods_list = ["선택안함", "감성적인", "경건하고 거룩한", "기쁘고 희망찬", "평화롭고 차분한", "에너지 넘치는", "어둡고 무거운", "몽환적인", "웅장한", "쓸쓸하고 우울한", "따뜻하고 포근한", "신비로운", "향수를 부르는", "사랑스러운", "결연하고 비장한", "치유되는", "흥겨운"]
suno_tempo_list = ["선택안함", "매우 느린", "느린", "중간 느린", "중간", "조금 빠른", "빠른", "매우 빠른", "경쾌한 업템포", "자유로운 템포", "안정적인 8비트", "그루비한 16비트"]
suno_inst_list = ["선택안함", "어쿠스틱 기타", "피아노", "신디사이저", "일렉기타", "웅장한 오케스트라", "아름다운 현악기", "금관악기", "무거운 베이스", "어쿠스틱 밴드", "로파이 비트", "808 드럼", "파이프 오르간", "하프", "첼로"]
suno_vocals_list = ["선택안함", "남성 솔로", "여성 솔로", "혼성 듀엣", "대규모 합창단", "어린이 합창단", "허스키한 남성", "청아한 여성", "소울풀한 보컬", "파워풀한 고음", "속삭이는 보컬", "중후한 바리톤", "보컬 없음/연주곡"]

# --- 유틸리티 함수 ---
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
                self.st_text.text(f"⏳ {self.prefix}: {int(percent * 100)}%")
                self.last_percent = percent

def parse_time_to_sec(time_str):
    try:
        if not time_str or ":" not in time_str: return 0.0
        m, s = time_str.split(":")
        return int(m) * 60 + float(s)
    except: 
        return 0.0

def extract_eng(text):
    if "(" in text and ")" in text: 
        return text.split("(")[1].replace(")", "").strip()
    return text.strip()

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
        encoded_prompt = urllib.parse.quote(re.sub(r'\s+', ' ', prompt).strip())
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            with open(output_path, "wb") as f: 
                f.write(resp.content)
            img = Image.open(output_path).convert("RGBA")
        except: 
            img = Image.new("RGBA", (width, height), (35, 35, 40, 255))
            
    draw = ImageDraw.Draw(img)
    
    # --- [수정된 부분: 시스템 내 폰트 부재 시 URL 다운로드 및 Default 폰트 폴백 적용] ---
    font_info = font_links.get(font_choice, ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"))
    font_file, font_url = font_info[0], font_info[1]
    
    if not os.path.exists(font_file) and font_url:
        try:
            r = requests.get(font_url, allow_redirects=True, timeout=10)
            with open(font_file, "wb") as f: f.write(r.content)
        except: pass
        
    try:
        f_kr = ImageFont.truetype(font_file, title_size)
        f_en = ImageFont.truetype(font_file, int(title_size * 0.65))
    except IOError:
        f_kr = ImageFont.load_default()
        f_en = ImageFont.load_default()
    # --------------------------------------------------------------------------------
    
    y_center = height * (y_pos_percent / 100.0)
    
    try:
        h_kr = draw.textbbox((0,0), title_kr if title_kr else "A", font=f_kr)[3]
        h_en = draw.textbbox((0,0), title_en if title_en else "A", font=f_en)[3]
    except: 
        h_kr = title_size
        h_en = int(title_size * 0.65)
        
    start_y = y_center - ((h_kr + line_spacing + h_en) / 2)
    
    if title_kr: 
        draw.text((width/2, start_y), title_kr, font=f_kr, fill="white", stroke_width=3, stroke_fill="black", anchor="ma")
    if title_en: 
        draw.text((width/2, start_y + h_kr + line_spacing), title_en, font=f_en, fill="lightgray", stroke_width=2, stroke_fill="black", anchor="ma")
        
    img.convert("RGB").save(output_path)
    img.close()
    return output_path

def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height, start_sec=0):
    base_img = Image.open(image_path).convert("RGB")
    base_np = np.array(base_img)
    base_img.close()
    duration = audio_clip.duration
    lines = lyrics_text.rstrip().split('\n')
    
    if not lyrics_text.strip():
        clip = ImageClip(base_np).set_duration(duration).set_audio(audio_clip)
        clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
        clip.close()
        return

    l_size = 24 if width == 720 else 22
    
    # --- [수정된 부분: 렌더링 폰트 호출 시 예외 처리 적용] ---
    try:
        l_font = ImageFont.truetype("NanumGothicBold.ttf", l_size)
    except IOError:
        l_font = ImageFont.load_default()
    # --------------------------------------------------------

    step_y = int(l_size * 2.0)
    w_top = int(height * 0.60) if width == 720 else int(height * 0.40)
    w_bottom = int(height * 0.95)
    w_h = w_bottom - w_top
    f_h = int(step_y * 1.5)
    long_h = w_h + (len(lines) * step_y) + w_h
    long_img = Image.new("RGBA", (width, long_h), (0,0,0,0))
    draw_l = ImageDraw.Draw(long_img)
    
    for i, line in enumerate(lines):
        draw_l.text((width/2, w_h + (i*step_y)), line, font=l_font, fill="white", stroke_width=2, stroke_fill="black", anchor="ma")
        
    long_np = np.array(long_img)
    long_img.close()
    
    fade_mask = np.ones((w_h, width, 1), dtype=np.float32)
    for y in range(f_h): 
        fade_mask[y,:,0] = y/f_h
    for y in range(w_h-f_h, w_h): 
        fade_mask[y,:,0] = (w_h-y)/f_h
        
    bg_slice = base_np[w_top:w_bottom, :, :].astype(np.float32)

    def make_frame(t):
        if t < start_sec: 
            progress = 0.0
            g_alpha = 0.0
        else:
            progress = min(1.0, (t-start_sec)/(duration-start_sec))
            g_alpha = min(1.0, (t-start_sec)/1.0)
            
        v_y = int(progress * (w_h + len(lines)*step_y))
        src = long_np[v_y : v_y + w_h, :, :]
        alpha = (src[:,:,3].astype(np.float32)/255.0)[:,:,np.newaxis] * fade_mask * g_alpha
        blended = src[:,:,:3]*alpha + bg_slice*(1.0-alpha)
        out = base_np.copy()
        out[w_top:w_bottom, :, :] = blended.astype(np.uint8)
        return out

    VideoClip(make_frame, duration=duration).set_audio(audio_clip).write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)

def find_highlights_lite(duration_sec, num_highlights=0): 
    if num_highlights <= 0: return []
    highlights = []
    step = (duration_sec - 30) / num_highlights
    for i in range(num_highlights): 
        highlights.append(int((i*step) + (step*random.uniform(0.5, 0.8))))
    return highlights

def analyze_audio_start(audio_clip):
    try:
        snd = audio_clip.to_soundarray(fps=2)
        if len(snd.shape) > 1: snd = snd.mean(axis=1)
        rms = np.abs(snd)
        idx = np.where(rms > np.max(rms)*0.15)[0]
        return max(0, (idx[0]/2.0)-2.0) if len(idx)>0 else 5.0
    except: 
        return 5.0

def upload_to_youtube(video_path, title, description, tags, privacy_status, publish_at=None):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
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
    request.execute()
    return True, "🎉 업로드 성공!"