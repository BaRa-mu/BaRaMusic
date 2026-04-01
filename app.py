import streamlit as st
import requests
import os
from moviepy.editor import AudioFileClip, ImageClip

# 웹사이트 기본 설정 (탭 제목, 레이아웃)
st.set_page_config(page_title="나만의 뮤직비디오 생성기", page_icon="🎵", layout="centered")

st.title("🎵 AI 뮤직비디오 & 가사 추출기")
st.write("음원과 가사를 넣으면 유튜브용 동영상(MP4)과 유튜브 자막용 가사 파일(TXT)을 만들어줍니다.")

# 1. 입력 섹션
st.header("1. 정보 입력")
uploaded_audio = st.file_uploader("🎧 음원 파일 업로드 (mp3, wav)", type=['mp3', 'wav'])
prompt = st.text_input("🎨 앨범 커버 프롬프트 (영어로 입력)", "A beautiful sunset over a synthwave futuristic city, 4k")
lyrics = st.text_area("📝 가사 입력 (선택 사항)", height=200, placeholder="여기에 가사를 복사해서 붙여넣으세요.\n이 가사는 유튜브에 올릴 때 '자동 동기화'용으로 사용됩니다.")

# 2. 생성 버튼
if st.button("🚀 비디오 및 가사 파일 생성하기", use_container_width=True):
    if uploaded_audio is not None and prompt:
        with st.spinner("작업을 진행 중입니다. (약 1~3분 소요)"):
            try:
                # 파일 임시 저장
                audio_path = "temp_audio.mp3"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                    
                # [이미지 생성] 무료 서버 메모리 보호를 위해 720p(1280x720) 해상도 사용
                st.info("1/3: AI가 음악에 어울리는 이미지를 그리고 있습니다...")
                image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1280&height=720&nologo=true"
                response = requests.get(image_url)
                
                image_path = "temp_image.jpg"
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                st.image(image_path, caption="생성된 배경 이미지 (720p)")

                # [동영상 렌더링] 메모리 폭발 방지 세팅 (fps=1, preset='ultrafast')
                st.info("2/3: 이미지와 오디오를 합쳐 동영상을 렌더링하고 있습니다...")
                video_path = "output_video.mp4"
                
                audio_clip = AudioFileClip(audio_path)
                image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
                video_clip = image_clip.set_audio(audio_clip)
                
                # 무료 서버 맞춤형 렌더링 설정
                video_clip.write_videofile(
                    video_path, 
                    fps=1, # 정지 이미지이므로 1초에 1프레임만 렌더링 (속도 상승, 메모리 절약)
                    codec="libx264", 
                    audio_codec="aac",
                    preset="ultrafast", # 렌더링 속도 최우선
                    threads=1 # 서버 과부하 방지
                )
                
                st.success("🎉 모든 작업이 완료되었습니다!")

                # 3. 다운로드 섹션
                st.header("2. 완성된 파일 다운로드")
                
                col1, col2 = st.columns(2)
                
                # 영상 다운로드 버튼
                with col1:
                    with open(video_path, "rb") as file:
                        st.download_button(
                            label="🎥 유튜브용 동영상 다운로드 (.mp4)",
                            data=file,
                            file_name="my_music_video.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                # 가사 다운로드 버튼
                with col2:
                    if lyrics: # 입력된 가사가 있을 때만 버튼 생성
                        st.download_button(
                            label="📝 유튜브 자막용 가사 다운로드 (.txt)",
                            data=lyrics,
                            file_name="lyrics.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    else:
                        st.write("입력된 가사가 없습니다.")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                
    else:
        st.warning("⚠️ 음원 파일을 업로드하고 이미지 프롬프트를 입력해주세요.")