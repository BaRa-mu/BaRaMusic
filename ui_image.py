import streamlit as st
import utils

def render_tab2():
    st.header("🖼️ 배경 이미지 생성")
    
    # 탭 1에서 생성된 프롬프트를 자동으로 가져옴
    default_prompt = st.session_state.get("edit_prompt", "기본 배경 이미지 프롬프트")
    prompt = st.text_area("이미지 프롬프트 (가사 탭에서 자동 연동됨)", default_prompt)
    
    up_m = st.file_uploader("직접 배경 이미지 업로드 (선택사항)", type=["png", "jpg", "jpeg"])
    gen_m = st.button("🎨 이미지 생성 및 준비")
    
    if gen_m:
        with st.spinner("이미지를 준비하는 중입니다..."):
            # utils.py의 prepare_background 함수 호출 (에러 해결됨)
            st.session_state.bg_m = utils.prepare_background(1280, 720, prompt, 1, "bg_m.png", up_m)
            st.success("이미지가 성공적으로 준비되었습니다!")
            st.image(st.session_state.bg_m, use_container_width=True)