import streamlit as st
import requests
import os
import urllib.parse
from moviepy.editor import AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="AI 뮤직비디오 메이커", page_icon="🎵", layout="centered")

# 한글 제목이 깨지지 않도록 무료 폰트(나눔고딕 볼드체) 자동 다운로드
font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
font_path = "NanumGothicBold.ttf"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f:
        f.write(requests.get(font_url).content)

st.title("🎵 AI 뮤직비디오 & 가사 추출기")
st.write("메뉴를 선택하면 AI가 영상을 만들고, 파일명(한글_영어)을 분석해 영상 상단에 제목을 새겨줍니다.")

# --- 11개의 딕셔너리 (이전과 동일) ---
pop_genres = {"선택안함": "", "팝 (Pop)": "pop music vibe", "발라드 (Ballad)": "emotional ballad vibe", "알앤비/소울 (R&B/Soul)": "smooth R&B soul vibe", "힙합/랩 (Hip-hop)": "hip-hop culture, urban vibe", "어쿠스틱/인디 (Acoustic/Indie)": "acoustic indie folk", "신스팝/시티팝 (City Pop)": "synthpop, retro city pop vibe", "EDM/일렉트로닉 (EDM)": "edm, electronic dance music", "로파이 (Lo-Fi)": "lofi hip hop, chillhop aesthetic", "모던 락 (Modern Rock)": "modern rock band", "펑크/디스코 (Funk/Disco)": "funky disco", "재즈/블루스 (Jazz/Blues)": "classic jazz club", "앰비언트/뉴에이지 (Ambient)": "ambient music", "헤비메탈 (Heavy Metal)": "heavy metal", "레게/라틴 (Reggae/Latin)": "reggae, tropical latin", "트로트/전통 (Traditional)": "traditional korean pop"}
ccm_genres = {"선택안함": "", "전통 찬송가 (Hymns)": "traditional hymns, classic church", "모던 워십 (Modern Worship)": "modern christian worship", "어쿠스틱 찬양 (Acoustic)": "acoustic worship, intimate prayer", "가스펠 콰이어 (Gospel Choir)": "joyful black gospel choir", "CCM 발라드 (Ballad)": "emotional christian ballad", "워십 락 (Worship Rock)": "christian rock", "크리스천 힙합 (Christian Hip-Hop)": "christian hip-hop", "R&B/소울 가스펠 (R&B Gospel)": "soulful christian R&B", "앰비언트/기도 음악 (Prayer)": "ambient worship, deep prayer meditation", "어린이/주일학교 (Children's)": "joyful children's sunday school", "컨트리 가스펠 (Country)": "country gospel", "신스팝 워십 (Synthpop)": "upbeat synthpop worship", "아카펠라 찬양 (A Cappella)": "a cappella worship", "피아노 묵상곡 (Piano Solo)": "peaceful piano worship", "오케스트라 찬양 (Orchestral)": "epic orchestral worship", "켈틱 워십 (Celtic)": "celtic christian worship"}
moods = {"선택안함": "", "경건하고 홀리한 (Holy)": "holy, reverent, divine presence", "은혜롭고 따뜻한 (Graceful)": "graceful, warm, comforting", "몽환적이고 신비로운 (Dreamy)": "ethereal, dreamy, magical", "차분하고 우울한 (Calm/Sad)": "melancholic, somber, calm", "밝고 희망찬 (Joyful)": "joyful, uplifting, bright", "어둡고 긴장감 있는 (Dark)": "dark, eerie, suspenseful", "웅장하고 에픽한 (Epic)": "epic, majestic, cinematic", "평화롭고 힐링되는 (Peaceful)": "peaceful, relaxing, tranquil"}
styles = {"선택안함": "", "실사 사진 (Photorealistic)": "photorealistic, 8k resolution", "스테인드글라스 (Stained Glass)": "beautiful stained glass art", "2D 애니메이션 (지브리 풍)": "studio ghibli style, anime art", "3D 애니메이션 (픽사 풍)": "3D render, pixar style", "수채화 (Watercolor)": "soft watercolor painting", "유화 (Oil Painting)": "classic oil painting", "미니멀리즘 (Minimalist)": "minimalist illustration", "레트로 픽셀 아트 (Pixel Art)": "16-bit pixel art"}
lightings = {"선택안함": "", "성스러운 빛 (God Rays)": "god rays, divine light", "따스한 자연광 (Sunlight)": "natural sunlight, golden hour", "어두운 밤 (달빛/별빛)": "nighttime, moonlight", "화려한 네온사인 (Neon)": "vibrant neon lighting", "안개 낀/흐린 날 (Soft Light)": "foggy, soft diffused light", "영화 같은 무드등 (Cinematic)": "cinematic lighting, chiaroscuro", "역광 (실루엣 강조)": "backlit, strong silhouette"}
colors = {"선택안함": "", "황금빛 톤 (Golden)": "golden color palette", "따뜻한 웜톤 (오렌지/브라운)": "warm color palette", "차가운 쿨톤 (블루/시안)": "cool color palette", "흑백/모노톤 (B&W)": "black and white, monochrome", "부드러운 파스텔 (Pastel)": "soft pastel colors", "빈티지 (빛바랜 느낌)": "vintage colors, sepia", "어둡고 칙칙한 (Dark)": "muted colors, desaturated"}
cameras = {"선택안함": "", "클로즈업 (얼굴/사물 강조)": "extreme close-up shot", "전신 샷 (Full Body)": "full body shot", "풍경 위주 (Wide Shot)": "wide landscape shot", "로우 앵글 (아래에서 위로)": "low angle shot", "하이 앵글 (위에서 아래로)": "high angle shot", "드론 뷰 (하늘에서 본 풍경)": "drone photography, bird's eye view"}
times = {"선택안함": "", "이른 새벽 (Dawn)": "early dawn, bluish morning light", "밝은 아침/정오 (Morning)": "bright morning", "해질녘/노을 (Sunset)": "sunset, beautiful evening sky", "푸른 저녁 (Blue Hour)": "blue hour, twilight", "깊은 밤 (Midnight)": "midnight, dark night sky"}
weathers = {"선택안함": "", "맑고 쾌청한 (Clear)": "clear weather", "비 내리는 (Rainy)": "raining, wet streets", "눈 내리는 (Snowy)": "snowing, winter wonderland", "안개/연기 (Foggy)": "thick fog, mysterious mist", "흩날리는 꽃잎 (Petals)": "falling cherry blossom petals", "별이 쏟아지는 (Starry)": "starry night sky"}
eras = {"선택안함": "", "현대/도심 (Modern)": "modern day, contemporary city", "근미래/SF (Cyberpunk)": "futuristic, cyberpunk city", "90년대 레트로 (90s Retro)": "1990s retro aesthetic", "중세 판타지 (Medieval)": "medieval fantasy world", "고대/신화 (Ancient)": "ancient times, mythological"}
effects = {"선택안함": "", "필름 노이즈 (Film Grain)": "heavy film grain, vintage effect", "빛 번짐 (Lens Flare)": "lens flare, optical glare", "아웃포커싱 (Bokeh)": "shallow depth of field, bokeh", "글리치 (Glitch)": "digital glitch effect", "몽환적인 블러 (Soft Focus)": "soft focus, dreamlike blur"}

# --- 화면 구성 ---
st.header("1. 음악 및 가사 업로드")
st.info("💡 꿀팁: 파일명을 '한글제목_영어제목' (예: 은혜_Grace.wav)으로 올리면 영상 상단에 제목이 새겨집니다!")
uploaded_audio = st.file_uploader("🎧 음원 파일 (WAV, MP3)", type=['wav', 'mp3'])
lyrics = st.text_area("📝 가사 입력 (유튜브 하단 자막용)", height=100)

st.header("2. 앨범 커버 100% 맞춤 설정")
subject = st.text_input("🎯 메인 주제/사물 (선택)", placeholder="예: 십자가를 바라보는 소녀 (영어로 쓰면 완벽합니다)")

st.subheader("🎸 1. 음악 장르 선택")
tab1, tab2 = st.tabs(["대중음악 장르", "CCM (기독교 음악) 장르"])
with tab1:
    pop_choice = st.selectbox("대중음악에서 선택", list(pop_genres.keys()))
with tab2:
    ccm_choice = st.selectbox("CCM에서 선택", list(ccm_genres.keys()))

st.subheader("🎨 2. 기본 비주얼 설정")
col1, col2 = st.columns(2)
with col1:
    mood_choice = st.selectbox("✨ 전체 분위기", list(moods.keys()))
    style_choice = st.selectbox("🖌️ 그림 스타일", list(styles.keys()))
with col2:
    light_choice = st.selectbox("💡 조명 느낌", list(lightings.keys()))
    color_choice = st.selectbox("🌈 색감 (팔레트)", list(colors.keys()))

with st.expander("🎬 3. 디테일 연출 설정 (클릭해서 펼치기)"):
    col3, col4 = st.columns(2)
    with col3:
        camera_choice = st.selectbox("🎥 카메라 앵글", list(cameras.keys()))
        time_choice = st.selectbox("⏰ 시간대", list(times.keys()))
        weather_choice = st.selectbox("☁️ 날씨/환경", list(weathers.keys()))
    with col4:
        era_choice = st.selectbox("🏰 시대적 배경", list(eras.keys()))
        effect_choice = st.selectbox("✨ 특수효과", list(effects.keys()))

# --- 렌더링 로직 ---
if st.button("🚀 비디오 및 가사 파일 생성하기", use_container_width=True):
    if uploaded_audio is not None:
        with st.spinner("작업을 진행 중입니다. (약 1~3분 소요)"):
            try:
                # 1) 파일명 파싱 (한글제목_영어제목 추출)
                original_filename = uploaded_audio.name
                base_name = os.path.splitext(original_filename)[0]
                
                # '_' 기준으로 제목 분리
                if '_' in base_name:
                    title_ko, title_en = base_name.split('_', 1)
                    display_title = f"{title_ko}\n{title_en}"
                else:
                    display_title = base_name # '_'가 없으면 그냥 원래 이름 사용

                # 음원 임시 저장
                audio_extension = original_filename.split('.')[-1]
                audio_path = f"temp_audio.{audio_extension}"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                    
                # 2) 프롬프트 조합 및 이미지 생성
                st.info("1/3: AI가 배경 이미지를 생성하고 있습니다...")
                selected_genre = ccm_genres[ccm_choice] if ccm_choice != "선택안함" else pop_genres[pop_choice]
                prompt_parts = [
                    subject, selected_genre, moods[mood_choice], styles[style_choice], 
                    lightings[light_choice], colors[color_choice], cameras[camera_choice],
                    times[time_choice], weathers[weather_choice], eras[era_choice], effects[effect_choice],
                    "masterpiece", "best quality", "4k resolution"
                ]
                final_prompt = ", ".join([p for p in prompt_parts if p])
                encoded_prompt = urllib.parse.quote(final_prompt)
                
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
                response = requests.get(image_url)
                
                raw_image_path = "temp_raw_image.jpg"
                with open(raw_image_path, "wb") as f:
                    f.write(response.content)

                # 3) 🌟 이미지 상단에 파싱된 제목 새기기 (Pillow 사용)
                st.info("2/3: 앨범 커버에 곡 제목을 새기고 있습니다...")
                img = Image.open(raw_image_path).convert("RGBA")
                draw = ImageDraw.Draw(img)
                title_font = ImageFont.truetype(font_path, 65) # 폰트 크기 65
                
                # 글씨 크기 계산 및 위치 잡기 (상단 중앙)
                try:
                    bbox = draw.textbbox((0, 0), display_title, font=title_font, align="center")
                    text_w = bbox[2] - bbox[0]
                except:
                    text_w = 400
                
                W, H = img.size
                x = (W - text_w) / 2
                y = 50 # 상단에서 50픽셀 떨어진 위치
                
                # 글씨 쓰기 (어떤 배경에서도 잘 보이게 검은색 두꺼운 테두리 + 흰 글씨)
                draw.multiline_text((x, y), display_title, font=title_font, fill="white", stroke_width=4, stroke_fill="black", align="center")
                
                final_image_path = "temp_final_image.jpg"
                img.convert("RGB").save(final_image_path)
                st.image(final_image_path, caption=f"제목이 새겨진 앨범 커버: {base_name}")

                # 4) 동영상 렌더링 (서버 보호 세팅)
                st.info("3/3: 음악과 이미지를 합쳐 영상을 렌더링하고 있습니다...")
                video_path = "output_video.mp4"
                
                audio_clip = AudioFileClip(audio_path)
                image_clip = ImageClip(final_image_path).set_duration(audio_clip.duration)
                video_clip = image_clip.set_audio(audio_clip)
                
                video_clip.write_videofile(
                    video_path, 
                    fps=1, 
                    codec="libx264", 
                    audio_codec="aac",
                    preset="ultrafast",
                    threads=1
                )
                
                st.success("🎉 모든 작업이 완료되었습니다!")

                # 5) 다운로드 섹션
                st.header("3. 완성된 파일 다운로드")
                dl_col1, dl_col2 = st.columns(2)
                
                with dl_col1:
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="🎥 유튜브용 동영상 다운로드 (.mp4)",
                            data=file,
                            file_name=f"{base_name}_MusicVideo.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                with dl_col2:
                    if lyrics: 
                        st.download_button(
                            label="📝 자막용 가사 다운로드 (.txt)",
                            data=lyrics,
                            file_name=f"{base_name}_lyrics.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    else:
                        st.write("입력된 가사가 없습니다.")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                
    else:
        st.warning("⚠️ 음원 파일(WAV 또는 MP3)을 업로드해주세요.")