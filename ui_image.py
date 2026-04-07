import streamlit as st
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont # [확실함] 한글 제목 직접 그리기를 위한 라이브러리

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

# [확실함] 테스트용 이미지 생성 함수 (한글 지원 및 실패 시뮬레이션 포함)
def create_test_image(width, height, text_kr, text_en, is_failed=False):
    # 실패 시 회색 박스 생성
    color = (128, 128, 128) if is_failed else (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    # 폰트 설정 (기본 폰트 사용, 한글 깨짐 방지 위해 시스템 폰트 경로 확인 필요)
    try:
        # 나눔고딕 등 한글 폰트가 설치되어 있어야 함
        font_kr = ImageFont.truetype("NanumGothicBold.ttf", int(height/15))
        font_en = ImageFont.truetype("NanumGothicBold.ttf", int(height/20))
    except:
        font_kr = ImageFont.load_default()
        font_en = ImageFont.load_default()

    if is_failed:
        draw.text((width/2, height/2), "Generation Failed\n(GRAY BOX)", fill=(255,255,255), anchor="mm", align="center")
    else:
        # [확실함] 이미지 위에 한글/영어 제목 줄바꿈하여 출력
        draw.text((width/2, height/2 - 20), text_kr, font=font_kr, fill=(255,255,255), anchor="mm")
        draw.text((width/2, height/2 + 20), text_en, font=font_en, fill=(200,200,200), anchor="mm")
    
    return img

def render_tab2():
    # --- 🛠️ CSS 조절 구역 ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 2px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
        }
        .stTextArea textarea { height: 120px !important; } 
        
        /* 제목(라벨)과 입력박스 사이 간격 0px로 고정 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: 0px !important; /* 마진 0 적용 */
            padding-top: 6px !important;
            color: #444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 설정")
        api_key = get_api_key()

        # 음원 업로드
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr, t_en = parts[0], parts[1] if len(parts) > 1 else ""

        # 제목 한 줄 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        context_lyrics = st.text_area("📝 가사 무드 분석", value=st.session_state.get('gen_lyrics', ""))

        st.divider()
        num_shorts = st.slider("✂️ 쇼츠 이미지 (0~5개)", 0, 5, 2)
        s_style = st.selectbox("🎨 예술 스타일", ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크"])

        st.divider()
        gen_btn = st.button("🚀 이미지 생성 테스트 시작", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 미리보기 및 개별 조절")
        
        if gen_btn:
            with st.spinner("이미지 및 제목 오버레이 생성 중..."):
                time.sleep(1)
                st.session_state.img_objs = []
                
                # 실패 시뮬레이션 (15% 확률)
                is_failed = random.random() < 0.15
                
                # 규격별 이미지 생성
                specs = [("메인 (16:9)", 1280, 720), ("틱톡 (9:16)", 720, 1280)]
                for i in range(num_shorts): specs.append((f"쇼츠 {i+1}", 720, 1280))
                
                for label, w, h in specs:
                    img_obj = create_test_image(w, h, title_kr, title_en, is_failed)
                    st.session_state.img_objs.append({"label": label, "img": img_obj})
                
                if is_failed: st.warning("생성에 실패하여 회색 박스가 표시됩니다.")

        if st.session_state.get('img_objs'):
            res = st.session_state.img_objs
            kr_fonts = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨"]
            en_fonts = ["Great Vibes", "Dancing Script", "Pacifico"]

            # 1. 메인 이미지 (가로 16:9)
            main_data = res[0]
            with st.container(border=True):
                c_img, c_ctrl = st.columns([1, 1])
                with c_img:
                    st.image(main_data['img'], caption=main_data['label'], use_column_width=True)
                with c_ctrl:
                    st.write("**메인 개별 조절**")
                    st.selectbox("한글 폰트", kr_fonts, key="f_kr_m")
                    st.selectbox("영어 폰트", en_fonts, key="f_en_m")
                    st.slider("위치", 0, 100, 50, key="v_m")
                    st.slider("크기", 10, 100, 50, key="s_m")

            st.write("**📱 세로형 규격 (9:16) - 콤팩트 5열 보기**")
            
            # 2. 세로 이미지 (작게 줄인 5열 배치)
            v_items = res[1:]
            cols = st.columns(5)
            for idx, item in enumerate(v_items):
                with cols[idx % 5]:
                    with st.container(border=True):
                        st.image(item['img'], use_column_width=True)
                        st.write(f"<p style='font-size:10px; margin-bottom:2px;'>{item['label']}</p>", unsafe_allow_html=True)
                        st.selectbox("한글", kr_fonts, key=f"f_kr_{idx}", label_visibility="collapsed")
                        st.selectbox("영어", en_fonts, key=f"f_en_{idx}", label_visibility="collapsed")
                        st.slider("위치", 0, 100, 50, key=f"v_{idx}", label_visibility="collapsed")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
