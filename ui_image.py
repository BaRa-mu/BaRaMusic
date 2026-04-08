import streamlit as st

def render_tab2():
    # 모든 설정 메뉴를 사이드바(왼쪽)로 복구
    with st.sidebar:
        st.subheader("🎨 이미지 상세 설정")
        img_subject = st.text_input("💡 이미지 주제", placeholder="이미지의 핵심 주제 입력", key="i_subject")
        img_style = st.selectbox(
            "🎭 화풍 선택", 
            ["극사실주의", "디즈니 애니메이션", "유화", "수채화", "사이버펑크", "신비로운 판타지", "연필 스케치", "3D 렌더링", "레트로 픽셀"], 
            key="i_style"
        )
        img_mood = st.selectbox(
            "✨ 이미지 분위기",
            ["웅장한", "따뜻한", "차가운", "몽환적인", "어두운", "밝고 화사한", "빈티지한"],
            key="i_mood_sel"
        )
        img_ratio = st.radio("📐 가로세로 비율", ["1:1", "16:9", "9:16"], horizontal=True, key="i_ratio")
        
        st.divider()
        gen_img_btn = st.button("🚀 AI 이미지 프롬프트 생성", type="primary", use_container_width=True)

    # 메인 화면 출력 영역
    if gen_img_btn or st.session_state.get('img_ready'):
        st.session_state.img_ready = True
        
        # [결과 고정] 제목: 한글_영어제목 형식
        st.session_state.res_img_title = f"{img_subject}_Visual_Art_Concept"
        
        # [프롬프트 생성] 상세 옵션 반영
        st.session_state.res_img_prompt = (
            f"A high-quality masterpiece of {img_subject}. Style: {img_style}. "
            f"Overall atmosphere is {img_mood}. Optimization for {img_ratio} aspect ratio. "
            f"Cinematic lighting, 8k resolution, highly detailed textures, trending on artstation, professional digital art."
        )

        st.subheader("🏷️ 이미지 제목 (한글_영어제목)")
        st.code(st.session_state.res_img_title, language="text")
        
        st.divider()
        st.subheader("🖼️ 생성 이미지 프롬프트")
        st.text_area("Image Prompt Box", value=st.session_state.res_img_prompt, height=250, key="img_prompt_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_img_prompt, language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 이미지 설정을 마치고 생성 버튼을 눌러주세요.")
