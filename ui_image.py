import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 15종 이상의 데이터 (유실 방지)
KR_FONTS_LIST = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS_LIST = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

# [확실함] 한글 깨짐 방지용 시스템 폰트 로드 함수
def get_korean_font(size):
    # 시스템별 예상 한글 폰트 경로 (리눅스, 윈도우, 맥 순서)
    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",  # Streamlit Cloud/Linux
        "C:/Windows/Fonts/malgun.ttf",                         # Windows
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",   # Mac
        "NanumGothicBold.ttf"                                  # 로컬 폴더 직접 포함 시
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default() # 최후의 수단 (이 경우 한글 깨짐)

def draw_text_overlay(width, height, kr_text, en_text, v_pos, kr_size, en_size):
    # 배경 생성
    img = Image.new('RGB', (width, height), (55, 65, 55))
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드 (한글 깨짐 차단)
    f_kr = get_korean_font(int(kr_size * (height/500)))
    f_en = get_korean_font(int(en_size * (height/500)))

    y_base = height * (v_pos / 100)
    
    # [확실함] 한글 [줄바꿈] 영어 가로 중앙 정렬 출력
    # 한글(위)
    draw.text((width/2, y_base - kr_size), kr_text, font=f_kr, fill=(255,255,255), anchor="mm")
    # 영어(아래)
    draw.text((width/2, y_base + en_size), en_text, font=f_en, fill=(210,210,210), anchor="mm")
    return img

def render_tab2():
    # [수정] 간격 최소화 및 겹침 방지 CSS
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -12px !important; margin-bottom: 0px !important; }
        .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { 
            margin-bottom: 0px !important; padding-top: 3px !important; font-size: 11px !important; font-weight: 600 !important;
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            height: 28px !important; min-height: 28px !important; font-size: 13px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        # 1. 파일 업로드 및 파싱 (세션 직접 주입)
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
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
        st.selectbox("🎨 스타일", ["사진", "시네마틱", "유화", "판타지", "사이버펑크"], key="s_st")
        st.selectbox("💡 조명", ["자연광", "네온", "시네마틱", "골든아워"], key="s_li")
        st.selectbox("📷 앵글", ["광각", "클로즈업", "조감도"], key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs_data = [{"label": "메인 (16:9)", "w": 1280, "h": 720}] + \
                                         [{"label": "틱톡 (9:16)", "w": 720, "h": 1280}] + \
                                         [{"label": f"쇼츠 {i+1}", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            all_imgs = st.session_state.get('imgs_data', [])
            
            # 1. 메인 이미지 조절
            main_item = all_imgs[0]
            with st.container(border=True):
                c_i, c_c = st.columns([1.5, 1])
                with c_c:
                    st.write(f"**{main_item['label']}**")
                    v_m = st.slider("위치", 0, 100, 50, key="v_0")
                    sk_m = st.slider("한글 크기", 10, 200, 60, key="sk_0")
                    se_m = st.slider("영어 크기", 10, 200, 40, key="se_0")
                    st.selectbox("KR 폰트", KR_FONTS_LIST, key="fk_0")
                    st.selectbox("EN 폰트", EN_FONTS_LIST, key="fe_0")
                with c_i:
                    img_main = draw_text_overlay(main_item['w'], main_item['h'], t_kr, t_en, v_m, sk_m, se_m)
                    st.image(img_main, use_column_width=True)

            # [확실함] 2. 세로 규격 콤팩트 배치 (3열 그리드 적용)
            st.write("**📱 세로 규격 (9:16) - 3열 콤팩트**")
            v_items = all_imgs[1:]
            v_cols = st.columns(3) # 3열로 나누어 사이즈를 메인처럼 작게 줄임
            for idx, item in enumerate(v_items):
                r_idx = idx + 1
                with v_cols[idx % 3]:
                    with st.container(border=True):
                        # 실시간 조절 바 (라벨 숨김으로 공간 절약)
                        v = st.slider("V", 0, 100, 50, key=f"v_{r_idx}", label_visibility="collapsed")
                        sk = st.slider("KR", 10, 200, 45, key=f"sk_{r_idx}", label_visibility="collapsed")
                        se = st.slider("EN", 10, 200, 30, key=f"se_{r_idx}", label_visibility="collapsed")
                        
                        img_v = draw_text_overlay(item['w'], item['h'], t_kr, t_en, v, sk, se)
                        st.image(img_v, use_column_width=True)
                        st.write(f"<p style='font-size:10px; text-align:center;'>{item['label']}</p>", unsafe_allow_html=True)
                        
                        st.selectbox("F_K", KR_FONTS_LIST, key=f"fk_{r_idx}", label_visibility="collapsed")
                        st.selectbox("F_E", EN_FONTS_LIST, key=f"fe_{r_idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 생성을 시작하세요.")
