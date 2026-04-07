import streamlit as st

def render_tab3():
    st.header("🎬 최종 영상 생성")
    
    # 이미지가 정상적으로 생성되었는지 확인
    if "bg_m" in st.session_state and st.session_state.bg_m is not None:
        st.info("✅ 앞서 준비된 배경 이미지를 사용하여 영상을 제작합니다.")
        st.image(st.session_state.bg_m, width=400)
    else:
        st.warning("⚠️ 준비된 배경 이미지가 없습니다. 영상 전용 기본 배경으로 렌더링을 진행합니다.")
    
    # 영상 렌더링 버튼 및 로직
    if st.button("▶️ 영상 렌더링 시작", type="primary"):
        with st.spinner("영상을 렌더링하고 있습니다..."):
            # 실제 영상 생성 로직이 들어갈 자리
            st.success("영상 렌더링이 완료되었습니다!")