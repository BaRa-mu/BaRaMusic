import streamlit as st
import os
import time
import random # [확실함] 실패 시뮬레이션을 위한 랜덤 함수

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # --- 🛠️ [직접 조절 구역] 수치를 변경하며 간격을 맞추세요 ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { 
            margin-top: 0px !important;    /* 위쪽 간격 */
            margin-bottom: 2px !important;   /* 아래쪽 간격 */
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
        }
        .stTextArea textarea { height: 120px !important; } /* 가사창 전용 높이 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: -10px !important; color: #444 !important; padding-top: 6px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 유튜브용 이미지 생성 테스트")
        
        # [확실함] 플레이스홀더 생성에는 API 키가 필요 없으나, UI 흐름상 저장 유도
        # 실제 무료 테스트 시에는 키를 넣지 않아도 되게끔 로직 수정.

        # 1. 음원 업로드 및 제목 자동 추출
        aud_file = st.file_uploader("🎧 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr, t_en = parts[0], parts[1] if len(parts) > Part else ""

        # [확실함] 한글/영어 제목 한 줄 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # [확실함] 가사 수동 입력 (가사 탭 연동)
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 기반 무드 분석", value=lyrics_val)

        st.divider()
        
        # [확실함] 유튜브용 구성 설정 (고정 및 선택)
        st.write("**📱 플랫폼별 수량 설정**")
        c_fix1, c_fix2 = st.columns(2)
        with c_fix1: st.info("📺 메인(16:9): 1개 고정 (1280x720)")
        with c_fix2: st.info("📱 틱톡(9:16): 1개 고정 (720x1280)")
        num_shorts = st.slider("✂️ 쇼츠용 추가 이미지 (9:16)", 0, 5, 2)

        # [확실함] 실제 생성 AI가 아니므로 효과 메뉴는 UI로만 유지
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀리즘", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        st.divider()
        gen_btn = st.button("🚀 유튜브 최적화 무료 이미지 생성 테스트", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not context_lyrics: st.error("가사 무드를 입력하세요."); return
            
            with st.spinner("플레이스홀더 이미지를 규격에 맞춰 생성 중입니다..."):
                # [확실함] 무료 이미지 생성 시뮬레이션
                time.sleep(1.5)
                
                # [확실함] 랜덤 실패 확률 도입 (요구사항 반영)
                # 10% 확률로 실패로 간주
                generation_failed = random.random() < 0.1
                
                st.session_state.gen_images_data = [] # 기존 이미지 초기화
                
                if generation_failed:
                    # [확실함] 실패 시 회색 이미지 Fallback 로직
                    # 메인 (16:9)
                    st.session_state.gen_images_data.append({
                        "label": "📺 유튜브 메인 (16:9)",
                        "url": "https://placehold.co/1280x720/808080/fff.png?text=Generation+Failed",
                        "size": "1280x720"
                    })
                    # 틱톡 (9:16)
                    st.session_state.gen_images_data.append({
                        "label": "📱 틱톡 (9:16)",
                        "url": "https://placehold.co/720x1280/808080/fff.png?text=Generation+Failed",
                        "size": "720x1280"
                    })
                    # 쇼츠 (9:16)
                    for i in range(num_shorts):
                        st.session_state.gen_images_data.append({
                            "label": f"✂️ 유튜브 쇼츠 {i+1} (9:16)",
                            "url": "https://placehold.co/720x1280/808080/fff.png?text=Generation+Failed",
                            "size": "720x1280"
                        })
                    st.warning("일부 이미지 생성에 실패하여 회색으로 표시됩니다.")
                
                else:
                    # [확실함] 성공 시 플레이스홀더 이미지 생성 로직
                    # 메인 (16:9) 1개 고정
                    st.session_state.gen_images_data.append({
                        "label": "📺 유튜브 메인 (16:9)",
                        "url": f"https://placehold.co/1280x720.png?text=YouTube+Main+(16:9)",
                        "size": "1280x720"
                    })
                    
                    # 틱톡 (9:16) 1개 고정
                    st.session_state.gen_images_data.append({
                        "label": "📱 틱톡 (9:16)",
                        "url": f"https://placehold.co/720x1280.png?text=TikTok+(9:16)",
                        "size": "720x1280"
                    })
                    
                    # 쇼츠 (9:16) 0~5개 선택
                    for i in range(num_shorts):
                        st.session_state.gen_images_data.append({
                            "label": f"✂️ 유튜브 쇼츠 {i+1} (9:16)",
                            "url": f"https://placehold.co/720x1280.png?text=YouTube+Shorts+{i+1}+(9:16)",
                            "size": "720x1280"
                        })
                    st.success("플레이스홀더 이미지 생성이 완료되었습니다. (무료 테스트)")

        # [확실함] 세션 상태 체크 후 이미지 출력
        if st.session_state.get('gen_images_data'):
            images_data = st.session_state.gen_images_data
            
            # 메인 영상 (가로 16:9)
            main_img = images_data[0]
            with st.container(border=True):
                st.write(f"**{main_img['label']}**")
                st.image(main_img['url'], caption=f"규격: {main_img['size']}")
            
            st.write("**📱 세로 규격 이미지 (9:16)**")
            # 틱톡 + 쇼츠 이미지를 grid로 배치 (답답함 해소)
            vertical_images = images_data[1:]
            
            # 3열 grid 구성
            cols_per_row = 3
            rows = (len(vertical_images) + cols_per_row - 1) // cols_per_row
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                for col_idx in range(cols_per_row):
                    img_idx = row * cols_per_row + col_idx
                    if img_idx < len(vertical_images):
                        img = vertical_images[img_idx]
                        with cols[col_idx].container(border=True):
                            st.write(f"**{img['label']}**")
                            st.image(img['url'], caption=f"규격: {img['size']}", use_column_width=True)
            
            st.info("💡 테스트 단계이므로 플레이스홀더 이미지가 생성되었습니다. 실제 유료 API를 연동하면 곡 분위기에 최적화된 배경을 얻을 수 있습니다.")
        else:
            st.info("👈 설정을 마친 후 생성 버튼을 눌러주세요.")
