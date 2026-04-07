import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 상수 데이터 보호
STYLE_LIST = ["사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"]
LIGHT_LIST = ["자연광", "안개", "네온", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르", "촛불", "석양", "명암", "레이저", "보케", "고대비"]
CAM_LIST = ["광각", "매크로", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안", "드론", "파노라마", "필름", "망원", "틸트-시프트"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def draw_text_overlay(width, height, kr_text, en_text, v_pos, kr_size, en_size):
    img = Image.new('RGB', (width, height), (60, 90, 60))
    draw = ImageDraw.Draw(img)
    s_kr = int((height / 10) * (kr_size / 50))
    s_en = int((height / 15) * (en_size / 50))
    y = int(height * (v_pos / 100))
    try: f_k = ImageFont.truetype("NanumGothicBold.ttf", s_kr)
    except: f_k = ImageFont.load_default()
    draw.text((width/2, y - s_kr/2), kr_text, font=f_k, fill=(255,255,255), anchor="mm")
    draw.text((width/2, y + s_en), en_text, fill=(210,210,210), anchor="mm")
    return img

def render_tab2():
    st.markdown("<style>.stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { margin-bottom: 0px !important; }</style>", unsafe_allow_html=True)
    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        # [복구] 파일 업로드 및 세션 기반 파싱 로직
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        if aud_file:
            base = os.path.splitext(aud_file.name)[0]
            parts = base.split('_')
            st.session_state['tmp_kr'] = parts[0]
            st.session_state['tmp_en'] = parts[1] if len(parts) > 1 else ""

        # [확실함] 세션 상태를 value로 바인딩하여 파싱 결과 표시
        t_kr = st.text_input("📌 한글 제목", value=st.session_state.get('tmp_kr', ""), key="in_kr")
        t_en = st.text_input("📌 영문 제목", value=st.session_state.get('tmp_en', ""), key="in_en")
        
        # [복구] 가사 입력칸 (이전 가사 데이터 연동)
        lyrics_default = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 무드 분석 (편집 가능)", value=lyrics_default, key="in_lyrics")

        st.divider()
        num_shorts = st.slider("✂️ 쇼츠 추가", 0, 5, 2)
        st.selectbox("🎨 예술 스타일", STYLE_LIST, key="s_st")
        st.selectbox("💡 조명 효과", LIGHT_LIST, key="s_li")
        st.selectbox("📷 카메라 앵글", CAM_LIST, key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_gen = True
            st.session_state.img_list = [{"label": "메인", "w": 1280, "h": 720}, {"label": "틱톡", "w": 720, "h": 1280}] + [{"label": f"쇼츠{i}", "w": 720, "h": 1280} for i in range(num_shorts)]

    with r_col:
        if st.session_state.get('is_gen'):
            for idx, item in enumerate(st.session_state.img_list):
                with st.container(border=True):
                    c_img, c_ctrl = st.columns([1.2, 1])
                    with c_ctrl:
                        st.write(f"**{item['label']} 조절**")
                        st.selectbox("한글 폰트", KR_FONTS, key=f"fk_{idx}")
                        st.selectbox("영어 폰트", EN_FONTS, key=f"fe_{idx}")
                        v = st.slider("위치", 0, 100, 50, key=f"v_{idx}")
                        sk = st.slider("한글 크기", 10, 200, 50, key=f"sk_{idx}")
                        se = st.slider("영어 크기", 10, 200, 40, key=f"se_{idx}")
                    with c_img:
                        img = draw_text_overlay(item['w'], item['h'], t_kr, t_en, v, sk, se)
                        st.image(img, use_column_width=True)
        else: st.info("👈 설정 후 생성을 시작하세요.")
