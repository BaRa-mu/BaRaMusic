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

st.set_page_config(page_title="AI 뮤직비디오 자동화 팩토리", page_icon="🎵", layout="wide")

# --- 메모리 유지 (Session State) ---
if 'is_completed' not in st.session_state: st.session_state.is_completed = False
if 'main_video_path' not in st.session_state: st.session_state.main_video_path = ""
if 'shorts_paths' not in st.session_state: st.session_state.shorts_paths = [] # 쇼츠 리스트
if 'clean_lyrics' not in st.session_state: st.session_state.clean_lyrics = ""
if 'base_name' not in st.session_state: st.session_state.base_name = ""
if 'yt_title' not in st.session_state: st.session_state.yt_title = ""
if 'yt_desc' not in st.session_state: st.session_state.yt_desc = ""
if 'yt_tags' not in st.session_state: st.session_state.yt_tags = ""

# 폰트 다운로드
font_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
font_path = "NanumGothicBold.ttf"
if not os.path.exists(font_path):
    with open(font_path, "wb") as f: f.write(requests.get(font_url).content)

st.title("🎵 AI 뮤직비디오 공장 (하이라이트 자동추출)")
st.write("음원의 에너지를 분석해 클라이맥스를 찾고, 메인 영상과 최대 4개의 쇼츠를 한 번에 만듭니다.")

# --- 오디오 하이라이트(클라이맥스) 추출 알고리즘 ---
def find_highlights(audio_clip, num_highlights=1, window_sec=15, min_dist=25):
    """오디오의 파형을 분석해 에너지가 가장 높은(후렴구) 구간의 시작 시간들을 반환합니다."""
    try:
        # 연산 속도와 메모리를 위해 샘플레이트를 낮춰서 배열로 변환
        fps = 11025 
        snd_array = audio_clip.to_soundarray(fps=fps)
        if len(snd_array.shape) > 1:
            snd_array = snd_array.mean(axis=1) # 스테레오를 모노로 병합
            
        window_size = int(window_sec * fps)
        energies = []
        
        # 15초 단위로 쪼개어 RMS(소리 에너지/볼륨) 평균값 계산
        for i in range(0, len(snd_array) - window_size, int(fps * 5)): # 5초 간격으로 스캔
            chunk = snd_array[i:i+window_size]
            rms = np.sqrt(np.mean(chunk**2))
            energies.append((rms, i / fps))
            
        # 에너지가 높은 순으로 정렬
        energies.sort(key=lambda x: x[0], reverse=True)
        
        highlights = []
        for eng, t in energies:
            # 기존에 찾은 하이라이트 구간과 최소 간격(min_dist) 이상 떨어져 있는지 확인 (중복 방지)
            if all(abs(t - ht) > min_dist for ht in highlights):
                # 영상이 곡 길이를 초과하지 않도록 보정
                safe_t = min(t, max(0, audio_clip.duration - 60))
                highlights.append(safe_t)
            if len(highlights) >= num_highlights:
                break
                
        # 곡이 너무 짧아서 구간을 다 못 찾은 경우 랜덤으로 채움
        while len(highlights) < num_highlights:
            highlights.append(random.randint(0, int(max(0, audio_clip.duration - 60))))
            
        return sorted(highlights) # 시간순 정렬
    except Exception as e:
        # 에러 발생 시 안전하게 기존 랜덤 방식 사용
        return [random.randint(15, int(max(15, audio_clip.duration - 60))) for _ in range(num_highlights)]

# --- 이미지 생성 함수 ---
def create_cover_image(prompt, width, height, title_text, output_path, seed):
    encoded_prompt = urllib.parse.quote(prompt)
    # seed 값을 추가하여 쇼츠마다 미세하게 다른 배경 이미지가 나오도록 설정
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
    img_data = requests.get(url).content
    with open(output_path, "wb") as f: f.write(img_data)
    
    img = Image.open(output_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(font_path, 65 if width == 1280 else 55)
    try:
        bbox = draw.textbbox((0, 0), title_text, font=title_font, align="center")
        text_w = bbox[2] - bbox[0]
    except:
        text_w = 400
    
    x = (width - text_w) / 2
    y = height * 0.1 
    draw.multiline_text((x, y), title_text, font=title_font, fill="white", stroke_width=4, stroke_fill="black", align="center")
    img.convert("RGB").save(output_path)

# --- UI 및 메뉴 ---
pop_genres = {"팝 (Pop)": "pop music vibe", "발라드 (Ballad)": "emotional ballad vibe", "R&B/Soul": "smooth R&B soul", "힙합 (Hip-hop)": "urban hip-hop", "어쿠스틱 (Acoustic)": "acoustic indie", "EDM": "electronic dance music", "로파이 (Lo-Fi)": "lofi hip hop chill"}
ccm_genres = {"모던 워십": "modern christian worship", "전통 찬송가": "classic church hymns", "어쿠스틱 찬양": "acoustic worship", "CCM 발라드": "emotional christian ballad", "피아노 묵상": "peaceful piano worship prayer"}
moods = {"은혜롭고 따뜻한": "graceful warm", "경건하고 홀리한": "holy divine presence", "몽환적인": "ethereal dreamy", "차분한": "melancholic calm", "희망찬": "joyful bright"}
styles = {"실사 사진": "photorealistic 8k", "수채화 느낌": "soft watercolor", "지브리 애니풍": "studio ghibli anime art", "빛바랜 빈티지": "vintage cinematic"}

st.sidebar.header("1. 기본 설정")
uploaded_audio = st.sidebar.file_uploader("🎧 음원 업로드 (WAV, MP3)", type=['wav', 'mp3'])
num_shorts = st.sidebar.slider("📱 생성할 쇼츠 개수", min_value=1, max_value=4, value=2, help="음원의 에너지를 분석해 알아서 다른 구간으로 뽑아줍니다.")
lyrics = st.sidebar.text_area("📝 가사 복사 (대괄호 자동삭제)", height=150)

st.header("🎨 2. 앨범 커버 분위기 설정")
subject = st.text_input("🎯 메인 주제 (선택)", placeholder="예: 햇살이 비치는 교회 창문")

col1, col2, col3 = st.columns(3)
with col1:
    is_ccm = st.checkbox("⛪ CCM 곡인가요?", value=True)
    genre_choice = st.selectbox("장르", list(ccm_genres.keys()) if is_ccm else list(pop_genres.keys()))
    genre_prompt = ccm_genres[genre_choice] if is_ccm else pop_genres[genre_choice]
with col2:
    mood_choice = st.selectbox("✨ 분위기", list(moods.keys()))
with col3:
    style_choice = st.selectbox("🖌️ 스타일", list(styles.keys()))

# --- 렌더링 로직 ---
if st.button("🚀 비디오 팩토리 가동 (메인 + 쇼츠 생성)", use_container_width=True):
    if uploaded_audio is not None:
        # 영상이 최대 5개 만들어지므로 시간이 제법 소요됩니다.
        with st.spinner(f"음원을 분석하고 메인 영상과 {num_shorts}개의 쇼츠를 생성 중입니다. (약 3~7분 소요 ☕)"):
            try:
                # 초기화
                st.session_state.shorts_paths = []
                base_name = os.path.splitext(uploaded_audio.name)[0]
                display_title = f"{base_name.split('_')[0]}\n{base_name.split('_')[1]}" if '_' in base_name else base_name
                
                clean_lyrics_list = [line.strip() for line in re.sub(r'\[.*?\]', '', lyrics).split('\n') if line.strip()]
                final_clean_lyrics = '\n'.join(clean_lyrics_list)

                audio_path = "temp_audio.wav"
                with open(audio_path, "wb") as f: f.write(uploaded_audio.getbuffer())
                
                full_audio = AudioFileClip(audio_path)
                
                prompt_parts = [subject, genre_prompt, moods[mood_choice], styles[style_choice], "masterpiece", "best quality"]
                final_prompt = ", ".join([p for p in prompt_parts if p])

                # [1] 메인 영상 생성
                st.toast("🎬 1단계: 메인 영상 제작 중...")
                main_img_path = "temp_main_img.jpg"
                create_cover_image(final_prompt, 1280, 720, display_title, main_img_path, seed=123)
                main_video_path = "output_main_video.mp4"
                ImageClip(main_img_path).set_duration(full_audio.duration).set_audio(full_audio).write_videofile(main_video_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1)
                
                # [2] 하이라이트 분석
                st.toast("🔍 2단계: AI가 음원의 클라이맥스(하이라이트)를 분석 중입니다...")
                highlight_times = find_highlights(full_audio, num_shorts)
                
                # [3] 쇼츠 영상 연속 생성
                for i, start_time in enumerate(highlight_times):
                    st.toast(f"📱 3단계: 쇼츠 {i+1}/{num_shorts} 제작 중... (구간: {int(start_time)}초 부터)")
                    
                    shorts_img_path = f"temp_shorts_img_{i}.jpg"
                    # 쇼츠마다 그림이 조금씩 다르게 나오도록 난수(seed) 부여
                    create_cover_image(final_prompt, 720, 1280, display_title, shorts_img_path, seed=random.randint(1000, 9999))
                    
                    short_dur = random.randint(35, 55) # 35~55초 사이의 자연스러운 길이
                    shorts_audio = full_audio.subclip(start_time, min(start_time + short_dur, full_audio.duration))
                    # 오디오 페이드 인/아웃 부드럽게 적용
                    shorts_audio = shorts_audio.fx(afx.audio_fadein, 1.5).fx(afx.audio_fadeout, 3.0)
                    
                    shorts_video_path = f"output_shorts_{i+1}.mp4"
                    ImageClip(shorts_img_path).set_duration(shorts_audio.duration).set_audio(shorts_audio).write_videofile(shorts_video_path, fps=1, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1)
                    
                    st.session_state.shorts_paths.append(shorts_video_path)
                    
                    # 메모리 확보 (무료 서버 안 터지게 필수)
                    gc.collect()

                # 유튜브 메타데이터 생성
                st.session_state.yt_title = f"{display_title.replace(chr(10), ' - ')} | {mood_choice} 감성 플레이리스트"
                yt_desc_base = f"오늘 나눌 음악은 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 마음을 담아 준비했습니다.\n함께 들으시며 위로와 평안을 얻으시길 바랍니다. 🙏\n\n구독과 좋아요는 큰 힘이 됩니다!" if is_ccm else f"오늘의 추천곡 '{base_name.split('_')[0]}' 입니다.\n{mood_choice} 감성으로 작업하거나 쉴 때 듣기 좋아요.\n오늘 하루도 이 음악과 기분 좋게 보내세요! 🎧"
                st.session_state.yt_desc = yt_desc_base + f"\n\n# {base_name.split('_')[0].replace(' ', '')} #{mood_choice.split(' ')[0]}"
                st.session_state.yt_tags = f"{base_name.replace('_', ', ')}, 음악추천, 플레이리스트, {mood_choice.split(' ')[0]}음악, 힐링"

                full_audio.close()
                st.session_state.is_completed = True
                st.session_state.base_name = base_name

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("⚠️ 왼쪽 메뉴에서 음원 파일을 업로드해주세요.")

# ==========================================
# 🎉 완료 화면 (미리보기 및 다운로드)
# ==========================================
if st.session_state.is_completed:
    st.divider()
    st.success("🎉 모든 작업이 완벽하게 끝났습니다! 아래에서 확인하세요.")
    
    # 1. 메인 영상 영역
    st.subheader("📺 메인 영상 (16:9)")
    st.video(st.session_state.main_video_path)
    with open(st.session_state.main_video_path, "rb") as file:
        st.download_button("⬇️ 메인 영상 다운로드 (.mp4)", data=file, file_name=f"{st.session_state.base_name}_Main.mp4", mime="video/mp4")

    st.divider()
    
    # 2. 쇼츠 영상 영역 (그리드로 배치)
    st.subheader(f"📱 추출된 쇼츠 영상 ({len(st.session_state.shorts_paths)}개) - AI 하이라이트 분석 적용")
    
    # 쇼츠 개수에 맞춰 화면을 쪼개서 보여줌
    cols = st.columns(len(st.session_state.shorts_paths))
    for idx, (col, shorts_path) in enumerate(zip(cols, st.session_state.shorts_paths)):
        with col:
            st.video(shorts_path)
            with open(shorts_path, "rb") as file:
                st.download_button(f"⬇️ 쇼츠 {idx+1} 다운로드", data=file, file_name=f"{st.session_state.base_name}_Shorts_{idx+1}.mp4", mime="video/mp4", key=f"btn_shorts_{idx}")

    st.divider()
    
    # 3. 유튜브 업로드 정보
    st.header("📋 유튜브 업로드용 정보 (그대로 복사하세요!)")
    if st.session_state.clean_lyrics:
        st.download_button("⬇️ 가사 텍스트 파일 다운로드 (유튜브 자막용)", data=st.session_state.clean_lyrics, file_name=f"{st.session_state.base_name}_lyrics.txt", mime="text/plain")

    st.text_input("📌 영상 제목", value=st.session_state.yt_title)
    st.text_area("📝 영상 설명 (해시태그 포함)", value=st.session_state.yt_desc, height=150)
    st.text_input("🏷️ 태그 (쉼표로 구분)", value=st.session_state.yt_tags)