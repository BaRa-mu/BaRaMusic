import streamlit as st
import ui_lyrics, ui_image, ui_video

st.set_page_config(page_title="AI Music Studio", layout="wide")

# 세션 스테이트 초기화 (탭 제어용)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# 상단 탭 구성
tabs = st.tabs(["📝 1. 가사 생성", "🎨 2. 이미지 생성", "🎬 3. 영상 렌더링"])

# 현재 활성화된 탭 렌더링
with tabs[0]:
    ui_lyrics.render_tab1()

with tabs[1]:
    ui_image.render_tab2()

with tabs[2]:
    ui_video.render_tab3()

# 외부에서 탭 강제 전환이 필요한 경우를 위한 로직
if st.session_state.active_tab != 0:
    js = f"""
    <script>
        var tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
        tabs[{st.session_state.active_tab}].click();
    </script>
    """
    st.components.v1.html(js, height=0)
    st.session_state.active_tab = 0 # 전환 후 리셋
