import streamlit as st

def render_tab2():
    # 모든 입력을 왼쪽 사이드바에 배치
    with st.sidebar:
        st.divider()
        st.subheader("💡 이미지 주제")
        img_subject = st.text_input("주제 입력", placeholder="이미지의 핵심 주제 입력", key="i_subject", label_visibility="collapsed")
        
        st.divider()
        st.subheader("📂 참고 파일 업로드")
        uploaded_file = st.file_uploader("Browse files", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
        
        st.divider()
        st.subheader("🏷️ 이미지 제목 (입력)")
        img_title_input = st.text_input("Image Title", placeholder="이미지 제목 입력 (예: 은혜의 아침)", key="img_title_input_field", label_visibility="collapsed")
        
        st.divider()
        st.subheader("🎨 이미지 상세 설정")
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

    # --- 오른쪽 메인 화면: 결과 출력 ---
    if gen_img_btn or st.session_state.get('img_ready'):
        st.session_state.img_ready = True
        
        # 제목: 한글_영어제목 형식
        res_title_head = img_title_input if img_title_input else img_subject
        st.session_state.res_img_title = f"{res_title_head}_Visual_Art_Concept"
        st.session_state.res_img_prompt = (
            f"A high-quality masterpiece of {img_subject}. Style: {img_style}. Mood: {img_mood}. "
            f"Optimized for {img_ratio} ratio. Cinematic lighting, 8k, professional digital art."
        )

        st.subheader("🏷️ 확정 이미지 제목 (한글_영어제목)")
        st.code(st.session_state.res_img_title, language="text")
        
        st.divider()
        st.subheader("🖼️ 생성 이미지 프롬프트")
        st.text_area("Image Prompt Box", value=st.session_state.res_img_prompt, height=250, key="img_prompt_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_img_prompt, language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 주제를 입력하고 설정을 마친 뒤 생성 버튼을 눌러주세요.")
