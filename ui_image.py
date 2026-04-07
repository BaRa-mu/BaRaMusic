import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 폰트 및 스타일 데이터 보호
STYLE_LIST = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"]
LIGHT_LIST = ["자연광", "안개", "네온", "시네마틱", "골든 아워", "달빛", "스튜디오", "역광", "에테르", "촛불", "석양", "명암", "레이저", "보케", "고대비"]
CAM_LIST = ["광각", "매크로", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안", "드론", "파노라마", "필름", "망원", "틸트-시프트"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def render_tab2():
    # [수정] 간격 초밀착 CSS (겹치지 않는 한계선)
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
        # 1. 업로드 및 파싱 (상태 주입)
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
        st.selectbox("🎨 스타일", STYLE_LIST, key="s_st")
        st.selectbox("💡 조명", LIGHT_LIST, key="s_li")
        st.selectbox("📷 앵글", CAM_LIST, key="s_ca")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            st.session_state.imgs_data = [{"label": "메인 (16:9)", "w": 1280, "h": 720}] + \
                                         [{"label": "틱톡 (9:16)", "w": 720, "h": 1280}] + \
                                         [{"label": f"쇼츠 {i+1}", "w": 720, "h": 1280} for i in range(num_s)]

    with r_col:
        if st.session_state.get('is_generated'):
            all_imgs = st.session_state.get('imgs_data', [])
            
            # 1. 메인 이미지 (상단에 크게 배치)
            main_item = all_imgs[0]
            with st.container(border=True):
                c_i, c_c = st.columns([1.5, 1])
                with c_c:
                    st.write(f"**{main_item['label']}**")
                    v_m = st.slider("위치", 0, 100, 50, key="v_0")
                    sk_m = st.slider("한글 크기", 10, 200, 60, key="sk_0")
                    se_m = st.slider("영어 크기", 10, 200, 40, key="se_0")
                    st.selectbox("한글 폰트", KR_FONTS, key="fk_0")
                    st.selectbox("영어 폰트", EN_FONTS, key="fe_0")
                with c_i:
                    img = Image.new('RGB', (main_item['w'], main_item['h']), (50, 70, 50))
                    draw = ImageDraw.Draw(img)
                    y = main_item['h'] * (v_m/100)
                    draw.text((main_item['w']/2, y - sk_m/2), t_kr, fill=(255,255,255), anchor="mm")
                    draw.text((main_item['w']/2, y + se_m), t_en, fill=(210,210,210), anchor="mm")
                    st.image(img, use_column_width=True)

            st.write("**📱 세로 규격 (9:16) - 3열 콤팩트 배치**")
            # 2. 세로 이미지 (3열 배치를 통해 사이즈를 메인처럼 작게 줄임)
            v_items = all_imgs[1:]
            v_cols = st.columns(3) # [Certain] 3열 그리드로 사이즈 대폭 축소
            for idx, item in enumerate(v_items):
                real_idx = idx + 1
                with v_cols[idx % 3]:
                    with st.container(border=True):
                        # 실시간 조절 바
                        v = st.slider(f"위치", 0, 100, 50, key=f"v_{real_idx}", label_visibility="collapsed")
                        sk = st.slider(f"한글", 10, 200, 45, key=f"sk_{real_idx}", label_visibility="collapsed")
                        se = st.slider(f"영어", 10, 200, 30, key=f"se_{real_idx}", label_visibility="collapsed")
                        
                        # 렌더링
                        img_v = Image.new('RGB', (item['w'], item['h']), (60, 50, 70))
                        draw_v = ImageDraw.Draw(img_v)
                        y_v = item['h'] * (v/100)
                        draw_v.text((item['w']/2, y_v - sk/2), t_kr, fill=(255,255,255), anchor="mm")
                        draw_v.text((item['w']/2, y_v + se), t_en, fill=(200,200,200), anchor="mm")
                        
                        st.image(img_v, use_column_width=True)
                        st.write(f"<p style='font-size:10px; text-align:center;'>{item['label']}</p>", unsafe_allow_html=True)
                        # 드롭다운 메뉴 (공간 절약을 위해 아래 배치)
                        st.selectbox("KR", KR_FONTS, key=f"fk_{real_idx}", label_visibility="collapsed")
                        st.selectbox("EN", EN_FONTS, key=f"fe_{real_idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 생성을 시작하세요.")
