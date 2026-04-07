import streamlit as st
import os
import google.generativeai as genai

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 가장 좁았던 상태(-15px)에서 미세하게(+3px)만 넓힌 초정밀 CSS
    st.markdown("""
        <style>
        /* 수직 간격을 극도로 압축 (-10px) */
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 2px !important; }
        
        /* 모든 입력창 높이를 32px 슬림하게 고정 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; height: 32px !important; font-size: 13px !important;
            padding: 0px 10px !important;
        }
        
        /* 가사창 높이만 예외적으로 확보 */
        .stTextArea textarea { height: 130px !important; }
        
        /* 라벨을 박스에 바짝 붙임 */
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: -10px !important; color: #444 !important; padding-top: 6px !important;
        }
        
        /* 라디오 버튼 밀도 상향 */
        div[role="radiogroup"] { gap: 12px !important; margin-top: -4px !important; }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 이미지 설정")
        api_key = get_api_key()

        # 1. 음원 업로드
        aud_file = st.file_uploader("🎧 음원 업로드 (파일명 파싱)", type=['mp3', 'wav'])
        
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr = parts[0]
            t_en = parts[1] if len(parts) > 1 else ""

        # [확실함] 한 줄 배치 유지
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # [확실함] 가사 수동 입력 (기존 데이터 연동)
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 가사 입력/수정", value=lyrics_val)

        # 15종 옵션 드롭다운 (간격 압축 적용됨)
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지 일러스트", "미니멀리즘", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        lightings = ["부드러운 자연광", "볼류메트릭 안개", "네온 글로우", "시네마틱", "골든 아워", "차가운 달빛", "스튜디오 조명", "역광", "에테르 빛", "촛불", "석양", "드라마틱 명암", "레이저", "보케", "고대비"]
        s_light = st.selectbox("💡 조명 효과", lightings)

        cameras = ["광각 렌즈", "매크로 접사", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안 렌즈", "핸드헬드", "드론 POV", "파노라마", "필름 카메라", "망원 렌즈", "틸트-시프트"]
        s_cam = st.selectbox("📷 카메라 앵글", cameras)

        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])

        st.divider()
        gen_btn = st.button("🚀 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not api_key: st.error("가사 탭에서 키를 저장하세요."); return
            if not context_lyrics: st.error("가사를 입력하세요."); return
            with st.spinner("분석 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    prompt = f"Music Visual Director. Title:{title_kr}_{title_en}. Lyrics:{context_lyrics[:800]}. Style:{s_style}, Lighting:{s_light}, Camera:{s_cam}, Ratio:{s_ratio}. 1000-char English prompt. No bold(**)."
                    res = model.generate_content(prompt).text.replace("**", "")
                    st.session_state.gen_img_prompt = res
                except Exception as e: st.error(f"실패: {str(e)}")

        if st.session_state.get('gen_img_prompt'):
            with st.container(border=True):
                st.write("**🎨 AI 이미지 생성용 프롬프트**")
                st.code(st.session_state.get('gen_img_prompt'), language="markdown")
        else:
            st.info("👈 설정을 마친 후 생성 버튼을 눌러주세요.")
