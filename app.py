import streamlit as st
import requests
import os
import urllib.parse
import re
import random
import gc
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, VideoClip
import moviepy.audio.fx.all as afx
from PIL import Image, ImageDraw, ImageFont
from proglog import ProgressBarLogger

st.set_page_config(page_title="AI 뮤직비디오 자동화 팩토리", page_icon="🎵", layout="wide")

# --- 💾 메모리 유지 ---
if 'is_completed' not in st.session_state: st.session_state.is_completed = False
if 'main_video_path' not in st.session_state: st.session_state.main_video_path = ""
if 'shorts_paths' not in st.session_state: st.session_state.shorts_paths = []
if 'clean_lyrics' not in st.session_state: st.session_state.clean_lyrics = ""
if 'base_name' not in st.session_state: st.session_state.base_name = ""
if 'yt_title' not in st.session_state: st.session_state.yt_title = ""
if 'yt_desc' not in st.session_state: st.session_state.yt_desc = ""
if 'yt_tags' not in st.session_state: st.session_state.yt_tags = ""

# --- 🔠 폰트 다운로드 ---
font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
font_path = "NanumGothicBold.ttf"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f: f.write(requests.get(font_url).content)

st.title("🎵 AI 뮤직비디오 팩토리 (가사 마스킹 & 쇼츠 최적화)")
st.write("가사가 지정된 영역에서만 스크롤되며, 쇼츠 생성 에러가 완벽히 수정되었습니다.")

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
# 🎯 프롬프트 사전 (생략 방지)
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

def create_cover_image(prompt, width, height, title_text, output_path, seed):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
    img_data = requests.get(url, timeout=30).content
    with open(output_path, "wb") as f: f.write(img_data)
    
    img = Image.open(output_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # 🔥 제목 크기 축소 (1280일 땐 40, 720일 땐 32)
    title_font = ImageFont.truetype(font_path, 40 if width == 1280 else 32)
    
    # 화면 정중앙 (anchor="ma" 적용)
    x = width / 2
    y = height * 0.12 # 위에서 12% 위치
    
    draw.multiline_text((x, y), title_text, font=title_font, fill="white", stroke_width=3, stroke_fill="black", align="center", anchor="ma")
    img.convert("RGB").save(output_path)
    img.close()

# 🎬 🔥 개선된 스크롤 함수 (마스크 기법 및 메모리 정리 적용)
def generate_video_with_lyrics(image_path, audio_clip, lyrics_text, output_path, logger, width, height):
    base_img = Image.open(image_path).convert("RGBA")
    duration = audio_clip.duration
    lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
    
    if not lines:
        clip = ImageClip(np.array(base_img.convert("RGB"))).set_duration(duration).set_audio(audio_clip)
        clip.write_videofile(output_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1, logger=logger)
        clip.close()
        base_img.close()
        return

    # 🔥 가사 폰트 크기 대폭 축소 (Main 22, Shorts 20)
    lyric_font_size = 22 if width == 1280 else 20
    lyric_font = ImageFont.truetype(font_path, lyric_font_size)
    line_spacing = 2.0
    
    try:
        dummy_bbox = ImageDraw.Draw(base_img).textbbox((0,0), "A", font=lyric_font)
        line_height = dummy_bbox[3] - dummy_bbox[1]
    except:
        line_height = lyric_font_size
        
    step_y = line_height * line_spacing
    total_text_height = len(lines) * step_y
    
    # 🔥 마스킹 윈도우(창문) 좌표 설정
    window_top = int(height * 0.25)   # 상단 25% (제목 아래에서 사라짐)
    window_bottom = int(height * 0.95) # 하단 95% (아래 5% 지점에서 나타남)
    window_height = window_bottom - window_top

    def make_frame(t):
        frame_img = base_img.copy()
        
        # 🔥 투명한 레이어(창문) 생성
        overlay = Image.new("RGBA", (width, window_height), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        progress = t / duration
        # 창문 내부에서의 Y축 스크롤 계산
        current_y = window_height - (progress * (window_height + total_text_height))
        
        for i, line in enumerate(lines):
            lyric_y = current_y + (i * step_y)
            # 창문(overlay) 범위를 벗어난 글씨는 아예 그리지 않음 (메모리 및 속도 최적화)
            if -50 < lyric_y < window_height + 50:
                draw_overlay.text((width / 2, lyric_y), line, font=lyric_font, fill="white", stroke_width=2, stroke_fill="black", align="center", anchor="ma")
        
        # 🔥 완성된 창문을 베이스 이미지에 덮어쓰기 (클리핑 효과 완벽 구현)
        frame_img.paste(overlay, (0, window_top), overlay)
        
        result_array = np.array(frame_img.convert("RGB"))
        
        # 🔥 매 프레임마다 완벽한 메모리 해제 (무료서버 램 폭파 방지)
        overlay.close()
        frame_img.close()
        
        return result_array

    # 10 fps 적용 (메모리 절약과 부드러움의 타협점)
    video_clip = VideoClip(make_frame, duration=duration).set_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=10, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1, logger=logger)
    
    video_clip.close()
    base_img.close()

# ==========================================
# 🖥️ 사이드바 & 메인 UI 구성
# ==========================================
st.sidebar.header("1. 기본 설정")
uploaded_audio = st.sidebar.file_uploader("🎧 음원 파일 (WAV, MP3)", type=['wav', 'mp3'])
num_shorts = st.sidebar.slider("📱 생성할 쇼츠 개수", min_value=0, max_value=4, value=0)
lyrics = st.sidebar.text_area("📝 가사 입력 (비워두면 스크롤 없음)", height=200)

st.header("🎨 2. 앨범 커버 초정밀 연출")
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

with st.expander("🎬 3. 디테일 연출 설정 (선택사항)"):
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
if st.button("🚀 비디오 팩토리 가동하기", use_container_width=True):
    if uploaded_audio is not None:
        status_box = st.container()
        with status_box:
            st.markdown("### 📡 실시간 작업 모니터링")
            step_title = st.empty()
            progress_bar = st.progress(0)
            progress_text = st.empty()

        try:
            st.session_state.shorts_paths = []
            st.session_state.is_completed = False
            
            base_name = os.path.splitext(uploaded_audio.name)[0]
            display_title = f"{base_name.split('_')[0]}\n{base_name.split('_')[1]}" if '_' in base_name else base_name
            
            clean_lyrics_list = [line.strip() for line in re.sub(r'\[.*?\]', '', lyrics).split('\n') if line.strip()]
            final_clean_lyrics = '\n'.join(clean_lyrics_list)
            st.session_state.clean_lyrics = final_clean_lyrics 

            step_title.markdown("#### 🎵 음원 파일 로딩 중...")
            audio_path = "temp_audio.wav"
            with open(audio_path, "wb") as f: f.write(uploaded_audio.getbuffer())
            
            full_audio = AudioFileClip(audio_path)
            audio_duration = full_audio.duration
            
            selected_genre = ccm_genres[ccm_choice] if ccm_choice != "선택안함" else pop_genres[pop_choice]
            prompt_parts = [
                subject, selected_genre, moods[mood_choice], styles[style_choice], 
                lightings[light_choice], colors[color_choice], cameras[camera_choice],
                times[time_choice], weathers[weather_choice], eras[era_choice], effects[effect_choice],
                "masterpiece", "best quality", "4k resolution"
            ]
            final_prompt = ", ".join([p for p in prompt_parts if p])

            # [작업 1] 메인 영상 커버 생성
            step_title.markdown("#### 🖼️ [1단계] 메인 앨범 커버(16:9) 생성 중...")
            main_img_path = "temp_main_img.jpg"
            create_cover_image(final_prompt, 1280, 720, display_title, main_img_path, seed=123)
            
            # [작업 2] 메인 영상 렌더링
            step_title.markdown("#### 🎬 [2단계] 메인 영상(16:9) 렌더링 중... (가사 애니메이션 적용)")
            main_video_path = "output_main_video.mp4"
            main_logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
            
            generate_video_with_lyrics(main_img_path, full_audio, final_clean_lyrics, main_video_path, main_logger, 1280, 720)
            
            st.session_state.main_video_path = main_video_path 
            gc.collect() # 램 확보

            # [작업 3] 쇼츠 추출 및 렌더링
            if num_shorts > 0:
                progress_bar.progress(0)
                progress_text.empty()
                step_title.markdown("#### 🔍 [3단계] 쇼츠 추출 구간 계산 중...")
                highlight_times = find_highlights_lite(audio_duration, num_shorts)
                
                for i, start_time in enumerate(highlight_times):
                    progress_bar.progress(0)
                    step_title.markdown(f"#### 📱 [4단계] 쇼츠 {i+1}/{num_shorts} 제작 중... (구간: {int(start_time)}초 부터)")
                    
                    shorts_img_path = f"temp_shorts_img_{i}.jpg"
                    create_cover_image(final_prompt, 720, 1280, display_title, shorts_img_path, seed=random.randint(1000, 9999))
                    
                    short_dur = min(random.randint(35, 55), audio_duration - start_time)
                    if short_dur < 5: short_dur = 5 # 너무 짧은 오디오 잘림 방지
                    
                    shorts_audio = full_audio.subclip(start_time, start_time + short_dur)
                    
                    # 🔥 에러 방지: 오디오 길이에 맞춰 페이드아웃 길이 자동 조절
                    fade_dur = min(1.5, shorts_audio.duration / 3.0)
                    shorts_audio = shorts_audio.fx(afx.audio_fadein, fade_dur).fx(afx.audio_fadeout, fade_dur)
                    
                    shorts_video_path = f"output_shorts_{i+1}.mp4"
                    shorts_logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                    
                    generate_video_with_lyrics(shorts_img_path, shorts_audio, final_clean_lyrics, shorts_video_path, shorts_logger, 720, 1280)
                    
                    shorts_audio.close()
                    st.session_state.shorts_paths.append(shorts_video_path)
                    gc.collect() # 램 확보

            # 메타데이터 생성
            is_ccm_selected = ccm_choice != "선택안함"
            st.session_state.yt_title = f"{display_title.replace(chr(10), ' - ')} | {mood_choice} 감성 플레이리스트"
            yt_desc_base = f"오늘 나눌 찬양은 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 마음을 담아 준비했습니다.\n함께 들으시며 위로와 평안을 얻으시길 바랍니다. 🙏" if is_ccm_selected else f"오늘의 추천곡 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 감성으로 쉴 때 듣기 좋아요.\n오늘 하루도 이 음악과 기분 좋게 보내세요! 🎧"
            st.session_state.yt_desc = yt_desc_base + f"\n\n# {base_name.split('_')[0].replace(' ', '')} #{mood_choice.split(' ')[0]}"
            st.session_state.yt_tags = f"{base_name.replace('_', ', ')}, 음악추천, 플레이리스트, {mood_choice.split(' ')[0]}음악, 힐링"
            if is_ccm_selected: st.session_state.yt_tags += ", CCM, 찬양, 은혜, 예배"

            full_audio.close()
            st.session_state.is_completed = True
            st.session_state.base_name = base_name
            
            step_title.markdown("#### ✨ 모든 작업이 완료되었습니다! 아래로 스크롤하세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ 왼쪽 사이드바에서 음원 파일을 업로드해주세요.")

# ==========================================
# 🎉 결과 출력 화면
# ==========================================
if st.session_state.is_completed:
    st.divider()
    
    if not os.path.exists(st.session_state.main_video_path):
        st.error("🚨 서버 메모리 부족으로 파일이 유실되었습니다. 새로고침(F5) 후 쇼츠 개수를 줄여서 다시 시도해주세요.")
        st.session_state.is_completed = False
    else:
        st.success("🎉 모든 영상이 성공적으로 렌더링되었습니다! 아래에서 확인 및 다운로드하세요.")
        
        st.subheader("📺 메인 영상 (16:9)")
        st.video(st.session_state.main_video_path)
        with open(st.session_state.main_video_path, "rb") as file:
            st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")

        st.divider()
        
        if len(st.session_state.shorts_paths) > 0:
            st.subheader(f"📱 추출된 쇼츠 영상 ({len(st.session_state.shorts_paths)}개)")
            cols = st.columns(len(st.session_state.shorts_paths))
            for idx, (col, shorts_path) in enumerate(zip(cols, st.session_state.shorts_paths)):
                with col:
                    if os.path.exists(shorts_path):
                        st.video(shorts_path)
                        with open(shorts_path, "rb") as file:
                            st.download_button(f"⬇️ 쇼츠 {idx+1} 다운로드", data=file, file_name=f"{st.session_state.base_name}_Shorts_{idx+1}.mp4", mime="video/mp4", key=f"btn_shorts_{idx}")
                    else:
                        st.error(f"쇼츠 {idx+1} 파일 유실됨")
            st.divider()
        
        st.header("📋 유튜브 업로드용 정보 (복사해서 붙여넣기!)")
        if st.session_state.clean_lyrics:
            st.download_button("⬇️ 가사 텍스트 다운로드 (유튜브 자막용)", data=st.session_state.clean_lyrics, file_name=f"{st.session_state.base_name}_lyrics.txt", mime="text/plain")

        st.text_input("📌 영상 제목", value=st.session_state.yt_title)
        st.text_area("📝 영상 설명 (해시태그 포함)", value=st.session_state.yt_desc, height=150)
        st.text_input("🏷️ 태그 (쉼표로 구분)", value=st.session_state.yt_tags)