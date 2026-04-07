import streamlit as st
import os
import time
import random
import google.generativeai as genai

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # --- 🛠️ [직접 조절 구역] 수치를 변경하며 디자인을 완성하세요 ---
    st.markdown("""
        <style>
        /* [1] 위젯 전체 수직 간격 조절 (좁히려면 마이너스값 확대) */
        [data-testid="stVerticalBlock"] > div { 
            margin-top: -10px !important;    /* 조절: 위쪽 간격 (예: -15px은 더 좁게, 0px은 넓게) */
            margin-bottom: 0px !important;   /* 조절: 아래쪽 간격 */
        }
        
        /* [2] 드롭다운(Select) 및 입력창(Input) 높이 조절 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 25px !important;     /* 조절: 최소 높이 */
            height: 25px !important;         /* 조절: 드롭메뉴/입력창 높이 */
            font-size: 13px !important;      /* 조절: 박스 안 글자 크기 */
            padding: 0px 10px !important;    /* 조절: 박스 안 좌우 여백 */
        }
        
        /* [3] 가사 입력창 전용 높이 (가사는 길어야 하므로 별도 설정) */
        .stTextArea textarea { 
            height: 120px !important;        /* 조절: 가사 입력칸 높이 */
        }
        
        /* [4] 제목(라벨) 위치 및 크기 조절 */
        .stSelectbox label, .stTextArea label, .stTextInput label, .stSlider label {
            font-size: 11px !important;      /* 조절: 제목 글자 크기 */
            font-weight: 600 !important;     /* 조절: 제목 굵기 */
            margin-bottom: -10px !important; /* 조절: 제목을 박스에 얼마나 붙일지 (낮을수록 밀착) */
            padding-top: 6px !important;     /* 조절: 제목 위쪽 여백 */
            color: #444 !important;
        }

        /* [5] 라디오 버튼 사이의 가로 간격 */
        div[role="radiogroup"] { 
            gap: 15px !important;            /* 조절: 버튼 사이 거리 */
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 생성 (무료 테스트)")
        api_key = get_api_key()

        # 1. 음원 업로드 및 파일명 파싱
        aud_file = st.file_uploader("🎧 음원 업로드", type=['mp3', 'wav'])
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr = parts[0]
            t_en = parts[1] if len(parts) > 1 else ""

        # [확실함] 한글/영어 제목 한 줄(Row) 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # [확실함] 가사 수동 입력 (편집 가능)
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 분석용 가사 입력", value=lyrics_val)

        # 수량 설정
        st.write("**📱 플랫폼별 수량**")
        st.info("📺 메인(16:9): 1개 / 📱 틱톡(9:16): 1개 고정")
        num_shorts = st.slider("✂️ 쇼츠용 이미지 개수 (9:16)", 0, 5, 2)

        # 다채로운 드롭다운 메뉴 (15종 이상)
        s_style = st.selectbox("🎨 예술 스타일", ["사진", "시네마틱", "유화", "수채화", "판타지", "미니멀", "빈티지", "사이버펑크", "초현실", "팝아트", "잉크", "스팀펑크", "픽셀", "고딕", "우키요에"])
        s_light = st.selectbox("💡 조명 효과", ["자연광", "안개", "네온", "시네마틱", "골든아워", "달빛", "스튜디오", "역광", "에테르", "촛불", "석양", "명암", "레이저", "보케", "고대비"])
        s_cam = st.selectbox("📷 카메라 앵글", ["광각", "매크로", "아이레벨", "조감도", "웜즈아이", "클로즈업", "아웃포커싱", "딥포커스", "어안", "핸드헬드", "드론", "파노라마", "필름", "망원", "틸트시프트"])

        st.divider()
        gen_btn = st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not context_lyrics: st.error("가사를 입력해주세요."); return
            with st.spinner("이미지 생성 중..."):
                time.sleep(1) # 시뮬레이션
                
                # [확실함] 10% 확률로 실패 시 회색 Fallback
                is_failed = random.random() < 0.1
                st.session_state.img_results = []
                
                # 메인 + 틱톡 + 쇼츠 데이터 구성
                specs = [("메인 (16:9)", "1280x720"), ("틱톡 (9:16)", "720x1280")]
                for i in range(num_shorts): specs.append((f"쇼츠 {i+1} (9:16)", "720x1280"))
                
                for label, size in specs:
                    color = "808080" if is_failed else f"{random.randint(10,99)}a{random.randint(10,99)}b"
                    text = "Failed" if is_failed else label.replace(" ", "+")
                    url = f"https://placehold.co/{size}/{color}/fff.png?text={text}"
                    st.session_state.img_results.append({"label": label, "url": url, "size": size})
                
                if is_failed: st.warning("일부 생성에 실패하여 회색으로 표시됩니다.")

        # 결과 출력 구역
        if st.session_state.get('img_results'):
            res = st.session_state.img_results
            # 1. 메인 (가로)
            with st.container(border=True):
                st.write(f"**{res[0]['label']}**")
                st.image(res[0]['url'], caption=res[0]['size'])
            
            # 2. 세로 이미지들 그리드 배치 (3열)
            st.write("**📱 세로형 규격 (9:16)**")
            v_res = res[1:]
            cols = st.columns(3)
            for i, img in enumerate(v_res):
                with cols[i % 3].container(border=True):
                    st.write(f"**{img['label']}**")
                    st.image(img['url'], use_column_width=True)
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
