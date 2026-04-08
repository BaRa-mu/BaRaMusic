import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Video Studio", layout="wide")

# 탭 인덱스 제어를 위한 세션 스테이트
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# 상단 탭 정의
tabs = st.tabs(["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"])

# 세션 스테이트에 따라 활성 탭 유지
with tabs[0]:
    ui_lyrics.render_tab1()

with tabs[1]:
    ui_image.render_tab2()

with tabs[2]:
    ui_video.render_tab3()
