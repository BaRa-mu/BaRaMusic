import streamlit as st
import requests
import os
import urllib.parse
import re
import random
import gc
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip
import moviepy.audio.fx.all as afx
from PIL import Image, ImageDraw, ImageFont
from proglog import ProgressBarLogger # 🌟 실시간 진행률 가로채기 모듈

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

st.title("🎵 AI 뮤직비디오 팩토리 (실시간 모니터링 탑재)")
st.write("진행 상황을 눈으로 확인하세요! 메인 영상과 최대 4개의 쇼츠를 한 번에 뽑아냅니다.")

# ==========================================
# 🌟 스트림릿 전용 실시간 진행률 로거 클래스
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
            # bar == 'chunk'는 오디오 렌더링, 't'는 비디오 렌더링을 의미합니다.
            task_type = "오디오 합성 중" if bar == 'chunk' else "비디오 렌더링 중"
            self.st_text.text(f"⏳ {self.prefix} - {task_type}: {int(percent * 100)}%")

# ==========================================
# 🎯 11개의 초정밀 프롬프트 사전 (이전과 동일하게 유지)
# ==========================================
pop_genres = {"선택안함": "", "팝 (Pop)": "pop music vibe", "감성 발라드 (Emotional Ballad)": "emotional ballad vibe", "정통 발라드 (Classic Ballad)": "classic korean ballad", "어쿠스틱 발라드 (Acoustic Ballad)": "acoustic guitar ballad", "인디 팝 (Indie Pop)": "indie pop aesthetic", "인디 포크 (Indie Folk)": "indie folk, acoustic guitar", "인디 라틴 (Indie Latin)": "indie latin, acoustic bossa nova", "모던 락 (Modern Rock)": "modern rock band", "얼터너티브 락 (Alt Rock)": "alternative rock vibe", "드림팝 / 슈게이징 (Dream Pop)": "dream pop, ethereal shoegaze", "신스팝 (Synthpop)": "synthpop, retro electronic", "시티팝 (City Pop)": "retro city pop vibe", "알앤비 / 소울 (R&B/Soul)": "smooth R&B soul vibe", "네오 소울 (Neo Soul)": "neo soul, groovy", "재즈 (Jazz)": "classic jazz club vibe", "보사노바 (Bossa Nova)": "bossa nova, relaxing", "라운지 음악 (Lounge)": "lounge music", "로파이 (Lo-Fi)": "lofi hip hop", "앰비언트 (Ambient)": "ambient music", "뉴에이지 (New Age)": "peaceful new age", "시네마틱 / OST (Cinematic)": "cinematic soundtrack", "켈틱 / 아이리쉬 (Celtic)": "celtic folk"}
ccm_genres = {"선택안함": "", "전통 찬송가 (Hymns)": "traditional hymns", "모던 워십 (Modern Worship)": "modern christian worship", "라이브 워십 콘서트": "live worship concert", "어쿠스틱 찬양 (Acoustic)": "acoustic worship", "가스펠 콰이어 (Choir)": "joyful black gospel choir", "CCM 발라드 (Ballad)": "emotional christian ballad", "워십 락 (Worship Rock)": "christian rock", "R&B/소울 가스펠": "soulful christian R&B", "로파이 워십 (Lo-Fi Worship)": "lofi christian worship", "앰비언트/기도 (Prayer)": "ambient worship, deep prayer", "주일학교 (Children's)": "joyful children's sunday school", "컨트리 가스펠 (Country)": "country gospel", "아카펠라 합창단 (A Cappella)": "a cappella worship choir", "피아노 묵상곡 (Piano)": "peaceful piano worship", "시네마틱 오케스트라 찬양": "epic orchestral worship", "켈틱 워십 (Celtic)": "celtic christian worship"}
moods = {"선택안함": "", "경건하고 홀리한": "holy, reverent, divine presence", "은혜롭고 따뜻한": "graceful, warm, comforting", "몽환적이고 신비로운": "ethereal, dreamy, magical", "차분하고 서정적인": "lyrical, poetic, calm", "우울하고 쓸쓸한": "melancholic, somber, lonely", "밝고 희망찬": "joyful, uplifting, bright", "어둡고 긴장감 있는": "dark, eerie, suspenseful", "웅장하고 에픽한": "epic, majestic, cinematic", "평화롭고 힐링되는": "peaceful, relaxing, tranquil", "향수를 부르는 (아련한)": "nostalgic, longing", "로맨틱하고 사랑스러운": "romantic, affectionate", "에너지 넘치는 (파워풀)": "energetic, dynamic"}
styles = {"선택안함": "", "실사 사진 (초고화질)": "photorealistic, 8k resolution", "수채화 (감성적인)": "soft watercolor painting", "유화 (명화 느낌)": "classic oil painting", "지브리 애니메이션 풍": "studio ghibli style, anime art", "신카이 마코토 풍 (빛의 마술)": "makoto shinkai style, breathtaking sky", "픽사/디즈니 3D 풍": "3D render, pixar style", "스테인드글라스 아트": "beautiful stained glass art", "빈티지 일러스트": "vintage illustration", "미니멀리즘 일러스트": "minimalist, clean lines", "레트로 픽셀 아트": "16-bit pixel art", "스케치 / 펜 드로잉": "pencil sketch", "동양화 / 수묵화": "traditional korean painting", "사이버펑크 디지털 아트": "cyberpunk digital art"}
lightings = {"선택안함": "", "성스러운 빛 (God Rays)": "god rays, volumetric lighting", "따스한 자연광 (오후)": "natural sunlight", "눈부신 역광 (실루엣 강조)": "backlit, strong silhouette, lens flare", "부드러운 스튜디오 조명": "soft studio lighting", "어두운 밤 (달빛/별빛)": "nighttime, soft moonlight", "화려한 네온사인": "vibrant neon lighting", "안개 낀 / 흐린 날의 빛": "foggy, soft diffused light", "영화 같은 무드등 (대비)": "cinematic lighting, chiaroscuro", "촛불 조명 (따뜻한)": "candlelight, warm glowing", "스테인드글라스 투과광": "colorful light filtered through stained glass", "골든 아워 (노을빛)": "golden hour lighting", "블루 아워 (새벽빛)": "blue hour lighting"}
colors = {"선택안함": "", "황금빛 톤 (성스러운)": "golden color palette", "따뜻한 웜톤 (가을 느낌)": "warm color palette", "차가운 쿨톤 (새벽/겨울)": "cool color palette", "흑백 / 모노톤": "black and white, monochrome", "부드러운 파스텔": "soft pastel colors", "강렬하고 쨍한 색감": "vivid colors, high contrast", "빈티지 (빛바랜 느낌)": "vintage colors, sepia", "어둡고 칙칙한 (다크 무드)": "muted colors", "모노크로매틱 블루": "monochromatic blue", "로즈 골드 / 핑크빛": "rose gold palette", "에메랄드 / 그린 톤": "emerald green tones", "네온 사이버펑크 색감": "neon pink, cyan"}
cameras = {"선택안함": "", "클로즈업 (표정/사물 강조)": "extreme close-up shot", "바스트 샷 (상반신)": "medium shot, bust shot", "전신 샷 (Full Body)": "full body shot", "풍경 위주 (Wide Shot)": "wide landscape shot", "로우 앵글 (아래에서 위로)": "low angle shot", "하이 앵글 (위에서 아래로)": "high angle shot", "드론 뷰 (하늘에서 본 풍경)": "bird's eye view", "어안 렌즈 (왜곡된 뷰)": "fisheye lens effect", "실루엣 샷": "silhouette shot", "1인칭 시점 (POV)": "first person view", "파노라마 (넓은 가로)": "panoramic shot"}
times = {"선택안함": "", "이른 새벽 (동틀 무렵)": "early dawn, bluish morning light", "밝은 아침": "bright morning", "화창한 정오": "midday, clear bright sky", "늦은 오후 (나른한)": "late afternoon", "해질녘 (골든아워)": "sunset, beautiful evening sky", "푸른 저녁 (블루아워)": "blue hour, twilight", "별이 뜨는 초저녁": "early evening", "깊은 밤 (자정)": "midnight, dark night sky", "비현실적인 우주/은하수": "ethereal night, glowing galaxy sky", "시간 불상 (초현실)": "timeless, surreal dimension"}
weathers = {"선택안함": "", "맑고 쾌청한": "clear weather", "구름이 예쁜 날": "fluffy white clouds", "비 내리는 (촉촉한)": "raining, wet streets", "폭우 / 천둥번개": "heavy rain, thunderstorm", "눈 내리는 (포근한)": "snowing, winter wonderland", "눈보라 (거친)": "blizzard, heavy snowstorm", "안개 낀 (몽환적인)": "thick fog, mysterious mist", "바람 부는 (흩날리는)": "windy, blowing hair", "흩날리는 벚꽃잎": "falling cherry blossom petals", "흩날리는 가을 낙엽": "falling autumn leaves", "무지개가 뜬 날": "beautiful rainbow"}
eras = {"선택안함": "", "현대 / 도심 (2020년대)": "modern day", "근미래 / 사이버펑크": "futuristic, cyberpunk city", "90년대 / Y2K 레트로": "1990s retro aesthetic", "80년대 / 카세트 감성": "1980s aesthetic, vaporwave", "중세 판타지 (기사/마법)": "medieval fantasy world", "고대 / 성서 시대": "ancient times, biblical era", "빅토리아 시대 (19세기)": "victorian era", "일제강점기 / 개화기": "1920s to 1930s vintage korean aesthetic", "르네상스 시대": "renaissance era", "포스트 아포칼립스 (폐허)": "post-apocalyptic, overgrown ruins", "선사시대 / 원시 자연": "prehistoric, untouched pristine nature"}
effects = {"선택안함": "", "필름 노이즈 (거친 느낌)": "heavy film grain", "빛 번짐 (렌즈 플레어)": "lens flare", "아웃포커싱 (배경 흐림)": "shallow depth of field, bokeh", "글리치 (디지털 깨짐)": "digital glitch effect", "몽환적인 블러 (소프트포커스)": "soft focus, dreamlike blur", "비네팅 (가장자리 어두움)": "vignette, dark edges", "이중 노출 (오버랩)": "double exposure", "세피아 필터 (옛날 사진)": "sepia filter", "프리즘 / 무지개 반사": "prism light leak, rainbow reflections", "빛바랜 폴라로이드 느낌": "polaroid effect", "스피드 블러 (움직임 강조)": "motion blur"}

# ==========================================
# ⚙️ 핵심 알고리즘
# ==========================================
def find_highlights(audio_clip, num_highlights=1, window_sec=15, min_dist=25):
    try:
        fps = 11025 
        snd_array = audio_clip.to_soundarray(fps=fps)
        if len(snd_array.shape) > 1: snd_array = snd_array.mean(axis=1)
            
        window_size = int(window_sec * fps)
        energies = []
        for i in range(0, len(snd_array) - window_size, int(fps * 5)):
            chunk = snd_array[i:i+window_size]
            rms = np.sqrt(np.mean(chunk**2))
            energies.append((rms, i / fps))
            
        energies.sort(key=lambda x: x[0], reverse=True)
        
        highlights = []
        for eng, t in energies:
            if all(abs(t - ht) > min_dist for ht in highlights):
                safe_t = min(t, max(0, audio_clip.duration - 60))
                highlights.append(safe_t)
            if len(highlights) >= num_highlights: break
                
        while len(highlights) < num_highlights:
            highlights.append(random.randint(0, int(max(0, audio_clip.duration - 60))))
            
        return sorted(highlights)
    except Exception as e:
        return [random.randint(15, int(max(15, audio_clip.duration - 60))) for _ in range(num_highlights)]

def create_cover_image(prompt, width, height, title_text, output_path, seed):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
    img_data = requests.get(url).content
    with open(output_path, "wb") as f: f.write(img_data)
    
    img = Image.open(output_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(font_path, 65 if width == 1280 else 55)
    try:
        bbox = draw.textbbox((0, 0), title_text, font=title_font, align="center")
        text_w = bbox[2] - bbox[0]
    except: text_w = 400
    
    x = (width - text_w) / 2
    y = height * 0.1 
    draw.multiline_text((x, y), title_text, font=title_font, fill="white", stroke_width=4, stroke_fill="black", align="center")
    img.convert("RGB").save(output_path)

# ==========================================
# 🖥️ 사이드바 & 메인 UI 구성
# ==========================================
st.sidebar.header("1. 기본 설정")
uploaded_audio = st.sidebar.file_uploader("🎧 음원 파일 (WAV, MP3)", type=['wav', 'mp3'])
num_shorts = st.sidebar.slider("📱 생성할 쇼츠 개수", min_value=1, max_value=4, value=2)
lyrics = st.sidebar.text_area("📝 가사 입력 (대괄호 자동 삭제)", height=150)

st.header("🎨 2. 앨범 커버 초정밀 연출")
subject = st.text_input("🎯 메인 주제/사물 (선택)", placeholder="예: 창밖을 바라보는 고양이, 낡은 피아노 (영어로 쓰면 더 정확합니다)")

st.subheader("🎸 1. 음악 장르 선택")
tab1, tab2 = st.tabs(["🎧 대중음악 (인디/발라드 특화)", "⛪ CCM / 기독교 음악"])
with tab1: pop_choice = st.selectbox("대중음악", list(pop_genres.keys()))
with tab2: ccm_choice = st.selectbox("CCM", list(ccm_genres.keys()))

st.subheader("🎨 2. 기본 비주얼 설정")
col1, col2 = st.columns(2)
with col1:
    mood_choice = st.selectbox("✨ 분위기", list(moods.keys()))
    style_choice = st.selectbox("🖌️ 그림 스타일", list(styles.keys()))
with col2:
    light_choice = st.selectbox("💡 조명 느낌", list(lightings.keys()))
    color_choice = st.selectbox("🌈 색감 (팔레트)", list(colors.keys()))

with st.expander("🎬 3. 디테일 연출 설정 (카메라, 시간, 날씨, 시대, 효과)"):
    col3, col4 = st.columns(2)
    with col3:
        camera_choice = st.selectbox("🎥 카메라 앵글", list(cameras.keys()))
        time_choice = st.selectbox("⏰ 시간대", list(times.keys()))
        weather_choice = st.selectbox("☁️ 날씨/환경", list(weathers.keys()))
    with col4:
        era_choice = st.selectbox("🏰 시대적 배경", list(eras.keys()))
        effect_choice = st.selectbox("✨ 특수효과", list(effects.keys()))

# ==========================================
# 🚀 렌더링 시작 및 실시간 모니터링
# ==========================================
if st.button("🚀 비디오 팩토리 가동하기", use_container_width=True):
    if uploaded_audio is not None:
        
        # 🌟 진행률 모니터링 UI 컨테이너 생성
        status_box = st.container()
        with status_box:
            st.markdown("### 📡 실시간 작업 모니터링")
            step_title = st.empty() # 현재 어떤 작업중인지 큰 제목
            progress_bar = st.progress(0) # 게이지 바
            progress_text = st.empty() # % 텍스트

        try:
            st.session_state.shorts_paths = []
            base_name = os.path.splitext(uploaded_audio.name)[0]
            display_title = f"{base_name.split('_')[0]}\n{base_name.split('_')[1]}" if '_' in base_name else base_name
            
            clean_lyrics_list = [line.strip() for line in re.sub(r'\[.*?\]', '', lyrics).split('\n') if line.strip()]
            final_clean_lyrics = '\n'.join(clean_lyrics_list)

            step_title.markdown("#### 🎵 음원 파일 분석 중...")
            audio_path = "temp_audio.wav"
            with open(audio_path, "wb") as f: f.write(uploaded_audio.getbuffer())
            full_audio = AudioFileClip(audio_path)
            
            selected_genre = ccm_genres[ccm_choice] if ccm_choice != "선택안함" else pop_genres[pop_choice]
            prompt_parts = [
                subject, selected_genre, moods[mood_choice], styles[style_choice], 
                lightings[light_choice], colors[color_choice], cameras[camera_choice],
                times[time_choice], weathers[weather_choice], eras[era_choice], effects[effect_choice],
                "masterpiece", "best quality", "4k resolution"
            ]
            final_prompt = ", ".join([p for p in prompt_parts if p])

            # [작업 1] 메인 영상 생성
            step_title.markdown("#### 🖼️ [1단계] 메인 앨범 커버(16:9) 생성 중...")
            main_img_path = "temp_main_img.jpg"
            create_cover_image(final_prompt, 1280, 720, display_title, main_img_path, seed=123)
            
            step_title.markdown("#### 🎬 [2단계] 메인 영상(16:9) 렌더링 중...")
            main_video_path = "output_main_video.mp4"
            main_logger = StreamlitProgressLogger(progress_bar, progress_text, "메인 영상")
            ImageClip(main_img_path).set_duration(full_audio.duration).set_audio(full_audio).write_videofile(
                main_video_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1, logger=main_logger
            )
            
            # [작업 2] 오디오 하이라이트 지능형 추출
            progress_bar.progress(0)
            progress_text.empty()
            step_title.markdown("#### 🔍 [3단계] AI가 곡의 최고조(하이라이트) 구간을 찾는 중...")
            highlight_times = find_highlights(full_audio, num_shorts)
            
            # [작업 3] 쇼츠 생성
            for i, start_time in enumerate(highlight_times):
                progress_bar.progress(0) # 게이지 초기화
                step_title.markdown(f"#### 📱 [4단계] 쇼츠 {i+1}/{num_shorts} 제작 중... (구간: {int(start_time)}초 부터)")
                
                shorts_img_path = f"temp_shorts_img_{i}.jpg"
                create_cover_image(final_prompt, 720, 1280, display_title, shorts_img_path, seed=random.randint(1000, 9999))
                
                short_dur = random.randint(35, 55)
                shorts_audio = full_audio.subclip(start_time, min(start_time + short_dur, full_audio.duration))
                shorts_audio = shorts_audio.fx(afx.audio_fadein, 1.5).fx(afx.audio_fadeout, 3.0)
                
                shorts_video_path = f"output_shorts_{i+1}.mp4"
                shorts_logger = StreamlitProgressLogger(progress_bar, progress_text, f"쇼츠 {i+1}")
                ImageClip(shorts_img_path).set_duration(shorts_audio.duration).set_audio(shorts_audio).write_videofile(
                    shorts_video_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1, logger=shorts_logger
                )
                
                st.session_state.shorts_paths.append(shorts_video_path)
                gc.collect()

            # 완료 처리
            is_ccm_selected = ccm_choice != "선택안함"
            st.session_state.yt_title = f"{display_title.replace(chr(10), ' - ')} | {mood_choice} 감성 플레이리스트"
            yt_desc_base = f"오늘 나눌 찬양은 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 마음을 담아 준비했습니다.\n함께 들으시며 위로와 평안을 얻으시길 바랍니다. 🙏" if is_ccm_selected else f"오늘의 추천곡 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 감성으로 쉴 때 듣기 좋아요.\n오늘 하루도 이 음악과 기분 좋게 보내세요! 🎧"
            st.session_state.yt_desc = yt_desc_base + f"\n\n# {base_name.split('_')[0].replace(' ', '')} #{mood_choice.split(' ')[0]}"
            st.session_state.yt_tags = f"{base_name.replace('_', ', ')}, 음악추천, 플레이리스트, {mood_choice.split(' ')[0]}음악, 힐링"
            if is_ccm_selected: st.session_state.yt_tags += ", CCM, 찬양, 은혜, 예배"

            full_audio.close()
            st.session_state.is_completed = True
            st.session_state.base_name = base_name
            
            # 모니터링 창 초기화 및 완료 메시지
            step_title.markdown("#### ✨ 모든 작업이 완료되었습니다!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ 왼쪽 사이드바에서 음원 파일을 업로드해주세요.")

# ==========================================
# 🎉 완료 화면
# ==========================================
if st.session_state.is_completed:
    st.divider()
    st.success("🎉 모든 영상이 성공적으로 렌더링되었습니다! 아래에서 확인 및 다운로드하세요.")
    
    st.subheader("📺 메인 영상 (16:9)")
    st.video(st.session_state.main_video_path)
    with open(st.session_state.main_video_path, "rb") as file:
        st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")

    st.divider()
    
    st.subheader(f"📱 추출된 쇼츠 영상 ({len(st.session_state.shorts_paths)}개)")
    cols = st.columns(len(st.session_state.shorts_paths))
    for idx, (col, shorts_path) in enumerate(zip(cols, st.session_state.shorts_paths)):
        with col:
            st.video(shorts_path)
            with open(shorts_path, "rb") as file:
                st.download_button(f"⬇️ 쇼츠 {idx+1} 다운로드", data=file, file_name=f"{st.session_state.base_name}_Shorts_{idx+1}.mp4", mime="video/mp4", key=f"btn_shorts_{idx}")

    st.divider()
    
    st.header("📋 유튜브 업로드용 정보 (복사해서 붙여넣기!)")
    if st.session_state.clean_lyrics:
        st.download_button("⬇️ 가사 텍스트 파일 다운로드 (유튜브 하단 자막용)", data=st.session_state.clean_lyrics, file_name=f"{st.session_state.base_name}_lyrics.txt", mime="text/plain")

    st.text_input("📌 영상 제목", value=st.session_state.yt_title)
    st.text_area("📝 영상 설명 (해시태그 포함)", value=st.session_state.yt_desc, height=150)
    st.text_input("🏷️ 태그 (쉼표로 구분)", value=st.session_state.yt_tags)

# ==========================================
# 🎉 완료 화면 (파일 증발 에러 방지 안전장치 추가)
# ==========================================
if st.session_state.is_completed:
    st.divider()
    
    # 🌟 안전장치: 실제 서버에 파일이 살아있는지 검사합니다.
    if not os.path.exists(st.session_state.main_video_path):
        st.error("🚨 앗! 무료 서버의 메모리 부족으로 인해 만들어진 파일이 유실되었습니다. 새로고침(F5) 후 쇼츠 개수를 1~2개로 줄여서 다시 시도해주세요. 😭")
        st.session_state.is_completed = False
    else:
        st.success("🎉 모든 영상이 성공적으로 렌더링되었습니다! 아래에서 확인 및 다운로드하세요.")
        
        st.subheader("📺 메인 영상 (16:9)")
        st.video(st.session_state.main_video_path)
        with open(st.session_state.main_video_path, "rb") as file:
            st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")

        st.divider()
        
        st.subheader(f"📱 추출된 쇼츠 영상 ({len(st.session_state.shorts_paths)}개)")
        cols = st.columns(len(st.session_state.shorts_paths))
        for idx, (col, shorts_path) in enumerate(zip(cols, st.session_state.shorts_paths)):
            with col:
                # 쇼츠 파일도 살아있는지 개별 확인
                if os.path.exists(shorts_path):
                    st.video(shorts_path)
                    with open(shorts_path, "rb") as file:
                        st.download_button(f"⬇️ 쇼츠 {idx+1} 다운로드", data=file, file_name=f"{st.session_state.base_name}_Shorts_{idx+1}.mp4", mime="video/mp4", key=f"btn_shorts_{idx}")
                else:
                    st.error(f"쇼츠 {idx+1} 파일 유실됨")

        st.divider()
        
        st.header("📋 유튜브 업로드용 정보 (복사해서 붙여넣기!)")
        if st.session_state.clean_lyrics:
            st.download_button("⬇️ 가사 텍스트 파일 다운로드 (유튜브 하단 자막용)", data=st.session_state.clean_lyrics, file_name=f"{st.session_state.base_name}_lyrics.txt", mime="text/plain")

        st.text_input("📌 영상 제목", value=st.session_state.yt_title)
        st.text_area("📝 영상 설명 (해시태그 포함)", value=st.session_state.yt_desc, height=150)
        st.text_input("🏷️ 태그 (쉼표로 구분)", value=st.session_state.yt_tags)