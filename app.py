import streamlit as st
import ui_image
import ui_video
# ui_lyrics.py 파일이 같은 폴더에 있어야 합니다.
try:

    import ui_lyrics
except ImportError:
    pass

st.set_page_config(page_title="AI Music Studio", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 내부 전체 상단 여백 제거 */
    [data-testid="stSidebarUserContent"] { padding-top: 0rem !important; }
    /* 라디오 버튼 위치 위로 강제 인상 */
    div.row-widget.stRadio { margin-top: -100px !important; }
    /* 메뉴 사이 간격 및 여백 제로화 */
    hr { margin-top: -10px !important; margin-bottom: 10px !important; }
    /* 라디오 버튼 항목 사이 간격 조정 */
    div.row-widget.stRadio > div { gap: 5px !important; }
    </style>
""", unsafe_allow_html=True)

choice = st.sidebar.radio("단계", ["가사", "이미지", "영상"], key="main_nav", horizontal=True, label_visibility="collapsed")
st.sidebar.divider()

if choice == "가사":
    if 'ui_lyrics' in locals():
        ui_lyrics.render_tab1()
    else:
        st.warning("ui_lyrics.py 파일이 없습니다.")
elif choice == "이미지":
    ui_image.render_tab2()
elif choice == "영상":
    ui_video.render_tab3()
