import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 15종 이상의 전문 데이터 (유실 방지)
STYLE_LIST = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"]
LIGHT_LIST = ["자연광", "안개", "네온", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르", "촛불", "석양", "명암", "레이저", "보케", "고대비"]
CAM_LIST = ["광각", "매크로", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안", "드론", "파노라마", "필름", "망원", "틸트-시프트"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def render_tab2():
    # [수정] 메뉴 간격 최소화 및 마진 0px (겹치지 않게 조절)
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -11px !important; margin-bottom: 0px !important; }
        .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { 
            margin-bottom: 0px !important; padding-top: 4px !important; font-size: 11px !important; font-weight: 600 !important;
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            height: 30px !important; min-height: 30px !important; font-size: 13px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        # 1. 파일 업로드 및 자동 파싱
        aud_file = st.file_uploader("🎧 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        if aud_file:
            base = os.path.splitext(aud_file.name)[0]
            if "_" in base:
                parts = base.split('_')
                st.session_state.in_kr = parts[0]
                st.session_state.in_en = parts[1] if len(parts) > 1 else ""

        t_kr = st.text_input("📌 한글 제목", key="in_kr")
        t_en = st.text_input("📌 영문 제목", key="in_en")
        c_lyrics = st.text_area("📝 가사 무드", value=st.session_state.get('gen_lyrics', ""), height=80, key="in_l")

        st.divider()
        num_s = st.slider("✂️ 쇼츠 추가", 0, 5, 2, key="n_s")
        st.selectbox("🎨 스타일", STYLE_LIST, key="s_st")
        st.selectbox("💡 조명", LIGHT_LIST, key="s_li")
        st.selectbox("📷 앵글", CAM_LIST, key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs_data = [{"label": "유튜브 메인 (16:9)", "w": 1280, "h": 720}, {"label": "틱톡 (9:16)", "w": 720, "h": 1280}] + \
                                         [{"label": f"유튜브 쇼츠 {i+1} (9:16)", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            # [확실함] 세로 이미지도 메인처럼 큰 가로 너비(Horizontal Width)를 갖도록 개별 배치
            for idx, item in enumerate(st.session_state.get('imgs_data', [])):
                with st.container(border=True):
                    # 모든 미리보기를 동일한 2열 구조(이미지 1.5 : 조절부 1)로 배치하여 가로 사이즈 확보
                    c_i, c_c = st.columns([1.5, 1])
                    with c_c:
                        st.write(f"**{item.get('label')}**")
                        v = st.slider("상하 위치", 0, 100, 50, key=f"v_{idx}")
                        sk = st.slider("한글 크기", 10, 200, 55, key=f"sk_{idx}")
                        se = st.slider("영어 크기", 10, 200, 35, key=f"se_{idx}")
                        st.selectbox("한글 폰트", KR_FONTS, key=f"fk_{idx}")
                        st.selectbox("영어 폰트", EN_FONTS, key=f"fe_{idx}")
                    with c_i:
                        # [확실함] 한글 [줄바꿈] 영어 렌더링 엔진 (PIL 로컬 엔진)
                        img = Image.new('RGB', (item['w'], item['h']), (50, 70, 50))
                        draw = ImageDraw.Draw(img)
                        try:
                            f_kr = ImageFont.truetype("NanumGothicBold.ttf", sk)
                            f_en = ImageFont.truetype("NanumGothicBold.ttf", se)
                        except:
                            f_kr = ImageFont.load_default()
                            f_en = ImageFont.load_default()

                        y_base = item['h'] * (v/100)
                        # 한글(위) / 영어(아래) 물리적 좌표 분리 출력
                        draw.text((item['w']/2, y_base - (sk/1.5)), t_kr, font=f_kr, fill=(255,255,255), anchor="mm")
                        draw.text((item['w']/2, y_base + (se/1.2) + (sk/4)), t_en, font=f_en, fill=(210,210,210), anchor="mm")
                        
                        st.image(img, use_column_width=True)
        else:
            st.info("👈 설정을 마친 후 생성을 시작하세요.")
