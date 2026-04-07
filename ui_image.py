import streamlit as st
import utils

def render_tab2():
    st.header("🖼️ 이미지 생성 상세 설정")
    
    with st.expander("이미지 생성 옵션 설정", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            ratio = st.selectbox("화면 비율", ["16:9 (유튜브)", "9:16 (쇼츠)", "1:1 (인스타그램)"])
            style = st.selectbox("화풍/스타일", ["실사", "애니메이션", "수채화", "유화", "3D 렌더링"])
        with col2:
            quality = st.selectbox("해상도/품질", ["Standard", "HD", "4K", "8K"])
            variation = st.number_input("생성 개수", 1, 4, 1)

    # 이전 탭에서 만든 프롬프트를 기본값으로 가져옴
    default_p = st.session_state.get("prompt", "")
    prompt = st.text_area("최종 프롬프트 (가사 탭의 결과가 자동 연동됩니다)", default_p)
    
    up_m = st.file_uploader("커스텀 배경 이미지 업로드", type=["png", "jpg", "jpeg"])
    
    if st.button("🎨 이미지 생성 및 준비", type="primary"):
        with st.spinner("배경 이미지를 준비하고 있습니다..."):
            # utils.prepare_background 함수가 반드시 존재해야 함
            st.session_state.bg_m = utils.prepare_background(1280, 720, prompt, variation, "bg_m.png", up_m)
            st.success("이미지가 성공적으로 준비되었습니다!")
            st.image(st.session_state.bg_m, use_container_width=True)