import streamlit as st

def render_tab2():
    # 설정 메뉴를 왼쪽 사이드바로 이동
    with st.sidebar:
        st.subheader("🎨 이미지 상세 설정")
        img_subject = st.text_input("💡 이미지 주제", key="i_subject")
        img_style = st.selectbox("🎭 화풍 선택", ["극사실주의", "디즈니 애니메이션", "유화", "수채화", "사이버펑크", "신비로운 판타지", "연필 스케치"], key="i_style")
        img_ratio = st.radio("📐 비율", ["1:1", "16:9", "9:16"], horizontal=True, key="i_ratio")
        
        st.divider()
        gen_img_btn = st.button("🚀 AI 이미지 프롬프트 생성", type="primary", use_container_width=True)

    # 메인 화면 출력 영역
    if gen_img_btn or st.session_state.get('img_ready'):
        st.session_state.img_ready = True
        
        # 제목 및 프롬프트 생성 (한글_영어제목 형식)
        st.session_state.res_img_title = f"{img_subject}_Visual_Art_Concept"
        st.session_state.res_img_prompt = f"A masterpiece of {img_subject}, rendered in a {img_style} style. High-resolution 8k, cinematic lighting, {img_ratio} aspect ratio."

        st.subheader("🏷️ 이미지 제목 (한글_영어제목)")
        st.code(st.session_state.res_img_title, language="text")
        
        st.divider()
        st.subheader("🖼️ 생성 이미지 프롬프트")
        st.text_area("Image Prompt Box", value=st.session_state.res_img_prompt, height=300, key="img_prompt_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_img_prompt, language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 설정을 마치고 생성 버튼을 눌러주세요.")
