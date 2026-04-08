import streamlit as st
import ui_lyrics, ui_image, ui_video

# 페이지 설정
st.set_page_config(page_title="AI Music Studio", layout="wide")

# [핵심] 사이드바 천장 여백 0으로 만드는 CSS
st.markdown("""
    <style>
    /* 사이드바 내부 전체 상단 여백 제거 */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    /* 라디오 버튼 위쪽 여백 제거 */
    div.row-widget.stRadio {
        margin-top: -30px !important;
    }
    /* 메뉴 가로 배치 간격 조정 */
    div.row-widget.stRadio > div {
        gap: 10px !important;
    }
    /* 구분선 여백 제로 */
    hr {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# [사이드바 최상단] 한 줄 배치
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
