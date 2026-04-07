import st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# --- 1. 절대 유실 금지 데이터 (각 15종 이상) [Certain] ---
STYLE_LIST = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크", "스팀펑크", "픽셀 아트", "고딕", "우키요에", "추상화", "네온 아트"]
LIGHT_LIST = ["자연광", "안개 조명", "네온 글로우", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르 빛", "촛불", "석양", "명암", "레이저", "보케", "고대비", "네온 라이트"]
CAM_LIST = ["광각 렌즈", "매크로 접사", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안 렌즈", "드론 POV", "파노라마", "필름 카메라", "망원 렌즈", "틸트-시프트", "핸드헬드"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def get_font(size):
    paths = ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", "C:/Windows/Fonts/malgun.ttf", "/System/Library/Fonts/Supplemental/AppleGothic.ttf", "NanumGothicBold.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_overlay(width, height, kr_text, en_text, v_pos, kr_s, en_s, ls):
    img = Image.new('RGB', (width, height), (55, 65, 55))
    draw = ImageDraw.Draw(img)
    f_kr, f_en = get_font(kr_s), get_font(en_s)
    y_center = height * (v_pos / 100)
    total_h = kr_s + ls + en_s
    start_y = y_center - (total_h / 2)
    # 한글(위) / 영어(아래) 줄바꿈 구조 유지 [Certain]
    draw.text((width/2, start_y + (kr_s/2)), kr_text, font=f_kr, fill=(255,255,255), anchor="mm")
    draw.text((width/2, start_y + kr_s + ls + (en_s/2)), en_text, font=f_en, fill=(210,210,210), anchor="mm")
    return img

def render_tab2():
    # 간격 최소화 CSS (겹치지 않게 유지)
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
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
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
        st.selectbox("🎨 예술 스타일", STYLE_LIST, key="s_st")
        st.selectbox("💡 조명 효과", LIGHT_LIST, key="s_li")
        st.selectbox("📷 카메라 앵글", CAM_LIST, key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs_data = [{"label": "메인 (16:9)", "w": 1280, "h": 720}, {"label": "틱톡 (9:16)", "w": 720, "h": 1280}] + \
                                         [{"label": f"쇼츠 {i+1}", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            all_imgs = st.session_state.get('imgs_data', [])
            
            # 1. 메인 이미지 (기존 레이아웃 유지: 이미지 왼쪽, 조절바 오른쪽)
            m_item = all_imgs[0]
            with st.container(border=True):
                c_i, c_c = st.columns([1.5, 1])
                with c_c:
                    st.write(f"**{m_item['label']}**")
                    v_0 = st.slider("위치", 0, 100, 50, key="v_0")
                    sk_0 = st.slider("한글 크기", 10, 200, 60, key="sk_0")
                    se_0 = st.slider("영어 크기", 10, 200, 40, key="se_0")
                    ls_0 = st.slider("줄 간격", 0, 100, 20, key="ls_0")
                    st.selectbox("KR 폰트", KR_FONTS, key="fk_0")
                    st.selectbox("EN 폰트", EN_FONTS, key="fe_0")
                with c_i:
                    st.image(draw_overlay(m_item['w'], m_item['h'], t_kr, t_en, v_0, sk_0, se_0, ls_0), use_column_width=True)

            st.write("**📱 세로 규격 (9:16) - 콤팩트 배치**")
            # 2. 세로 이미지 (3열 배치 / 조절바와 메뉴를 하단으로 이동) [Certain]
            v_cols = st.columns(3)
            for idx, item in enumerate(all_imgs[1:]):
                r_idx = idx + 1
                with v_cols[idx % 3]:
                    with st.container(border=True):
                        # [A] 이미지 최상단 배치
                        img_v = draw_overlay(item['w'], item['h'], t_kr, t_en, 
                                             st.session_state.get(f"v_{r_idx}", 50), 
                                             st.session_state.get(f"sk_{r_idx}", 45), 
                                             st.session_state.get(f"se_{r_idx}", 30), 
                                             st.session_state.get(f"ls_{r_idx}", 15))
                        st.image(img_v, use_column_width=True)
                        st.write(f"<p style='font-size:10px; text-align:center;'>{item['label']}</p>", unsafe_allow_html=True)
                        
                        # [A] 조절바와 메뉴를 모두 하단으로 이동
                        v = st.slider("V", 0, 100, 50, key=f"v_{r_idx}", label_visibility="collapsed")
                        sk = st.slider("KR", 10, 200, 45, key=f"sk_{r_idx}", label_visibility="collapsed")
                        se = st.slider("EN", 10, 200, 30, key=f"se_{r_idx}", label_visibility="collapsed")
                        ls = st.slider("L", 0, 100, 15, key=f"ls_{r_idx}", label_visibility="collapsed")
                        st.selectbox("F_K", KR_FONTS, key=f"fk_{r_idx}", label_visibility="collapsed")
                        st.selectbox("F_E", EN_FONTS, key=f"fe_{r_idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 생성을 시작하세요.")
