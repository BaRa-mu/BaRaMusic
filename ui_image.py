import streamlit as st
import os
import random
from PIL import Image, ImageDraw, ImageFont

# [확실함] 15종 이상의 전문 데이터 상수 격리
STYLE_LIST = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
KR_FONTS = ["나눔붓", "나눔펜", "상상꽃길", "배민연성", "교보손글씨", "나눔바른펜", "안동엄마", "상상신비", "이순신굵은", "배민한나", "제주한라산", "나눔라운드", "상상금도끼", "안성탕면", "tvN즐거운"]
EN_FONTS = ["Great Vibes", "Dancing Script", "Pacifico", "Allura", "Sacramento", "Arizonia", "Pinyon Script", "Parisienne", "Cookie", "Kaushan Script", "Tangerine", "Clicker Script", "Playball", "Alex Brush", "Monsieur"]

def render_tab2():
    # 0. 레이아웃 및 마진 설정
    st.markdown("<style>.stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label { margin-bottom: 0px !important; }</style>", unsafe_allow_html=True)
    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 상세 설정")
        
        # 1. 파일 업로드 및 [상태 주입] 로직
        aud_file = st.file_uploader("🎧 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            if "_" in base_name:
                parts = base_name.split('_')
                # [확실함] 위젯 렌더링 전에 세션 상태에 직접 주입 (key와 매칭)
                if 'in_kr' not in st.session_state or st.session_state.in_kr == "":
                    st.session_state.in_kr = parts[0]
                if 'in_en' not in st.session_state or st.session_state.in_en == "":
                    st.session_state.in_en = parts[1]
        
        # 2. 위젯 배치 (value를 쓰지 않고 key만 사용하여 세션과 직결)
        t_kr = st.text_input("📌 한글 제목", key="in_kr")
        t_en = st.text_input("📌 영문 제목", key="in_en")
        
        # [복구] 가사 입력창 (가사 탭 데이터 연동 및 유지)
        if 'in_lyrics' not in st.session_state:
            st.session_state.in_lyrics = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 무드 분석", key="in_lyrics", height=100)

        st.divider()
        num_shorts = st.slider("✂️ 쇼츠 추가", 0, 5, 2, key="num_s")
        st.selectbox("🎨 스타일", STYLE_LIST, key="sel_style")
        st.selectbox("💡 조명", ["자연광", "네온", "시네마틱", "골든아워", "스튜디오"], key="sel_light")
        st.selectbox("📷 카메라", ["광각", "클로즈업", "조감도", "매크로", "드론 POV"], key="sel_cam")

        if st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True):
            st.session_state.is_generated = True
            # 이미지 규격 리스트 생성
            st.session_state.img_queue = [{"label": "메인", "w": 1280, "h": 720}, {"label": "틱톡", "w": 720, "h": 1280}] + \
                                         [{"label": f"쇼츠{i+1}", "w": 720, "h": 1280} for i in range(num_shorts)]

    with r_col:
        if st.session_state.get('is_generated'):
            for idx, item in enumerate(st.session_state.img_queue):
                with st.container(border=True):
                    c_img, c_ctrl = st.columns([1.2, 1])
                    with c_ctrl:
                        st.write(f"**{item['label']} 개별 조절**")
                        st.selectbox("한글 폰트", KR_FONTS, key=f"fkr_{idx}")
                        st.selectbox("영어 폰트", EN_FONTS, key=f"fen_{idx}")
                        v_pos = st.slider("위치", 0, 100, 50, key=f"vp_{idx}")
                        sk = st.slider("한글 크기", 10, 200, 50, key=f"sk_{idx}")
                        se = st.slider("영어 크기", 10, 200, 40, key=f"se_{idx}")
                    with c_img:
                        # [확실함] 배경 이미지 생성 시뮬레이션 및 텍스트 렌더링
                        preview_img = Image.new('RGB', (item['w'], item['h']), (50, 70, 50))
                        draw = ImageDraw.Draw(preview_img)
                        # 실제 폰트 적용 로직 생략 (이전 유지)
                        draw.text((item['w']/2, item['h']*(v_pos/100)), f"{t_kr}\n{t_en}", fill=(255,255,255), anchor="mm", align="center")
                        st.image(preview_img, use_column_width=True)
        else:
            st.info("👈 설정을 마친 후 생성을 시작하세요.")
