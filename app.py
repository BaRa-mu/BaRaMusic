import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Production", layout="wide")

# 상단 탭 구성
tabs = st.tabs(["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"])

with tabs[0]:
    ui_lyrics.render_tab1()

with tabs[1]:
    ui_image.render_tab2()

with tabs[2]:
    ui_video.render_tab3()
