import streamlit as st
import ui_lyrics
import ui_image
import ui_video

# 페이지 기본 설정
st.set_page_config(page_title="CCM & 자장가 자동 생성기", layout="wide")

st.title("🎶 찬양 & 자장가 영상 자동 제작")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["1. 가사 및 프롬프트", "2. 배경 이미지", "3. 영상 제작"])

with tab1:
    ui_lyrics.render_tab1()

with tab2:
    try:
        ui_image.render_tab2()
    except Exception as e:
        st.error("이미지 생성 중 오류가 발생했습니다. 아래 영상 탭으로 넘어가서 작업을 계속하실 수 있습니다.")
        st.caption(f"에러 상세 내용: {e}")

with tab3:
    ui_video.render_tab3()