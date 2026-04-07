import streamlit as st
import os
import time
import random
import urllib.parse

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # --- 🛠️ CSS 설정 구역 ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 2px !important; }
        
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
        }
        
        .stTextArea textarea { height: 120px !important; } 
        
        /* 제목(라벨)과 입력박스 사이 간격 0px 고정 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: 0px !important; /* 마진 0 적용 */
            padding-top: 6px !important;
            color: #444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 설정 (유튜브 최적화)")
        api_key = get_api_key()

        # 1. 음원 업로드 및 파싱
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
        num_shorts = st.slider("✂️ 쇼츠 이미지 (0~5개)", 0, 5, 2)

        # 복구된 15종 이상의 풍부한 옵션 메뉴
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        lightings = ["자연광", "안개", "네온", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르", "촛불", "석양", "명암", "레이저", "보케", "고대비"]
        s_light = st.selectbox("💡 조명 효과", lightings)

        cameras = ["광각", "매크로", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안", "핸드헬드", "드론", "파노라마", "필름", "망원", "틸트-시프트"]
        s_cam = st.selectbox("📷 카메라 앵글", cameras)

        st.divider()
        gen_btn = st.button("🚀 이미지 생성 시작 (한글 지원)", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 미리보기 및 개별 조절")
        
        if gen_btn:
            if not context_lyrics: st.error("가사를 입력해주세요."); return
            with st.spinner("이미지 엔진 가동 중..."):
                time.sleep(1)
                st.session_state.img_results_data = []
                
                # 규격 설정
                specs = [("메인 (16:9)", 1280, 720), ("틱톡 (9:16)", 720, 1280)]
                for i in range(num_shorts): specs.append((f"쇼츠 {i+1}", 720, 1280))
                
                # 이미지 생성 로직
                for label, w, h in specs:
                    display_text = f"{title_kr}\n{title_en}"
                    encoded_text = urllib.parse.quote(display_text)
                    seed = random.randint(1, 9999)
                    # 한글을 지원하는 Pollinations 엔진 사용
                    url = f"https://image.pollinations.ai/prompt/{encoded_text}?width={w}&height={h}&seed={seed}&nologo=true"
                    st.session_state.img_results_data.append({"label": label, "url": url, "w": w, "h": h})

        # 결과물 렌더링
        if st.session_state.get('img_results_data'):
            results = st.session_state.img_results_data
            kr_fonts = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
            en_fonts = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

            # 1. 메인 이미지 조절
            main_img = results[0]
            with st.container(border=True):
                c_img, c_ctrl = st.columns([1, 1])
                with c_img:
                    st.image(main_img['url'], caption=main_img['label'], use_column_width=True)
                with c_ctrl:
                    st.write("**메인 개별 조절**")
                    st.selectbox("한글 폰트", kr_fonts, key="f_kr_m")
                    st.selectbox("영어 폰트", en_fonts, key="f_en_m")
                    st.slider("위치 상하", 0, 100, 50, key="v_m")
                    st.slider("크기 조절", 10, 100, 50, key="s_m")

            # 2. 세로 이미지 조절 (콤팩트 5열 보기)
            st.write("**📱 세로형 규격 (9:16)**")
            v_items = results[1:]
            cols = st.columns(5)
            for idx, img in enumerate(v_items):
                with cols[idx % 5]:
                    with st.container(border=True):
                        st.image(img['url'], use_column_width=True)
                        st.write(f"<p style='font-size:10px; margin-bottom:2px;'>{img['label']}</p>", unsafe_allow_html=True)
                        # 최소 조절 UI
                        st.selectbox("한글", kr_fonts, key=f"f_kr_{idx}", label_visibility="collapsed")
                        st.selectbox("영어", en_fonts, key=f"f_en_{idx}", label_visibility="collapsed")
                        st.slider("위치", 0, 100, 50, key=f"v_{idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
