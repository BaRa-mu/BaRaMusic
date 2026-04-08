import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Studio", layout="wide")

# [CSS] 작업 단계 메뉴 하단 여백 제거 및 한 줄 배치 스타일
st.markdown("""
    <style>
    /* 사이드바 최상단 여백 줄임 */
    [data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
    /* 라디오 버튼 하단 마진 제거 및 가로 배치 최적화 */
    div.row-widget.stRadio > div { margin-bottom: -15px !important; }
    hr { margin-top: 0px !important; margin-bottom: 15px !important; }
    </style>
""", unsafe_allow_html=True)

# [사이드바 최상단] 아이콘 없이 가로 한 줄 배치
choice = st.sidebar.radio(
    "단계",
    ["가사", "이미지", "영상"],
    key="main_nav",
    horizontal=True,
    label_visibility="collapsed"
)
st.sidebar.divider()

# 선택한 페이지 호출
if choice == "가사":
    ui_lyrics.render_tab1()
elif choice == "이미지":
    ui_image.render_tab2()
elif choice == "영상":
    ui_video.render_tab3()
