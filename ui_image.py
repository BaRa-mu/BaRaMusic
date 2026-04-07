import streamlit as st
import os
import time
import random

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # --- 🛠️ [직접 조절 구역] 수치를 변경하며 간격을 맞추세요 ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { 
            margin-top: -10px !important;    /* 위쪽 간격 */
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
        
        # 음원 업로드 및 제목 자동 추출
        aud_file = st.file_uploader("🎧 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr = parts[0]
            t_en = parts[1] if len(parts) > 1 else ""

        # 한글/영어 제목 한 줄(Row) 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # 가사 수동 입력 (편집 가능)
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 무드 분석", value=lyrics_val)

        st.divider()
        
        # 유튜브용 구성 설정
        st.write("**📱 플랫폼별 수량**")
        c_fix1, c_fix2 = st.columns(2)
        with c_fix1: st.info("📺 메인(16:9): 1개 고정")
        with c_fix2: st.info("📱 틱톡(9:16): 1개 고정")
        num_shorts = st.slider("✂️ 쇼츠용 추가 이미지 (9:16)", 0, 5, 2)

        # 다채로운 효과 (UI 유지)
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실", "팝아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        st.divider()
        gen_btn = st.button("🚀 유튜브 최적화 무료 이미지 생성 테스트 시작", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물 및 개별 오버레이 조절")
        
        # 플레이스홀더 한계 설명 보강
        st.info("💡 현재는 무료 테스트 단계이므로 곡 제목이 중앙에 오버레이된 플레이스홀더 이미지가 생성됩니다. 옆의 슬라이더(필기체, 위치, 크기)는 실제 유료 AI API를 연동할 때 적용될 설정을 테스트하는 용도이며, 현재 플레이스홀더 이미지에는 반영되지 않습니다.")

        if gen_btn:
            if not context_lyrics: st.error("가사 무드를 입력해주세요."); return
            with st.spinner("플레이스홀더 이미지를 플랫폼 규격에 맞춰 생성 중..."):
                time.sleep(1.5) # 시뮬레이션
                
                # 랜덤 실패 확률 (10% 확률로 회색 Fallback)
                is_failed = random.random() < 0.1
                st.session_state.img_results_data = [] # 기존 이미지 초기화
                
                # 유튜브 구성 데이터 생성
                specs = [("📺 유튜브 메인 (16:9)", "1280x720"), ("📱 틱톡 (9:16)", "720x1280")]
                for i in range(num_shorts): specs.append((f"✂️ 유튜브 쇼츠 {i+1} (9:16)", "720x1280"))
                
                for label, size in specs:
                    color = "808080" if is_failed else f"{random.randint(10,99)}a{random.randint(10,99)}b"
                    # 데이터 생성 시 시스템 텍스트("YouTube Main") 제거, 순수 배경만 생성
                    base_url = f"https://placehold.co/{size}/{color}/fff.png"
                    st.session_state.img_results_data.append({"label": label, "url": base_url, "size": size})
                
                if is_failed: st.warning("일부 이미지 생성에 실패하여 회색으로 표시됩니다.")

        # 결과 출력 및 각 이미지별 조절 패널 배치
        if st.session_state.get('img_results_data'):
            results = st.session_state.img_results_data
            
            # 사실적 필기체/캘리그라피 명칭 리스트
            kr_fonts_names = [
                "나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", 
                "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"
            ]
            en_fonts_names = [
                "Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", 
                "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", 
                "Playball", "Alex Brush", "Monsieur"
            ]

            # 1. 유튜브 메인 (16:9) 고정 1개
            main_img = results[0]
            with st.container(border=True):
                # 이미지 옆에 조절 패널 배치 (50% 싸이즈 미리보기 구현)
                col_img_main, col_ctrl_main = st.columns([1, 1]) 
                
                with col_img_main:
                    # 싸이즈 50% 줄임 미리보기 구현을 위해 use_column_width=True 사용
                    # 플레이스홀더 URL에 parameters로 사용자 입력 제목만 오버레이 시뮬레이션
                    st.image(main_img['url'] + f"?text={title_kr}%0A{title_en}", caption=main_img['size'], use_column_width=True)
                
                with col_ctrl_main:
                    st.write(f"**{main_img['label']} 오버레이 조절**")
                    # 개별 조절 UI
                    st.selectbox("한글 제목 필기체", kr_fonts_names, key="font_kr_main")
                    st.selectbox("영어 제목 필기체", en_fonts_names, key="font_en_main")
                    
                    st.slider("상하 위치", 0, 100, 50, key="pos_v_main")
                    st.slider("좌우 위치", 0, 100, 50, key="pos_h_main")
                    st.slider("크기 조절", 10, 100, 50, key="size_main")

            # 2. 세로 이미지 규격 (9:16) - 틱톡 고정 1개 + 쇼츠 선택 0~5개
            vertical_results = results[1:]
            
            if vertical_results:
                st.write("**📱 플랫폼별 세로형 규격 (9:16) 및 개별 조절**")
                # 2열 grid 구성으로 가로 공간 활용
                cols_grid = st.columns(2)
                
                for idx, img in enumerate(vertical_results):
                    # 각 열 안에 컨테이너를 만들어 이미지와 조절 패널 배치
                    with cols_grid[idx % 2].container(border=True):
                        # 싸이즈 50% 줄임 미리보기 구현을 위해 use_column_width=True 사용
                        st.image(img['url'] + f"?text={title_kr}%0A{title_en}", caption=img['size'], use_column_width=True)
                        
                        # 각 세로 이미지별 개별 조절 UI (Unique key 사용)
                        st.selectbox("한글 필기체", kr_fonts_names, key=f"font_kr_{idx}")
                        st.selectbox("영어 필기체", en_fonts_names, key=f"font_en_{idx}")
                        
                        col_pos1, col_pos2 = st.columns(2)
                        with col_pos1: st.slider("상하", 0, 100, 50, key=f"pos_v_{idx}")
                        with col_pos2: st.slider("좌우", 0, 100, 50, key=f"pos_h_{idx}")
                        st.slider("크기", 10, 100, 50, key=f"size_{idx}")
            
            st.info("💡 곡 분위기에 최적화된 배경 위에 지정한 스타일과 위치로 제목을 렌더링하려면 실제 유료 AI API 연동이 필요합니다.")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
