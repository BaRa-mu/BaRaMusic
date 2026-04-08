import streamlit as st

def render_tab3():
    # [1. 세션 상태 초기화]
    if 'vid_ready' not in st.session_state:
        st.session_state['vid_ready'] = False
    if 'res_vid_prompt' not in st.session_state:
        st.session_state['res_vid_prompt'] = ""

    # [2. 왼쪽 사이드바 구성]
    with st.sidebar:
        st.divider()
        st.subheader("📂 참고 파일 업로드")
        uploaded_vid = st.file_uploader("Browse files", type=["png", "jpg", "jpeg", "mp4", "mov"], key="vid_uploader", label_visibility="collapsed")
        
        st.divider()
        st.subheader("🏷️ 영상 제목 (입력)")
        vid_title_input = st.text_input("Video Title", placeholder="영상 제목 입력", key="vid_title_input_field", label_visibility="collapsed")
        
        st.divider()
        st.subheader("🎬 영상 상세 설정")
        vid_style = st.selectbox(
            "🎨 영상 스타일",
            ["시네마틱 실사", "2D 애니메이션", "3D 애니메이션", "스톱모션", "슬로 모션"],
            key="v_style_sel"
        )
        vid_motion = st.select_slider(
            "🎥 모션 강도", 
            options=["정적인", "부드러운", "역동적인", "매우 강렬한"],
            key="v_motion_slider"
        )
        vid_camera = st.selectbox(
            "📹 카메라 워킹",
            ["줌 인(Zoom In)", "줌 아웃(Zoom Out)", "패닝(Panning)", "틸트(Tilt)", "드론 샷"],
            key="v_camera_sel"
        )
        vid_length = st.selectbox("⏱️ 영상 길이", ["5초", "10초", "15초(최대)"], key="v_len_sel")
        
        st.divider()
        gen_vid_btn = st.button("🚀 AI 영상 프롬프트 생성", type="primary", use_container_width=True)

    # --- [3. 오른쪽 메인 화면: 결과물 분리 출력] ---
    if gen_vid_btn or st.session_state['vid_ready']:
        st.session_state['vid_ready'] = True
        
        # 제목 분리 처리
        res_k_vid_title = vid_title_input if vid_title_input else "제목없음"
        res_e_vid_title = "Eternal_Grace_Cinematic_Motion"
        
        st.subheader("🇰🇷 한글 영상 제목")
        st.code(res_k_vid_title, language="text")
        
        st.subheader("🇺🇸 영어 영상 제목")
        st.code(res_e_vid_title, language="text")
        
        st.divider()
        
        # 프롬프트 생성 (딕셔너리 방식으로 저장)
        st.session_state['res_vid_prompt'] = (
            f"Cinematic {vid_length} video of {res_k_vid_title}. Style: {vid_style}. "
            f"Motion: {vid_motion}, Camera: {vid_camera}. High-end production quality, 4k."
        )

        st.subheader("📽️ AI 영상 제작 프롬프트")
        st.text_area("Video Prompt Box", value=st.session_state['res_vid_prompt'], height=200, key="vid_prompt_view", label_visibility="collapsed")
        
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state['res_vid_prompt'], language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 설정을 마친 뒤 생성 버튼을 눌러주세요.")
