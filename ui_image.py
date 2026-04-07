import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# --- [확실함] 1. 절대 유실 금지 데이터 (각 15종 이상 고정) --- [Certain]
STYLE_LIST = ["사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크", "스팀펑크", "픽셀 아트", "고딕", "우키요에", "추상화", "네온 아트"]
LIGHT_LIST = ["자연광", "안개 조명", "네온 글로우", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르 빛", "촛불", "석양", "명암", "레이저", "보케", "고대비", "네온 라이트"]
CAM_LIST = ["광각", "매크로", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안 렌즈", "POV", "파노라마", "필름", "망원", "틸트-시프트", "핸드헬드"]
KR_FONTS_LIST = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS_LIST = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def render_tab2():
    # [수정] 겹치지 않는 범위 내 최소 간격 (안전 수치 -10px) [확실함]
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 0px !important; }
        .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { 
            margin-bottom: -5px !important; padding-top: 5px !important; font-size: 11px !important; font-weight: 600 !important;
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            height: 30px !important; min-height: 30px !important; font-size: 13px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        # 1. 업로드 및 파싱
        aud_file = st.file_uploader("🎧 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        if aud_file:
            base = os.path.splitext(aud_file.name)[0]
            if "_" in base:
                parts = base.split('_')
                st.session_state.in_kr, st.session_state.in_en = parts[0], parts[1] if len(parts) > 1 else ""

        t_kr = st.text_input("📌 한글 제목", key="in_kr")
        t_en = st.text_input("📌 영문 제목", key="in_en")
        st.text_area("📝 가사 무드", value=st.session_state.get('gen_lyrics', ""), height=80, key="in_l")

        st.divider()
        num_s = st.slider("✂️ 쇼츠 추가", 0, 5, 2, key="n_s")
        # [기능 유지] 15종 전문 메뉴 [Certain]
        st.selectbox("🎨 스타일", STYLE_LIST, key="s_st")
        st.selectbox("💡 조명", LIGHT_LIST, key="s_li")
        st.selectbox("📷 카메라", CAM_LIST, key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs_data = [{"label": "메인 (16:9)", "w": 1280, "h": 720}] + \
                                         [{"label": "틱톡 (9:16)", "w": 720, "h": 1280}] + \
                                         [{"label": f"쇼츠 {i+1}", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            all_imgs = st.session_state.get('imgs_data', [])
            
            # 1. 메인 이미지 (상단 배치)
            m_item = all_imgs[0]
            with st.container(border=True):
                c_i, c_c = st.columns([1.5, 1])
                with c_c:
                    st.write(f"**{m_item['label']}**")
                    st.selectbox("한글 폰트", KR_FONTS_LIST, key="fk_0")
                    st.selectbox("영어 폰트", EN_FONTS_LIST, key="fe_0")
                    v_m = st.slider("위치 상하", 0, 100, 50, key="v_0")
                    sk_m = st.slider("한글 크기", 10, 200, 60, key="sk_0")
                    se_m = st.slider("영어 크기", 10, 200, 40, key=f"se_0")
                    # [확실함] 줄 간격 조절 슬라이더 추가 [Certain]
                    ls_m = st.slider("줄 간격", 1, 30, 10, key="ls_0")
                with c_i:
                    # [확실함] 줄 간격 조절 엔진 고도화
                    img = Image.new('RGB', (m_item['w'], m_item['h']), (60, 110, 60))
                    draw = ImageDraw.Draw(img)
                    y = m_item['h'] * (v
