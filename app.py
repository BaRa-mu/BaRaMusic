import streamlit as st
import ui_lyrics
import ui_image
import ui_video

st.set_page_config(page_title="CCM & 자장가 제작 시스템", layout="wide")
st.title("🎵 콘텐츠 자동화 제작 스튜디오")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 가사 및 기획", "🖼️ 배경 생성", "🎬 영상 제작"])

with tab1:
    try:
        ui_lyrics.render_tab1()
    except Exception as e:
        st.error(f"가사 탭 로딩 중 오류 발생: {e}")

with tab2:
    try:
        ui_image.render_tab2()
    except Exception as e:
        st.warning("이미지 생성 시스템에 오류가 있으나, 영상 제작은 가능합니다.")
        st.caption(f"상세 에러: {e}")

with tab3:
    try:
        ui_video.render_tab3()
    except Exception as e:
        st.error(f"영상 탭 로딩 중 오류 발생: {e}")