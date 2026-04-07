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
        /* 위젯 간 전체 간격 조절 */
        [data-testid="stVerticalBlock"] > div { 
            margin-top: -10px !important;    /* 조절: 위쪽 간격 (-15px~0px) */
            margin-bottom: 2px !important;   /* 조절: 아래쪽 간격 */
        }
        
        /* 드롭다운(Select) 및 입력창(Input) 높이 조절 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important;     /* 조절: 드롭메뉴/입력창 높이 */
            height: 32px !important;         /* 조절: 드롭메뉴/입력창 높이 */
            font-size: 13px !important;      /* 조절: 박스 안 글자 크기 */
        }
        
        /* 가사 입력창 전용 높이 */
        .stTextArea textarea { height: 120px !important; }
        
        /* 제목(라벨) 위치 조절 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important;      /* 조절: 제목 글자 크기 */
            margin-bottom: -10px !important; /* 조절: 제목을 박스에 밀착 (-15px~0px) */
            padding-top: 6px !important;     /* 조절: 제목 위쪽 여백 */
            color: #444 !important;
        }

        /* 폰트 미리보기용 CSS (selectbox 옵션에 적용) */
        /* 검색된 명칭 기반 사실적 시뮬레이션 */
        .font-preview-kr-붓 { font-family: 'cursive', 'Nanum Brush Script', sans-serif !important; font-weight: bold; }
        .font-preview-kr-펜 { font-family: 'Nanum Pen Script', sans-serif !important; }
        .font-preview-kr-꽃길 { font-family: 'SangSangFlower', cursive !important; color: #ff69b4; }
        .font-preview-en-vibes { font-family: 'Great Vibes', cursive !important; font-size: 1.2em; }
        .font-preview-en-dancing { font-family: 'Dancing Script', cursive !important; }
        .font-preview-en-pacifico { font-family: 'Pacifico', cursive !important; color: #333; }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 생성 및 오버레이 설정")

        # 1. 음원 업로드 (파일명 파싱)
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
        context_lyrics = st.text_area("📝 가사 기반 무드 분석", value=lyrics_val)

        st.divider()
        
        # 유튜브용 구성 설정
        st.write("**📱 플랫폼별 수량**")
        c_fix1, c_fix2 = st.columns(2)
        with c_fix1: st.info("📺 메인(16:9): 1개")
        with c_fix2: st.info("📱 틱톡(9:16): 1개 고정")
        num_shorts = st.slider("✂️ 쇼츠용 추가 이미지 (9:16)", 0, 5, 2)

        st.divider()
        gen_btn = st.button("🚀 무료 이미지 생성 테스트 시작", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물 및 개별 오버레이 조절")
        
        # 한글 깨짐 현상 안내
        st.warning("💡 현재 무료 테스트 단계이므로 한글 제목은 깨져서 표시됩니다. 깨짐을 고치기 위해 이미지 출력 시 영어 제목만 표시하도록 임시로 조치했습니다.")

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
                    text = "Generation+Failed" if is_failed else label.replace(" ", "+")
                    # 플레이스홀더 기본 URL 저장
                    base_url = f"https://placehold.co/{size}/{color}/fff.png"
                    st.session_state.img_results_data.append({"label": label, "url": base_url, "size": size})
                
                if is_failed: st.warning("일부 이미지 생성에 실패하여 회색으로 표시됩니다.")

        # 결과 출력 및 각 이미지별 조절 패널 배치
        if st.session_state.get('img_results_data'):
            results = st.session_state.img_results_data
            
            # 사실적 필기체/캘리그라피 명칭 리스트 및 미리보기 UI 적용
            # 한글 제목 스타일 (cite: image_0.png, image_1.png)
            kr_fonts_names = [
                ":kr: 나눔붓붓", ":kr: 나눔펜펜", ":kr: 상상꽃길꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", 
                "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"
            ]
            # Streamlit selectbox는 HTML 렌더링을 지원하지 않으므로, 이 방식은 작동하지 않습니다.
            # 대안으로 st.markdown으로 드롭다운 외부에서 폰트 미리보기를 시뮬레이션합니다.
            
            # 영어 제목 스타일 (cite: image_2.png, image_3.png)
            en_fonts_names = [
                "Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", 
                "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", 
                "Playball", "Alex Brush", "Monsieur"
            ]

            # 폰트 미리보기 시뮬레이션 (드롭다운 위에 배치)
            st.write("**🎨 폰트 스타일 미리보기 (필기체 위주)**")
            f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns(6)
            f_col1.markdown('<span class="font-preview-kr-붓">나눔붓붓</span>', unsafe_allow_html=True)
            f_col2.markdown('<span class="font-preview-kr-펜">나눔펜펜</span>', unsafe_allow_html=True)
            f_col3.markdown('<span class="font-preview-kr-꽃길">상상꽃길꽃길</span>', unsafe_allow_html=True)
            f_col4.markdown('<span class="font-preview-en-vibes">Great Vibes</span>', unsafe_allow_html=True)
            f_col5.markdown('<span class="font-preview-en-dancing">Dancing Script</span>', unsafe_allow_html=True)
            f_col6.markdown('<span class="font-preview-en-pacifico">Pacifico</span>', unsafe_allow_html=True)
            st.divider()

            # 1. 유튜브 메인 (16:9) 고정 1개
            main_img = results[0]
            with st.container(border=True):
                # 이미지 옆에 조절 패널 배치 (50% 싸이즈 미리보기 구현)
                col_img_main, col_ctrl_main = st.columns([1, 1]) 
                
                with col_img_main:
                    # 싸이즈 50% 줄임 미리보기 구현을 위해 use_column_width=True 사용
                    # 한글 깨짐 수정을 위해 영어 제목만 오버레이 (title_en)
                    st.image(main_img['url'] + f"?text={title_en}", caption=main_img['size'], use_column_width=True)
                
                with col_ctrl_main:
                    st.write(f"**{main_img['label']} 오버레이 조절**")
                    # 개별 조절 UI ( Unique key 사용)
                    st.selectbox("한글 제목 필기체", [f.strip(':kr:') for f in kr_fonts_names], key="font_kr_main")
                    st.selectbox("영어 제목 필기체", en_fonts_names, key="font_en_main")
                    
                    st.slider("상하 위치", 0, 100, 50, key="pos_v_main")
                    st.slider("좌우 위치", 0, 100, 50, key="pos_h_main")
                    st.slider("크기 조절", 10, 100, 50, key="size_main")

            # 2. 세로 이미지 규격 (9:16) - 틱톡 고정 1개 + 쇼츠 선택 0~5개
            vertical_results = results[1:]
            
            if vertical_results:
                st.write("**📱 플랫폼별 세로형 규격 (9:16) 및 개별 조절**")
                # 3열 그리드 배치로 한눈에 보기 구현
                cols_grid = st.columns(3)
                
                for idx, img in enumerate(vertical_results):
                    # 각 열 안에 컨테이너를 만들어 이미지와 조절 패널 배치
                    with cols_grid[idx % 3].container(border=True):
                        # 한글 깨짐 수정을 위해 영어 제목만 오버레이 (title_en)
                        # 싸이즈 50% 줄임 미리보기 구현을 위해 use_column_width=True 사용
                        st.image(img['url'] + f"?text={title_en}", caption=img['size'], use_column_width=True)
                        
                        # 각 세로 이미지별 개별 조절 UI (Unique key 사용)
                        st.selectbox("한글 필기체", [f.strip(':kr:') for f in kr_fonts_names], key=f"font_kr_{idx}")
                        st.selectbox("영어 필기체", en_fonts_names, key=f"font_en_{idx}")
                        
                        col_pos1, col_pos2 = st.columns(2)
                        with col_pos1: st.slider("상하", 0, 100, 50, key=f"pos_v_{idx}")
                        with col_pos2: st.slider("좌우", 0, 100, 50, key=f"pos_h_{idx}")
                        st.slider("크기", 10, 100, 50, key=f"size_{idx}")
            
            st.info("💡 곡 분위기에 최적화된 배경 위에 지정한 스타일과 위치로 제목을 렌더링하려면 실제 유료 AI API 연동이 필요합니다.")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
