import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 데이터 상수 보호
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script"]

def render_tab2():
    # 1. 메뉴 간격 초압축 CSS
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -18px !important; margin-bottom: -5px !important; }
        .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { 
            margin-bottom: -12px !important; padding-top: 0px !important; font-size: 11px !important; 
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            height: 28px !important; min-height: 28px !important; font-size: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        # [확실함] 2. 파싱 및 상태 주입 (즉시 반영)
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        if aud_file:
            base = os.path.splitext(aud_file.name)[0]
            if "_" in base:
                parts = base.split('_')
                if 'in_kr' not in st.session_state or st.session_state.in_kr == "":
                    st.session_state.in_kr, st.session_state.in_en = parts[0], parts[1]

        # 제목 가로 나열을 위해 columns 배치
        t1, t2 = st.columns(2)
        with t1: t_kr = st.text_input("📌 한글 제목", key="in_kr")
        with t2: t_en = st.text_input("📌 영문 제목", key="in_en")
        
        c_lyrics = st.text_area("📝 가사 무드", value=st.session_state.get('gen_lyrics', ""), height=80, key="in_l")

        st.divider()
        num_s = st.slider("✂️ 쇼츠", 0, 5, 2, key="n_s")
        st.selectbox("🎨 스타일", ["사진", "유화", "판타지", "사이버펑크"], key="s_st")
        st.selectbox("💡 조명", ["자연광", "네온", "시네마틱"], key="s_li")
        st.selectbox("📷 앵글", ["광각", "클로즈업", "조감도"], key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs = [{"l": "메인", "w": 1280, "h": 720}, {"l": "틱톡", "w": 720, "h": 1280}] + \
                                    [{"l": f"쇼츠{i+1}", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            for idx, item in enumerate(st.session_state.imgs):
                with st.container(border=True):
                    c_i, c_c = st.columns([1.5, 1])
                    with c_c:
                        # [확실함] 개별 조절 UI 복구
                        st.write(f"**{item['l']}**")
                        v = st.slider("위치", 0, 100, 50, key=f"v_{idx}")
                        sk = st.slider("한글 크기", 10, 150, 50, key=f"sk_{idx}")
                        se = st.slider("영어 크기", 10, 150, 40, key=f"se_{idx}")
                        st.selectbox("한글 폰트", KR_FONTS, key=f"fk_{idx}")
                        st.selectbox("영어 폰트", EN_FONTS, key=f"fe_{idx}")
                    with c_i:
                        # 3. 로컬 렌더링 (한글 깨짐 차단)
                        img = Image.new('RGB', (item['w'], item['h']), (50, 60, 50))
                        draw = ImageDraw.Draw(img)
                        # [확실함] 제목 가로 나열 렌더링
                        try: font = ImageFont.truetype("NanumGothicBold.ttf", sk)
                        except: font = ImageFont.load_default()
                        full_title = f"{t_kr}  |  {t_en}" # 가로 나열
                        draw.text((item['w']/2, item['h']*(v/100)), full_title, font=font, fill=(255,255,255), anchor="mm")
                        st.image(img, use_column_width=True)
        else: st.info("👈 설정을 마친 후 생성을 시작하세요.")
