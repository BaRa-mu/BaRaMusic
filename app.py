import streamlit as st

# 페이지 기본 설정 (무조건 가장 먼저 호출해야 함)
st.set_page_config(page_title="AI 뮤직비디오 자동화 팩토리", page_icon="🎬", layout="wide")

# 세션 상태 초기화
if 'is_completed' not in st.session_state: st.session_state.is_completed = False
if 'main_video_path' not in st.session_state: st.session_state.main_video_path = ""
if 'tiktok_video_path' not in st.session_state: st.session_state.tiktok_video_path = ""
if 'shorts_paths' not in st.session_state: st.session_state.shorts_paths = []
if 'base_name' not in st.session_state: st.session_state.base_name = ""
if 'gen_title_kr' not in st.session_state: st.session_state.gen_title_kr = ""
if 'gen_title_en' not in st.session_state: st.session_state.gen_title_en = ""
if 'gen_lyrics' not in st.session_state: st.session_state.gen_lyrics = ""
if 'gen_prompt' not in st.session_state: st.session_state.gen_prompt = ""

# 분리된 UI 모듈 임포트
import ui_lyrics
import ui_image
import ui_video

# 3단계 탭 생성
tab1, tab2, tab3 = st.tabs(["📝 1. 수노(Suno) 가사/프롬프트 생성", "🎨 2. 이미지 팩토리 (디자인)", "🎬 3. 비디오 렌더링 & 업로드"])

# 각 탭에 UI 모듈 할당
with tab1:
    ui_lyrics.render_tab1()

with tab2:
    ui_image.render_tab2()

with tab3:
    ui_video.render_tab3()