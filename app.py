import streamlit as st
import ui_lyrics, ui_image, ui_video

# 페이지 설정 (반드시 최상단)
st.set_page_config(page_title="AI Music Studio", layout="wide")

# [핵심] 탭 메뉴 생성 - 왼쪽 상단 배치
tabs = st.tabs(["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"])

with tabs[0]:
    ui_lyrics.render_tab1()

with tabs[1]:
    ui_image.render_tab2()

with tabs[2]:
    ui_video.render_tab3()
