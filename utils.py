import os
import re
import random
import urllib.parse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from moviepy.editor import ImageClip, VideoClip
from proglog import ProgressBarLogger
import requests

# ==========================================
# 🔠 폰트 및 공통 사전 데이터
# ==========================================
font_links = {
    "나눔고딕 (기본/깔끔)": ("NanumGothicBold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"),
    "검은고딕 (강조/임팩트)": ("BlackHanSans.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    "노토산스 (모던/세련)": ("NotoSansKR.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR-Bold.ttf")
}

suno_pop_list = ["선택안함", "K-pop (케이팝)", "팝 발라드 (Pop Ballad)", "어쿠스틱 포크 (Acoustic Folk)", "인디 팝 (Indie Pop)", "R&B / Soul (알앤비/소울)", "모던 락 (Modern Rock)", "로파이 힙합 (Lo-Fi Hip Hop)", "시티팝 (City Pop)", "신스팝 (Synthpop)", "재즈 (Jazz)", "보사노바 (Bossa Nova)", "블루스 (Blues)", "컨트리 (Country)", "트로트 (Trot)", "일렉트로닉 (EDM)", "펑크 (Funk)", "디스코 (Disco)", "드림팝 (Dream Pop)", "얼터너티브 락 (Alt Rock)", "앰비언트 (Ambient)", "클래식 크로스오버 (Classical Crossover)"]
suno_ccm_list = ["선택안함", "모던 워십 (Modern Worship)", "전통 찬송가 편곡 (Traditional Hymns)", "가스펠 콰이어 (Gospel Choir)", "CCM 발라드 (CCM Ballad)", "워십 락 (Christian Rock)", "어쿠스틱 찬양 (Acoustic Worship)", "로파이 워십 (Lofi Worship)", "피아노 묵상 (Piano Prayer)", "시네마틱 워십 (Cinematic Worship)", "어린이 찬양 (Children's Worship)", "흑인 영가 (Black Gospel)", "소울 CCM (Soul CCM)", "재즈 워십 (Jazz Worship)", "컨트리 가스펠 (Country Gospel)", "아카펠라 (A Cappella)", "켈틱 워십 (Celtic Worship)", "일렉트로닉 워십 (EDM Worship)", "레게 CCM (Reggae CCM)", "라틴 가스펠 (Latin Gospel)", "스포큰 워드 기도 (Spoken Word)"]
suno_moods_list = ["선택안함", "감성적인 (Emotional)", "경건하고 거룩한 (Holy, Reverent)", "기쁘고 희망찬 (Joyful, Uplifting)", "평화롭고 차분한 (Peaceful, Calm)", "에너지 넘치는 (Energetic)", "어둡고 무거운 (Dark, Heavy)", "몽환적인 (Dreamy, Ethereal)", "웅장한 (Epic, Majestic)", "쓸쓸하고 우울한 (Melancholic, Sad)", "따뜻하고 포근한 (Warm, Comforting)", "신비로운 (Mysterious)", "향수를 부르는 (Nostalgic)", "사랑스러운 (Romantic, Sweet)", "결연하고 비장한 (Determined)", "치유되는 (Healing, Soothing)", "흥겨운 (Groovy, Fun)"]
suno_tempo_list = ["선택안함", "매우 느린 (Very Slow)", "느린 (Slow tempo)", "중간 느린 (Moderately Slow)", "중간 (Medium tempo)", "조금 빠른 (Allegretto)", "빠른 (Fast tempo)", "매우 빠른 (Very Fast)", "경쾌한 업템포 (Up-tempo)", "점점 빠르게 (Accelerando)", "점점 느리게 (Ritardando)", "자유로운 템포 (Rubato)", "안정적인 8비트 (Steady 8-beat)", "그루비한 16비트 (Groovy 16-beat)", "다이나믹 박자 (Dynamic Tempo)", "바운스 템포 (Bounce Tempo)", "왈츠풍 3/4박자 (Waltz Time)"]
suno_inst_list = ["선택안함", "어쿠스틱 기타 (Acoustic Guitar)", "피아노 (Piano)", "신디사이저 (Synthesizer)", "일렉기타 (Electric Guitar)", "웅장한 오케스트라 (Orchestra)", "아름다운 현악기 (Strings)", "금관악기 (Brass)", "무거운 베이스 (Heavy Bass)", "어쿠스틱 밴드 (Acoustic Band)", "로파이 비트 (Lo-Fi Beats)", "808 드럼 (808 Drum Machine)", "파이프 오르간 (Pipe Organ)", "하프 (Harp)", "첼로 (Cello)"]
suno_vocals_list = ["선택안함", "--- [ 👨 남성 보컬 ] ---", "남성 솔로 (Male vocal)", "허스키한 남성 (Husky male vocal)", "맑고 청아한 남성 (Clear male vocal)", "깊고 중후한 저음 남성 (Deep bass male vocal)", "따뜻한 중저음 남성 (Warm baritone male vocal)", "파워풀한 고음 남성 (Powerful high-pitch male vocal)", "부드럽고 감미로운 남성 (Soft and sweet male vocal)", "소울풀한 흑인 남성 (Soulful black male vocal)", "속삭이는 듯한 남성 (Whispering male vocal)", "거칠고 락적인 남성 (Gritty rock male vocal)", "소년 보컬 (Boy vocal)", "--- [ 👩 여성 보컬 ] ---", "여성 솔로 (Female vocal)", "허스키한 여성 (Husky female vocal)", "맑고 청아한 여성 (Clear female vocal)", "깊고 풍부한 저음 여성 (Deep rich female vocal)", "따뜻한 중저음 여성 (Warm alto female vocal)", "파워풀한 고음 여성 (Powerful belting female vocal)", "부드럽고 감미로운 여성 (Soft and sweet female vocal)", "소울풀한 흑인 여성 (Soulful black female vocal)", "속삭이는 듯한 여성 (Whispering female vocal)", "몽환적인 에테리얼 여성 (Ethereal dreamy female vocal)", "소녀 보컬 (Girl vocal)", "--- [ 👩‍❤️‍👨 듀엣 보컬 ] ---", "남녀 듀엣 (Male and female duet)", "감미로운 남녀 듀엣 (Sweet male and female duet)", "파워풀한 남녀 듀엣 (Powerful male and female duet)", "애절한 남녀 듀엣 (Sorrowful male and female duet)", "속삭이는 남녀 듀엣 (Whispering male and female duet)", "웅장한 남녀 듀엣 (Epic male and female duet)", "어쿠스틱 남녀 듀엣 (Acoustic male and female duet)", "남남 듀엣 (Male to male duet)", "감미로운 남남 듀엣 (Sweet male to male duet)", "파워풀한 남남 듀엣 (Powerful male to male duet)", "화음 위주 남남 듀엣 (Harmonious male to male duet)", "여여 듀엣 (Female to female duet)", "맑은 여여 듀엣 (Clear female to female duet)", "파워풀한 여여 듀엣 (Powerful female to female duet)", "화음 위주 여여 듀엣 (Harmonious female to female duet)", "소년 소녀 듀엣 (Boy and girl duet)", "중저음 남녀 듀엣 (Low pitch male and female duet)", "허스키 보컬 듀엣 (Husky vocal duet)", "소울풀 듀엣 (Soulful vocal duet)", "R&B 스타일 듀엣 (R&B style duet)", "팝 스타일 듀엣 (Pop style duet)", "--- [ 🎼 합창 및 기타 ] ---", "대규모 가스펠 합창 (Massive gospel choir)", "어린이 합창단 (Children's choir)", "장엄한 클래식 합창 (Majestic classical choir)", "잔잔한 아카펠라 합창 (Calm a cappella choir)", "남성 합창단 (Male choir)", "여성 합창단 (Female choir)", "천상의 목소리 합창 (Angelic ethereal choir)", "아프리칸 소울 합창 (African soul choir)", "현대 워십 코러스 (Modern worship chorus)", "보컬 없음 / 연주곡 (Instrumental only)"]

img_pop_genres = {"선택안함": "", "팝 (Pop)": "pop music vibe", "감성 발라드": "emotional ballad vibe", "정통 발라드": "classic korean ballad", "어쿠스틱 발라드": "acoustic guitar ballad", "인디 팝": "indie pop aesthetic", "인디 포크": "indie folk", "인디 라틴": "indie latin", "모던 락": "modern rock band", "얼터너티브 락": "alternative rock", "드림팝": "dream pop", "신스팝": "synthpop", "시티팝": "retro city pop", "알앤비 / 소울": "smooth R&B soul", "네오 소울": "neo soul", "재즈": "classic jazz club", "보사노바": "bossa nova relaxing", "로파이": "lofi hip hop aesthetic", "시네마틱 / OST": "cinematic soundtrack", "EDM / 일렉트로닉": "EDM festival vibe", "레트로 펑크": "retro funk groove", "컨트리": "country music vibe", "블루스": "blues club vibe", "클래식 크로스오버": "classical crossover elegant", "레게": "reggae beach vibe"}
img_ccm_genres = {"선택안함": "", "전통 찬송가": "traditional hymns", "모던 워십": "modern christian worship", "라이브 워십": "live worship concert", "어쿠스틱 찬양": "acoustic worship", "가스펠 콰이어": "joyful gospel choir", "CCM 발라드": "emotional christian ballad", "워십 락": "christian rock", "로파이 워십": "lofi christian worship", "피아노 묵상곡": "peaceful piano worship", "시네마틱 오케스트라 찬양": "epic orchestral worship", "어린이 찬양": "joyful children sunday school", "흑인 영가": "black gospel soulful", "재즈 워십": "jazz worship elegant", "컨트리 가스펠": "country gospel peaceful", "아카펠라": "a cappella worship choir", "켈틱 워십": "celtic christian worship", "EDM 워십": "youth worship energetic", "라틴 워십": "latin worship joyful", "스포큰 워드 기도": "deep prayer spoken word"}
img_moods = {"선택안함": "", "경건하고 홀리한": "holy, reverent, divine presence", "은혜롭고 따뜻한": "graceful, warm, comforting", "몽환적이고 신비로운": "ethereal, dreamy, magical", "차분하고 서정적인": "lyrical, poetic, calm", "우울하고 쓸쓸한": "melancholic, somber, lonely", "밝고 희망찬": "joyful, uplifting, bright", "에너지 넘치는 (파워풀)": "energetic, dynamic", "웅장하고 에픽한": "epic, majestic, awe-inspiring", "아련한 (향수)": "nostalgic, longing, sentimental", "사랑스럽고 포근한": "romantic, sweet, cozy", "비장하고 결연한": "determined, resolute, cinematic", "위로가 되는 (힐링)": "healing, soothing, peaceful therapy", "신비롭고 어두운": "dark fantasy, mysterious, eerie", "생동감 넘치는": "lively, vibrant, animated", "고독한 (혼자인)": "solitary, isolated, quiet"}
img_styles = {"선택안함": "", "실사 사진 (초고화질)": "photorealistic, 8k resolution", "수채화 (감성적인)": "soft watercolor painting", "유화 (명화 느낌)": "classic oil painting", "지브리 애니메이션 풍": "studio ghibli style, anime art", "신카이 마코토 풍": "makoto shinkai style, breathtaking sky", "픽사/디즈니 3D 풍": "3D render, pixar style", "빈티지 일러스트": "vintage 1950s illustration", "스테인드글라스 아트": "beautiful stained glass art", "미니멀리즘 (깔끔한)": "minimalist, clean lines, flat design", "레트로 픽셀 아트": "16-bit retro pixel art", "연필 스케치 / 드로잉": "detailed pencil sketch", "동양화 / 수묵화": "traditional korean painting", "사이버펑크 네온 아트": "cyberpunk digital art", "팝아트 (강렬한)": "pop art style, bold colors", "페이퍼 크래프트": "paper craft, origami style 3d"}
img_lightings = {"선택안함": "", "성스러운 빛 (God Rays)": "god rays, volumetric lighting", "따스한 자연광 (오후)": "natural sunlight, bright afternoon", "눈부신 역광 (실루엣 강조)": "backlit, strong silhouette, lens flare", "부드러운 스튜디오 조명": "soft studio lighting, diffuse light", "어두운 밤 (달빛/별빛)": "nighttime, soft moonlight, starlight", "골든 아워 (노을빛)": "golden hour lighting, warm glow", "블루 아워 (새벽빛)": "blue hour lighting, cool dusk", "화려한 네온사인": "vibrant neon lighting, cyberpunk glow", "안개 낀 빛 (산란광)": "foggy, soft diffused light through mist", "영화 같은 극적 조명": "cinematic lighting, chiaroscuro", "촛불 조명 (따뜻한)": "candlelight, warm glowing illumination", "스테인드글라스 투과광": "colorful light filtered through stained glass", "스포트라이트 (집중조명)": "single dramatic spotlight in darkness", "햇살 비치는 창가": "sunlight streaming through a window", "오로라 빛": "aurora borealis lighting, magical glow"}
img_colors = {"선택안함": "", "황금빛 톤 (성스러운)": "golden color palette", "따뜻한 웜톤 (가을 느낌)": "warm color palette, autumn colors", "차가운 쿨톤 (새벽/겨울)": "cool color palette, winter blues", "흑백 / 모노톤": "black and white, monochrome", "부드러운 파스텔": "soft pastel colors", "빈티지 (빛바랜 느낌)": "vintage colors, sepia tone", "강렬하고 쨍한 색감": "vivid colors, high contrast, vibrant", "어둡고 칙칙한 무드": "muted colors, dark palette", "에메랄드/그린 톤": "emerald green tones, lush nature", "모노크로매틱 블루": "monochromatic blue, deep sea", "로즈 골드/핑크 톤": "rose gold palette, soft pinks", "네온/사이버펑크 색감": "neon pink, cyan, cyberpunk palette", "어스 톤 (자연의 색)": "earth tones, brown, green, beige", "레드/오렌지 (석양)": "fiery red and orange sunset palette", "홀로그래픽 (무지개빛)": "holographic, iridescent colors"}
img_cameras = {"선택안함": "", "클로즈업 (사물/표정)": "extreme close-up shot", "바스트 샷 (상반신)": "medium shot, bust shot", "전신 샷 (Full body)": "full body shot", "풍경 위주 (Wide shot)": "wide landscape shot", "로우 앵글 (아래에서 위로)": "low angle shot, looking up", "하이 앵글 (위에서 아래로)": "high angle shot, looking down", "드론 뷰 (하늘에서)": "bird's eye view, drone shot", "어안 렌즈 (왜곡된 뷰)": "fisheye lens effect", "실루엣 샷": "silhouette shot against light", "1인칭 시점 (POV)": "first person view, POV shot", "파노라마 (넓은 시야)": "panoramic shot, ultra wide angle", "매크로 (초접사)": "macro photography, extreme detail", "어깨 너머 샷": "over the shoulder shot", "대칭 구도 (Symmetrical)": "perfectly symmetrical composition", "더치 앵글 (기울어진)": "dutch angle, tilted horizon"}
img_times = {"선택안함": "", "이른 새벽 (동틀 무렵)": "early dawn, breaking light", "밝은 아침": "bright morning", "화창한 정오": "midday, clear bright sky", "늦은 오후 (나른한)": "late afternoon", "해질녘 (골든아워)": "sunset, beautiful evening sky", "푸른 저녁 (블루아워)": "blue hour, twilight", "별이 뜨는 초저녁": "early evening, first stars", "깊은 밤 (자정)": "midnight, dark night sky", "비현실적인 우주/은하수": "ethereal night, glowing galaxy sky", "시간 불상 (초현실)": "timeless, surreal dimension", "비 오는 밤": "rainy night, wet reflections", "눈 내리는 아침": "snowy morning, winter daylight", "태양이 작열하는 한낮": "scorching sun, heatwave noon", "보름달이 뜬 밤": "full moon night, bright lunar light", "일식/월식의 순간": "solar eclipse, rare celestial event"}
img_weathers = {"선택안함": "", "맑고 쾌청한": "clear weather, sunny", "구름이 예쁜 날": "fluffy white clouds", "비 내리는 (촉촉한)": "raining, wet streets", "폭우 / 천둥번개": "heavy rain, thunderstorm, lightning", "눈 내리는 (포근한)": "snowing, winter wonderland", "거친 눈보라": "blizzard, heavy snowstorm", "안개 낀 (몽환적인)": "thick fog, mysterious mist", "바람 부는 (흩날리는)": "windy, blowing hair and clothes", "흩날리는 벚꽃잎": "falling cherry blossom petals", "흩날리는 가을 낙엽": "falling autumn leaves", "무지개가 뜬 날": "beautiful rainbow after rain", "황사/모래폭풍": "sandstorm, dusty wind", "흐리고 우중충한": "overcast, cloudy gloomy sky", "반짝이는 햇살 조각": "sun glints, sparkling light", "우박/얼음비": "hailstorm, freezing rain"}
img_eras = {"선택안함": "", "현대 / 도심 (2020년대)": "modern day, contemporary", "근미래 / 사이버펑크": "futuristic, cyberpunk city", "90년대 / Y2K 레트로": "1990s retro aesthetic, y2k", "80년대 / 카세트 감성": "1980s aesthetic, vaporwave", "중세 판타지 (기사/마법)": "medieval fantasy world", "고대 / 성서 시대": "ancient times, biblical era, historical", "빅토리아 시대 (19세기)": "victorian era, 19th century", "일제강점기 / 개화기": "1920s to 1930s vintage korean aesthetic", "르네상스 시대": "renaissance era, classic", "포스트 아포칼립스 (폐허)": "post-apocalyptic, overgrown ruins", "선사시대 / 원시 자연": "prehistoric, untouched pristine nature", "스팀펑크 (기계/증기)": "steampunk aesthetic, gears and brass", "우주 시대 (우주선/행성)": "space age, sci-fi, distant planet", "서부 개척 시대 (카우보이)": "wild west era, western", "로코코/바로크 시대": "rococo era, extravagant luxury"}
img_effects = {"선택안함": "", "필름 노이즈 (거친 느낌)": "heavy film grain, 35mm film", "빛 번짐 (렌즈 플레어)": "lens flare, light leak", "아웃포커싱 (배경 흐림)": "shallow depth of field, bokeh", "글리치 (디지털 깨짐)": "digital glitch effect, distortion", "몽환적인 블러 (소프트포커스)": "soft focus, dreamlike blur", "비네팅 (가장자리 어두움)": "vignette, dark edges", "이중 노출 (오버랩)": "double exposure art", "세피아 필터 (옛날 사진)": "sepia filter, aged photo", "프리즘 / 무지개 반사": "prism light leak, rainbow reflections", "빛바랜 폴라로이드 느낌": "polaroid effect, instant camera", "스피드 블러 (움직임 강조)": "motion blur, high speed", "만화책 느낌 (하프톤)": "comic book halftone effect", "수채화 번짐 효과": "watercolor bleed effect", "네온 글로우 (발광)": "neon glowing effect", "컬러 스플래시 (특정색 강조)": "color splash effect, selective color"}

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
    except Exception as e: return f"생성 오류: {e}"

def extract_eng(text):
    if "(" in text and ")" in text: return text.split("(")[1].replace(")", "").strip()
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
    
    if title_kr: draw.text((width/2, start_y), title_kr, font=font_kr, fill="white", stroke_width=3, stroke_fill="black", anchor="ma")
    if title_en: draw.text((width/2, start_y + h_kr + line_spacing), title_en, font=font_en, fill="lightgray", stroke_width=2, stroke_fill="black", anchor="ma")
        
    img.convert("RGB").save(output_path)
    img.close()
    return output_path

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