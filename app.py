import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Studio", layout="wide")

# 가사코드 수정 없이 app.py에서 CSS로 사이드바 천장 여백 0으로 밀어버림
st.markdown("""
    <style>
    /* 사이드바 내부 전체 상단 여백 제거 */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    /* 라디오 버튼 위치 위로 강제 인상 */
    div.row-widget.stRadio {
        margin-top: -100px !important;
    }
    /* 메뉴 사이 간격 및 여백 제로화 */
    hr {
        margin-top: -10px !important;
        margin-bottom: 10px !important;
    }
    /* 라디오 버튼 항목 사이 간격 조정 */
    div.row-widget.stRadio > div {
        gap: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 최상단 한 줄 메뉴 (아이콘 제외)
choice = st.sidebar.radio(
    "단계",
    ["가사", "이미지", "영상"],
    key="main_nav",
    horizontal=True,
    label_visibility="collapsed"
)
st.sidebar.divider()

# 선택한 페이지 호출 (기존 가사/이미지/영상 코드 그대로 연결)
if choice == "가사":
    ui_lyrics.render_tab1()
elif choice == "이미지":
    ui_image.render_tab2()
elif choice == "영상":
    ui_video.render_tab3()
