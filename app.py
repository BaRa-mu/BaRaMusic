import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI 뮤직비디오 자동화 팩토리", page_icon="🎬", layout="wide")

# 세션 상태 초기화 (에러 방지용)
keys = ['is_completed', 'gen_title_kr', 'gen_title_en', 'gen_lyrics', 'gen_prompt', 'v_main', 'v_tiktok', 'v_shorts']
for k in keys:
    if k not in st.session_state: st.session_state[k] = "" if 'v_' not in k else None

tab1, tab2, tab3 = st.tabs(["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"])
with tab1: ui_lyrics.render_tab1()
with tab2: ui_image.render_tab2()
with tab3: ui_video.render_tab3()