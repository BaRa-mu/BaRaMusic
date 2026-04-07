import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

# [확실함] 실시간으로 제목을 그려주는 함수
def draw_text_overlay(width, height, kr_text, en_text, v_pos, size_factor, is_failed=False):
    # 배경 생성 (실패 시 회색)
    bg_color = (128, 128, 128) if is_failed else (60, 120, 60)
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    if is_failed:
        draw.text((width/2, height/2), "Generation Failed", fill=(255,255,255), anchor="mm")
        return img

    # 슬라이더 값에 따른 폰트 크기 및 위치 계산
    base_size = int(height / 10)
    font_size = int(base_size * (size_factor / 50))
    y_coordinate = int(height * (v_pos / 100))
    
    try:
        # 시스템에 설치된 한글 폰트 경로 (필요시 경로 수정)
        font = ImageFont.truetype("NanumGothicBold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # 제목 그리기 (한글/영어 줄바꿈)
    full_text = f"{kr_text}\n{en_text}"
    draw.multiline_text((width/2, y_coordinate), full_text, font=font, fill=(255,255,255), anchor="mm", align="center", spacing=10)
    
    return img

def render_tab2():
    # --- 🛠️ CSS: 마진 0px 및 슬림 레이아웃 ---
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
        # 음원 업로드 및 파싱
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

        # [확실함] 복구된 드롭다운 메뉴 3종
        s_style = st.selectbox("🎨 예술 스타일", ["사진", "시네마틱", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크"])
        s_light = st.selectbox("💡 조명 효과", ["자연광", "네온", "시네마틱", "골든아워", "스튜디오", "역광"])
        s_cam = st.selectbox("📷 카메라 앵글", ["광각", "매크로", "아이레벨", "조감도", "클로즈업"])

        st.divider()
        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.generated = True # 생성 상태 저장

    with r_col:
        st.subheader("✨ 실시간 미리보기 및 조절")
        
        if st.session_state.get('generated'):
            # 폰트 리스트
            kr_fonts = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨"]
            en_fonts = ["Great Vibes", "Dancing Script", "Pacifico"]

            # 1. 메인 이미지 (16:9) 조절 섹션
            with st.container(border=True):
                c_img, c_ctrl = st.columns([1.2, 1])
                with c_ctrl:
                    st.write("**메인 개별 조절**")
                    st.selectbox("한글 폰트", kr_fonts, key="f_kr_m")
                    v_m = st.slider("위치 상하", 0, 100, 50, key="v_m")
                    s_m = st.slider("크기 조절", 10, 150, 50, key="s_m")
                with c_img:
                    # [확실함] 슬라이더 값(v_m, s_m)을 즉시 반영하여 이미지 생성
                    main_img = draw_text_overlay(1280, 720, title_kr, title_en, v_m, s_m)
                    st.image(main_img, caption="유튜브 메인 (16:9)", use_column_width=True)

            # 2. 세로 이미지 (9:16) 조절 섹션 (5열 콤팩트)
            st.write("**📱 세로형 규격 (9:16) - 5열 보기**")
            cols = st.columns(5)
            
            # 틱톡 + 쇼츠 포함 총 개수만큼 반복
            total_v = 1 + num_shorts
            for idx in range(total_v):
                label = "틱톡" if idx == 0 else f"쇼츠 {idx}"
                with cols[idx % 5]:
                    with st.container(border=True):
                        # 각 이미지별 개별 슬라이더
                        v_val = st.slider(f"위치", 0, 100, 50, key=f"v_{idx}", label_visibility="collapsed")
                        s_val = st.slider(f"크기", 10, 150, 40, key=f"s_{idx}", label_visibility="collapsed")
                        
                        # [확실함] 세로 이미지 실시간 렌더링
                        v_img = draw_text_overlay(720, 1280, title_kr, title_en, v_val, s_val)
                        st.image(v_img, use_column_width=True)
                        st.write(f"<p style='font-size:10px;'>{label}</p>", unsafe_allow_html=True)
        else:
            st.info("👈 설정을 마친 후 '이미지 생성 시작' 버튼을 눌러주세요.")
