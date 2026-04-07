import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

# [확실함] 실시간 렌더링 함수 (한글/영어 크기 분리)
def draw_text_overlay(width, height, kr_text, en_text, v_pos, kr_size, en_size, is_failed=False):
    # 배경 생성 (실패 시 회색)
    bg_color = (128, 128, 128) if is_failed else (80, 140, 80)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    if is_failed:
        draw.text((width/2, height/2), "Generation Failed", fill=(255,255,255), anchor="mm")
        return img

    # 높이 비율에 따른 폰트 크기 계산
    actual_kr_size = int((height / 10) * (kr_size / 50))
    actual_en_size = int((height / 15) * (en_size / 50))
    y_coordinate = int(height * (v_pos / 100))
    
    try:
        # 한글 폰트 (NanumGothicBold.ttf 파일이 실행 경로에 있어야 함)
        font_kr = ImageFont.truetype("NanumGothicBold.ttf", actual_kr_size)
        font_en = ImageFont.truetype("NanumGothicBold.ttf", actual_en_size)
    except:
        font_kr = ImageFont.load_default()
        font_en = ImageFont.load_default()

    # 한글 제목 그리기 (위쪽)
    draw.text((width/2, y_coordinate - actual_kr_size/2), kr_text, font=font_kr, fill=(255,255,255), anchor="mm")
    # 영어 제목 그리기 (아래쪽)
    draw.text((width/2, y_coordinate + actual_en_size), en_text, font=font_en, fill=(220,220,220), anchor="mm")
    
    return img

def render_tab2():
    # --- 🛠️ CSS: 마진 0px 및 간격 최적화 ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 2px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
        }
        .stTextArea textarea { height: 100px !important; } 
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: 0px !important; padding-top: 6px !important;
            color: #444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 설정")
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr, t_en = parts[0], parts[1] if len(parts) > 1 else ""

        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        context_lyrics = st.text_area("📝 가사 무드 분석", value=st.session_state.get('gen_lyrics', ""))

        st.divider()
        num_shorts = st.slider("✂️ 쇼츠 이미지 (0~5개)", 0, 5, 2)

        # 왼쪽 메뉴의 드롭다운
        s_style = st.selectbox("🎨 예술 스타일", ["사진", "시네마틱", "유화", "수채화", "판타지", "미니멀", "빈티지"])
        s_light = st.selectbox("💡 조명 효과", ["자연광", "네온", "시네마틱", "골든아워", "스튜디오"])
        s_cam = st.selectbox("📷 카메라 앵글", ["광각", "매크로", "아이레벨", "조감도", "클로즈업"])

        st.divider()
        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.generated = True

    with r_col:
        st.subheader("✨ 실시간 미리보기 및 개별 조절")
        
        if st.session_state.get('generated'):
            # [확실함] 조절 메뉴의 드롭다운 리스트
            kr_fonts = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨"]
            en_fonts = ["Great Vibes", "Dancing Script", "Pacifico", "Allura"]

            # 1. 메인 이미지 (16:9) 조절
            with st.container(border=True):
                c_img, c_ctrl = st.columns([1.2, 1])
                with c_ctrl:
                    st.write("**메인 개별 조절**")
                    # [확실함] 복구된 드롭다운 메뉴
                    st.selectbox("한글 폰트", kr_fonts, key="f_kr_m")
                    st.selectbox("영어 폰트", en_fonts, key="f_en_m")
                    v_m = st.slider("위치 상하", 0, 100, 50, key="v_m")
                    # [확실함] 한글/영어 크기 분리
                    ks_m = st.slider("한글 크기", 10, 150, 50, key="ks_m")
                    es_m = st.slider("영어 크기", 10, 150, 40, key="es_m")
                with c_img:
                    main_img = draw_text_overlay(1280, 720, title_kr, title_en, v_m, ks_m, es_m)
                    st.image(main_img, caption="유튜브 메인 (16:9)", use_column_width=True)

            # 2. 세로 이미지 (9:16) 조절 (5열 콤팩트)
            st.write("**📱 세로형 규격 (9:16) - 5열 보기**")
            cols = st.columns(5)
            total_v = 1 + num_shorts
            for idx in range(total_v):
                label = "틱톡" if idx == 0 else f"쇼츠 {idx}"
                with cols[idx % 5]:
                    with st.container(border=True):
                        # [확실함] 세로 이미지용 개별 크기/위치 조절
                        v_val = st.slider(f"위치", 0, 100, 50, key=f"v_{idx}", label_visibility="collapsed")
                        ks_val = st.slider(f"한글", 10, 150, 40, key=f"ks_{idx}", label_visibility="collapsed")
                        es_val = st.slider(f"영어", 10, 150, 30, key=f"es_{idx}", label_visibility="collapsed")
                        
                        # 실시간 렌더링
                        v_img = draw_text_overlay(720, 1280, title_kr, title_en, v_val, ks_val, es_val)
                        st.image(v_img, use_column_width=True)
                        st.write(f"<p style='font-size:10px;'>{label}</p>", unsafe_allow_html=True)
                        # 드롭다운 복구
                        st.selectbox("KR", kr_fonts, key=f"f_kr_{idx}", label_visibility="collapsed")
                        st.selectbox("EN", en_fonts, key=f"f_en_{idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 '이미지 생성 시작' 버튼을 눌러주세요.")
