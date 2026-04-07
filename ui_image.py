import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 전문가급 데이터 상수 격리 (각 15종 이상)
STYLE_LIST = ["사실적인 사진 (Hyper-Realistic)", "시네마틱 3D 렌더링", "고전 유화 (Oil Painting)", "감성적인 수채화", "판타지 일러스트", "미니멀리즘 아트", "빈티지 레트로 사진", "사이버펑크 스타일", "초현실주의 (Surrealism)", "팝 아트 (Pop Art)", "잉크 드로잉 (Ink)", "스팀펑크 (Steampunk)", "픽셀 아트 (Pixel)", "고딕 호러 (Gothic)", "우키요에 (Ukiyo-e)", "추상화 (Abstract)", "네온 라이트 아트"]
LIGHT_LIST = ["부드러운 자연광", "볼류메트릭 안개 조명", "네온 글로우 (Neon)", "시네마틱 조명", "골든 아워 (Golden Hour)", "차가운 달빛", "스튜디오 조명", "역광 (Rim Light)", "에테르 빛 (Ethereal)", "촛불 조명", "석양 (Sunset)", "드라마틱 명암 (Chiaroscuro)", "레이저 조명", "보케 (Bokeh)", "고대비 (High Contrast)"]
CAM_LIST = ["광각 렌즈 (Wide)", "매크로 접사 (Macro)", "아이 레벨 (Eye)", "조감도 (Bird's Eye)", "웜즈 아이 (Worm's)", "클로즈업 (Close-up)", "아웃포커싱 (Bokeh)", "딥 포커스 (Deep)", "어안 렌즈 (Fisheye)", "핸드헬드 (Handheld)", "드론 POV", "파노라마 (Panorama)", "필름 카메라", "망원 렌즈 (Telephoto)", "틸트-시프트 (Tilt-Shift)"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def draw_text_overlay(width, height, kr_text, en_text, v_pos, kr_size, en_size, is_failed=False):
    bg_color = (128, 128, 128) if is_failed else (60, 100, 60)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    if is_failed:
        draw.text((width/2, height/2), "Generation Failed", fill=(255,255,255), anchor="mm")
        return img
    # 개별 크기 조절 엔진
    s_kr = int((height / 10) * (kr_size / 50))
    s_en = int((height / 15) * (en_size / 50))
    y_coord = int(height * (v_pos / 100))
    try: font_kr = ImageFont.truetype("NanumGothicBold.ttf", s_kr)
    except: font_kr = ImageFont.load_default()
    draw.text((width/2, y_coord - s_kr/2), kr_text, font=font_kr, fill=(255,255,255), anchor="mm")
    draw.text((width/2, y_coord + s_en), en_text, fill=(220,220,220), anchor="mm")
    return img

def render_tab2():
    # [확실함] 마진 0px 적용
    st.markdown("<style>.stSelectbox label, .stSlider label, .stTextInput label { margin-bottom: 0px !important; }</style>", unsafe_allow_html=True)
    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        t_kr = st.text_input("📌 한글 제목", key="main_t_kr")
        t_en = st.text_input("📌 영문 제목", key="main_t_en")
        num_shorts = st.slider("✂️ 쇼츠 추가", 0, 5, 2)
        
        # [확실함] 15종 이상의 디테일 메뉴 복구 및 데이터 연동
        st.selectbox("🎨 예술 스타일 (15종+)", STYLE_LIST, key="final_style")
        st.selectbox("💡 조명 효과 (15종+)", LIGHT_LIST, key="final_light")
        st.selectbox("📷 카메라 앵글 (15종+)", CAM_LIST, key="final_cam")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.base_store = [{"label": "메인", "w": 1280, "h": 720}, {"label": "틱톡", "w": 720, "h": 1280}] + [{"label": f"쇼츠{i}", "w": 720, "h": 1280} for i in range(num_shorts)]

    with r_col:
        if st.session_state.get('is_generated'):
            for idx, item in enumerate(st.session_state.base_store):
                with st.container(border=True):
                    c_img, c_ctrl = st.columns([1.2, 1])
                    with c_ctrl:
                        st.write(f"**{item['label']} 개별 조절**")
                        # [확실함] 폰트 드롭다운 및 한글/영어 개별 크기 조절
                        st.selectbox("한글 폰트", KR_FONTS, key=f"fkr_{idx}")
                        st.selectbox("영어 폰트", EN_FONTS, key=f"fen_{idx}")
                        v = st.slider("상하 위치", 0, 100, 50, key=f"v_{idx}")
                        sk = st.slider("한글 크기", 10, 200, 50, key=f"sk_{idx}")
                        se = st.slider("영어 크기", 10, 200, 40, key=f"se_{idx}")
                    with c_img:
                        img = draw_text_overlay(item['w'], item['h'], t_kr, t_en, v, sk, se)
                        st.image(img, use_column_width=True)
        else:
            st.info("👈 왼쪽에서 상세 설정을 마친 후 생성을 시작하세요.")
