import streamlit as st
import os
import google.generativeai as genai

# [확실함] API 키 로컬 로드 함수
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 간격을 극단적으로 줄이되 겹치지 않게 하는 초정밀 CSS
    st.markdown("""
        <style>
        /* 위젯 간 수직 간격을 최소로 축소 */
        [data-testid="stVerticalBlock"] > div { margin-top: -15px !important; margin-bottom: 0px !important; }
        
        /* 드롭다운 및 입력창 높이 30px로 축소 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 30px !important; height: 30px !important; font-size: 13px !important;
            padding: 0px 8px !important;
        }
        
        /* 텍스트 에어리어(가사창)만 높이 예외 허용 */
        .stTextArea textarea { height: 150px !important; }
        
        /* 라벨 폰트 크기 및 박스와의 밀착도 조정 */
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-size: 11px !important; font-weight: 600 !important;
            margin-bottom: -12px !important; color: #555 !important; padding-top: 8px !important;
        }
        
        /* 라디오 버튼 간격 축소 */
        div[role="radiogroup"] { gap: 10px !important; margin-top: -5px !important; }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()

        # 1. 음원 업로드
        aud_file = st.file_uploader("🎧 음원 업로드 (파일명 파싱용)", type=['mp3', 'wav'])
        
        # 파일명 파싱 로직
        t_kr, t_en = "", ""
        if aud_file:
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr = parts[0]
            t_en = parts[1] if len(parts) > 1 else ""

        # [확실함] 한글/영어 제목 한 줄 배치
        col_t1, col_t2 = st.columns(2)
        with col_t1: title_kr = st.text_input("📌 한글 제목", value=t_kr)
        with col_t2: title_en = st.text_input("📌 영문 제목", value=t_en)

        # [확실함] 가사 수동 입력 모드 (사용자가 넣을 수 있도록 disabled 제거)
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 기반 가사 컨텍스트 (수정 가능)", value=lyrics_val, height=150)

        # [확실함] 15종 이상의 전문 옵션 메뉴
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지 일러스트", "미니멀리즘", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        lightings = ["부드러운 자연광", "볼류메트릭 안개", "네온 글로우", "시네마틱", "골든 아워", "차가운 달빛", "스튜디오 조명", "역광", "에테르 빛", "촛불", "석양", "드라마틱 명암", "레이저", "보케", "고대비"]
        s_light = st.selectbox("💡 조명 효과", lightings)

        cameras = ["광각 렌즈", "매크로 접사", "아이 레벨", "조감도", "웜즈 아이", "클로즈업", "아웃포커싱", "딥 포커스", "어안 렌즈", "핸드헬드", "드론 POV", "파노라마", "필름 카메라", "망원 렌즈", "틸트-시프트"]
        s_cam = st.selectbox("📷 카메라 앵글", cameras)

        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key: st.error("가사 탭에서 API 키를 저장하세요."); return
            if not context_lyrics: st.error("분석할 가사가 없습니다."); return
            
            with st.spinner("가사 무드를 시각적 프롬프트로 변환 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # 프롬프트 구성 (제목과 가사를 모두 반영)
                    prompt = f"""
                    Role: Music Visual Director. Task: Generate 1000-char English image prompt for an album cover.
                    Context: Title[{title_kr}({title_en})], Lyrics[{context_lyrics[:800]}]
                    Visuals: Style[{s_style}], Lighting[{s_light}], Camera[{s_cam}], Ratio[{s_ratio}]
                    Requirement: Describe the scene deeply in English. NO bolding (**). Output ONLY the prompt.
                    """
                    
                    response = model.generate_content(prompt)
                    # [확실함] ** 제거 후처리
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")
                except Exception as e:
                    st.error(f"생성 실패: {str(e)}")

        if 'gen_img_prompt' in st.session_state:
            with st.container(border=True):
                st.write("**🎨 AI 이미지 생성용 영문 프롬프트 (Midjourney / DALL-E 3)**")
                # 가독성과 복사 편의성을 위해 st.code 사용
                st.code(st.session_state.gen_img_prompt, language="markdown")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
