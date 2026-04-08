import streamlit as st

def render_tab3():
    # [왼쪽 사이드바] 상세 설정 드롭다운 메뉴들 배치
    with st.sidebar:
        st.subheader("🎬 영상 상세 설정")
        vid_style = st.selectbox(
            "🎨 영상 스타일",
            ["시네마틱 실사", "2D 애니메이션", "3D 애니메이션", "스톱모션", "슬로 모션"],
            key="v_style_sel"
        )
        vid_motion = st.select_slider(
            "🎥 모션 강도", 
            options=["정적인", "부드러운", "역동적인", "매우 강렬한"],
            value="부드러운",
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

    # --- [오른쪽 메인 화면: 원래대로 복구] ---
    # 복구 1: 영상 주제 입력창
    st.subheader("💡 영상 연출 주제")
    vid_subject = st.text_input("영상 주제", placeholder="영상 연출 주제 입력", key="v_subject", label_visibility="collapsed")
    
    st.divider()
    
    # 복구 2: 파일 업로드 칸 (Browse files)
    st.subheader("📂 참고 파일 업로드")
    uploaded_vid = st.file_uploader("Browse files", type=["png", "jpg", "jpeg", "mp4", "mov"], key="vid_uploader", label_visibility="collapsed")
    
    st.divider()
    
    # 복구 3: 영상 제목 입력 란
    st.subheader("🏷️ 영상 제목 (입력)")
    vid_title_input = st.text_input("Video Title", placeholder="영상 제목 입력", key="vid_title_input_field", label_visibility="collapsed")
    
    st.divider()

    # 결과 출력 영역
    if gen_vid_btn or st.session_state.get('vid_ready'):
        st.session_state.vid_ready = True
        
        # [결과 고정] 제목: 한글_영어제목 형식
        res_vid_title_head = vid_title_input if vid_title_input else vid_subject
        st.session_state.res_vid_title = f"{res_vid_title_head}_Cinematic_Motion_Vision"
        
        # [프롬프트 생성] 상세 옵션 반영
        st.session_state.res_vid_prompt = (
            f"Cinematic {vid_length} video showing {vid_subject}. Style: {vid_style}. "
            f"Camera movement: {vid_camera} with {vid_motion} intensity. "
            f"Fluid motion, professional color grading, visual effects."
        )

        st.subheader("🏷️ 확정 영상 제목 (한글_영어제목)")
        st.code(st.session_state.res_vid_title, language="text")
        
        st.divider()
        st.subheader("📽️ AI 영상 제작 프롬프트")
        st.text_area("Video Prompt Box", value=st.session_state.res_vid_prompt, height=200, key="vid_prompt_view", label_visibility="collapsed")
        if st.button("📋 프롬프트 복사"):
            st.code(st.session_state.res_vid_prompt, language="text")
    else:
        st.info("👈 왼쪽 사이드바에서 설정을 마치고 생성 버튼을 눌러주세요. 필요시 파일을 업로드하세요.")
