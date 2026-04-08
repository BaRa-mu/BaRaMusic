import os
import re
import random
import requests
import numpy as np
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, VideoClip

font_links = {
    "나눔고딕 (기본/깔끔)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강조/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (모던/세련)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

# [추가됨] 폰트 파일이 없으면 자동으로 다운로드하는 함수
def ensure_font_exists(font_name):
    file_name, url = font_links.get(font_name, ("NanumGothicBold.ttf", font_links["나눔고딕 (기본/깔끔)"][1]))
    if not os.path.exists(file_name) and url:
        try:
            res = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(res.content)
        except Exception as e:
            print(f"Font download failed: {e}")
    return file_name if os.path.exists(file_name) else None

from proglog import ProgressBarLogger
class StreamlitProgressLogger(ProgressBarLogger):
    def __init__(self, st_bar, st_text, prefix):
        super().__init__()
        self.st_bar = st_bar
        self.st_text = st_text
        self.prefix = prefix
        self.last_percent = 0.0

    def bars_callback(self, bar, attr, value, old_value=None):
        # [수정됨] 키 존재 여부 확인 로직 추가 (KeyError 방지)
        if bar in self.bars and 'total' in self.bars[bar]:
            total = self.bars[bar]['total']
            if total > 0:
                percent = value / total
                if percent - self.last_percent >= 0.01 or percent >= 1.0:
                    self.st_bar.progress(min(1.0, percent))
                    self.st_text.text(f"⏳ {self.prefix}: {int(percent * 100)}%")
                    self.last_percent = percent

def design_and_save_image(width, height, prompt, seed, title_kr, title_en, font_choice, title_size, y_pos_percent, line_spacing, output_path, custom_file=None):
    # (이미지 불러오기/크롭 로직은 동일)
    # ... 기존 코드 ...
    
    draw = ImageDraw.Draw(img)
    
    # [수정됨] 폰트 다운로드 보장 및 로드 로직
    font_file = ensure_font_exists(font_choice)
    try:
        f_kr = ImageFont.truetype(font_file, title_size) if font_file else ImageFont.load_default()
        f_en = ImageFont.truetype(font_file, int(title_size * 0.65)) if font_file else ImageFont.load_default()
    except OSError:
        f_kr = f_en = ImageFont.load_default()

    # ... 기존 코드 유지 ...

def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height, start_sec=0):
    # ... (기존 코드 유지) ...
    
    # [수정됨] 자막 폰트도 다운로드 보장
    l_font_file = ensure_font_exists("나눔고딕 (기본/깔끔)")
    try:
        l_font = ImageFont.truetype(l_font_file, l_size) if l_font_file else ImageFont.load_default()
    except OSError:
        l_font = ImageFont.load_default()
        
    # ... (기존 코드 유지) ...

    def make_frame(t):
        if t < start_sec: 
            progress = 0.0
            g_alpha = 0.0
        else:
            progress = min(1.0, (t-start_sec)/(duration-start_sec))
            g_alpha = min(1.0, (t-start_sec)/1.0)
            
        v_y = int(progress * (w_h + len(lines)*step_y))
        
        # [수정됨] 배열 슬라이싱 Index Out Of Bounds 에러 방지 (min/max 처리)
        v_y = min(v_y, long_h - w_h) 
        
        src = long_np[v_y : v_y + w_h, :, :]
        
        # [수정됨] Numpy 차원 및 shape 안전성 강화
        if src.shape[0] != fade_mask.shape[0]:
            src = np.resize(src, (fade_mask.shape[0], src.shape[1], src.shape[2]))
            
        alpha = (src[:,:,3].astype(np.float32)/255.0)[:,:,np.newaxis] * fade_mask * g_alpha
        blended = src[:,:,:3]*alpha + bg_slice*(1.0-alpha)
        
        out = base_np.copy()
        out[w_top:w_bottom, :, :] = blended.astype(np.uint8)
        return out

    # ... (기존 코드 유지) ...
