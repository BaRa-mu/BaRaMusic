import os
import re
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from moviepy.editor import ImageClip, VideoClip, AudioFileClip
from proglog import ProgressBarLogger

# --- 폰트 및 데이터 ---
font_links = {
    "나눔고딕 (기본/깔끔)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강조/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (모던/세련)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

suno_pop_list = ["선택안함", "K-pop (케이팝)", "팝 발라드", "어쿠스틱 포크", "인디 팝", "R&B / Soul", "모던 락", "로파이 힙합", "시티팝", "신스팝", "재즈", "보사노바", "블루스", "컨트리", "트로트", "일렉트로닉", "펑크", "디스코", "드림팝", "얼터너티브 락", "앰비언트", "클래식 크로스오버"]
suno_ccm_list = ["선택안함", "모던 워십", "전통 찬송가", "가스펠 콰이어", "CCM 발라드", "워십 락", "어쿠스틱 찬양", "로파이 워십", "피아노 묵상", "시네마틱 워십", "어린이 찬양", "흑인 영가", "소울 CCM", "재즈 워십", "컨트리 가스펠", "아카펠라", "켈틱 워십", "일렉트로닉 워십", "레게 CCM", "라틴 가스펠", "스포큰 워드 기도"]
suno_moods_list = ["선택안함", "감성적인", "경건하고 거룩한", "기쁘고 희망찬", "평화롭고 차분한", "에너지 넘치는", "어둡고 무거운", "몽환적인", "웅장한", "쓸쓸하고 우울한", "따뜻하고 포근한", "신비로운", "향수를 부르는", "사랑스러운", "결연하고 비장한", "치유되는", "흥겨운"]
suno_tempo_list = ["선택안함", "매우 느린", "느린", "중간 느린", "중간", "조금 빠른", "빠른", "매우 빠른", "경쾌한 업템포", "점점 빠르게", "점점 느리게", "자유로운 템포", "안정적인 8비트", "그루비한 16비트", "다이나믹 박자", "바운스 템포", "왈츠풍 3/4박자"]
suno_inst_list = ["선택안함", "어쿠스틱 기타", "피아노", "신디사이저", "일렉기타", "웅장한 오케스트라", "아름다운 현악기", "금관악기", "무거운 베이스", "어쿠스틱 밴드", "로파이 비트", "808 드럼", "파이프 오르간", "하프", "첼로"]
suno_vocals_list = ["선택안함", "남성 솔로", "여성 솔로", "혼성 듀엣", "대규모 합창단", "어린이 합창단", "허스키한 남성", "청아한 여성", "소울풀한 흑인 보컬", "파워풀한 고음", "속삭이는 보컬", "중후한 바리톤", "소년/소녀 보컬", "다중 하모니", "보코더/오토튠", "잔잔한 내레이션", "보컬 없음/연주곡"]

# --- 공통 유틸 ---
class StreamlitProgressLogger(ProgressBarLogger):
    def __init__(self, st_bar, st_text, prefix):
        super().__init__(); self.st_bar = st_bar; self.st_text = st_text; self.prefix = prefix; self.last_percent = 0.0
    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percent = value / total
            if percent - self.last_percent >= 0.01 or percent >= 1.0:
                self.st_bar.progress(min(1.0, percent))
                self.st_text.text(f"⏳ {self.prefix}: {int(percent * 100)}%")
                self.last_percent = percent

def extract_eng(text):
    if "(" in text and ")" in text: return text.split("(")[1].replace(")", "").strip()
    return text.strip()

def process_user_image(uploaded_file, width, height, output_path):
    img = Image.open(uploaded_file).convert("RGB")
    target_ratio = width / height
    img_ratio = img.width / img.height
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio); left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio); top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    img = img.resize((width, height), Image.Resampling.LANCZOS).save(output_path)

def analyze_audio_start(audio_clip):
    try:
        snd = audio_clip.to_soundarray(fps=2)
        if len(snd.shape) > 1: snd = snd.mean(axis=1)
        rms = np.abs(snd)
        idx = np.where(rms > np.max(rms) * 0.15)[0]
        return max(0, (idx[0]/2.0) - 2.0) if len(idx) > 0 else 5.0
    except: return 5.0

# --- 🎬 [핵심] 비디오 렌더링 함수 (utils에 있어야 함) ---
def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height, start_sec=0):
    base_img = Image.open(image_path).convert("RGB")
    base_img_np = np.array(base_img); base_img.close()
    duration = audio_clip.duration
    lines = lyrics_text.rstrip().split('\n')
    
    if not lyrics_text.strip():
        clip = ImageClip(base_img_np).set_duration(duration).set_audio(audio_clip)
        clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)
        clip.close(); return

    font_file = "NanumGothicBold.ttf"
    l_size = 24 if width == 720 else 22
    l_font = ImageFont.truetype(font_file, l_size)
    step_y = int(l_size * 2.0)
    
    w_top = int(height * 0.60) if width == 720 else int(height * 0.40)
    w_bottom = int(height * 0.95); w_h = w_bottom - w_top
    
    long_h = w_h + (len(lines) * step_y) + w_h
    long_img = Image.new("RGBA", (width, long_h), (0,0,0,0))
    draw_l = ImageDraw.Draw(long_img)
    for i, line in enumerate(lines):
        draw_l.text((width/2, w_h + (i*step_y)), line, font=l_font, fill="white", stroke_width=2, stroke_fill="black", anchor="ma")
    long_np = np.array(long_img); long_img.close()

    fade_mask = np.ones((w_h, width, 1), dtype=np.float32)
    f_h = int(step_y * 1.5)
    for y in range(f_h): fade_mask[y,:,0] = y/f_h
    for y in range(w_h-f_h, w_h): fade_mask[y,:,0] = (w_h-y)/f_h
    bg_slice = base_img_np[w_top:w_bottom, :, :].astype(np.float32)

    def make_frame(t):
        progress = 0.0 if t < start_sec else min(1.0, (t-start_sec)/(duration-start_sec))
        g_alpha = 0.0 if t < start_sec else min(1.0, (t-start_sec)/1.0)
        v_y = int(progress * (w_h + len(lines)*step_y))
        src = long_np[v_y : v_y + w_h, :, :]
        alpha = (src[:,:,3].astype(np.float32)/255.0)[:,:,np.newaxis] * fade_mask * g_alpha
        blended = src[:,:,:3]*alpha + bg_slice*(1.0-alpha)
        out = base_img_np.copy(); out[w_top:w_bottom, :, :] = blended.astype(np.uint8)
        return out

    VideoClip(make_frame, duration=duration).set_audio(audio_clip).write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)

def generate_static_video(image_path, audio_clip, output_path, logger):
    ImageClip(image_path).set_duration(audio_clip.duration).set_audio(audio_clip).write_videofile(output_path, fps=2, codec="libx264", audio_codec="aac", audio_fps=44100, preset="ultrafast", threads=1, logger=logger)

def upload_to_youtube(video_path, title, description, tags, privacy_status, publish_at=None):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
    youtube = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": title, "description": description, "tags": [t.strip() for t in tags.split(",") if t.strip()], "categoryId": "10"}, "status": {"privacyStatus": privacy_status}}
    if publish_at: body["status"]["publishAt"] = publish_at
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    return True, "🎉 업로드 성공!"