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
        /* [1] 위젯 간 전체 간격 조절 */
        [data-testid="stVerticalBlock"] > div { 
            margin-top: -10px !important; 
            margin-bottom: 2px !important; 
        }
        
        /* [2] 드롭다운 및 입력창 높이 조절 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
        }
        
        /* [3] 가사 입력창 전용 높이 */
        .stTextArea textarea { height: 120px !important; }
        
        /* [4] 한글제목/라벨과 입력박스 사이 간격 조절 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: 0px !important; /* 이 값을 조절하여 박스와 붙이거나 띄움 */
            padding-top: 6px !important;
            color: #444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 설정")
        api_key = get_api_key()

        # 1. 음원 업로드
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr, t_en = parts[0], parts[1] if len(parts) > 1 else ""

        # 제목 한 줄 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # 가사 수동 입력
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 무드 분석", value=lyrics_val)

        st.divider()
        
        # 수량 설정
        st.write("**📱 플랫폼별 수량**")
        st.info("📺 메인(16:9) / 📱 틱톡(9:16) 고정")
        num_shorts = st.slider("✂️ 쇼츠 이미지 (0~5개)", 0, 5, 2)

        # 드롭다운 메뉴 (건드리지 않은 순수 리스트)
        s_style = st.selectbox("🎨 예술 스타일", ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실", "팝아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"])

        st.divider()
        gen_btn = st.button("🚀 무료 이미지 생성 테스트", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 미리보기 및 개별 조절")
        
        if gen_btn:
            if not context_lyrics: st.error("가사를 입력해주세요."); return
            with st.spinner("이미지 생성 중..."):
                time.sleep(1)
                is_failed = random.random() < 0.1
                st.session_state.img_results_data = []
                
                # 규격 설정
                specs = [("메인 (16:9)", "1280x720"), ("틱톡 (9:16)", "720x1280")]
                for i in range(num_shorts): specs.append((f"쇼츠 {i+1}", "720x1280"))
                
                for label, size in specs:
                    color = "808080" if is_failed else f"{random.randint(20,80)}a{random.randint(20,80)}b"
                    url = f"https://placehold.co/{size}/{color}/fff.png"
                    st.session_state.img_results_data.append({"label": label, "url": url, "size": size})

        if st.session_state.get('img_results_data'):
            results = st.session_state.img_results_data
            
            # 폰트 리스트
            kr_fonts = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
            en_fonts = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

            # 1. 메인 이미지 (가로 16:9)
            main_img = results[0]
            with st.container(border=True):
                c_img, c_ctrl = st.columns([1, 1])
                with c_img:
                    st.image(main_img['url'] + f"?text={title_en}", caption=main_img['label'], use_column_width=True)
                with c_ctrl:
                    st.write("**메인 조절**")
                    st.selectbox("한글 폰트", kr_fonts, key="f_kr_m")
                    st.selectbox("영어 폰트", en_fonts, key="f_en_m")
                    st.slider("위치 상하", 0, 100, 50, key="v_m")
                    st.slider("크기", 10, 100, 50, key="s_m")

            st.write("**📱 세로 규격 (9:16) - 콤팩트 보기**")
            
            # 2. 세로 이미지 (9:16) - 5열 배치로 크기를 아주 작게 줄임
            v_items = results[1:]
            cols = st.columns(5) # 5열로 나누어 크기를 작게 조절
            for idx, img in enumerate(v_items):
                with cols[idx % 5]:
                    with st.container(border=True):
                        # 이미지 크기를 작게 유지
                        st.image(img['url'] + f"?text={title_en}", use_column_width=True)
                        st.write(f"<p style='font-size:10px; margin-bottom:2px;'>{img['label']}</p>", unsafe_allow_html=True)
                        
                        # 각 이미지별 최소 조절 도구 (공간 절약을 위해 드롭다운만 배치)
                        st.selectbox("한글", kr_fonts, key=f"f_kr_{idx}", label_visibility="collapsed")
                        st.selectbox("영어", en_fonts, key=f"f_en_{idx}", label_visibility="collapsed")
                        st.slider("위치", 0, 100, 50, key=f"v_{idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
