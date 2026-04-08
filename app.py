import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Studio", layout="wide")

# [핵심] 왼쪽에 메뉴 만들기
with st.sidebar:
    st.title("🎨 작업 단계")
    choice = st.radio(
        "이동할 단계를 선택하세요",
        ["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"],
        key="main_nav"
    )
    st.divider()

# 선택한 메뉴에 따라 화면 표시
if choice == "📝 1. 가사 생성":
    ui_lyrics.render_tab1()
elif choice == "🎨 2. 이미지 생성":
    ui_image.render_tab2()
elif choice == "🎬 3. 영상 렌더링":
    ui_video.render_tab3()
