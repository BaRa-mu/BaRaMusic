import streamlit as st
import os
import google.generativeai as genai

# [확실함] API 키 로드 함수
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 겹침 방지 및 표준 간격(15px) 확보 CSS
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: 0px !important; margin-bottom: 15px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; font-size: 13px !important;
        }
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-size: 12px !important; font-weight: 600 !important;
            margin-bottom: 6px !important; color: #333 !important; padding-top: 5px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()

        # [확실함] 음원 파일 업로드 및 파일명 파싱 로직
        aud_file = st.file_uploader("🎧 분석용 음원 업로드 (한글_영어.mp3)", type=['mp3', 'wav'])
        
        t_kr, t_en = "", ""
        if aud_file:
            # 파일명에서 확장자 제거 후 '_'로 분리
            base_name = os.path.splitext(aud_file.name)[0]
            parts = base_name.split('_')
            t_kr = parts[0]
            t_en = parts[1] if len(parts) > 1 else ""

        # [확실함] 업로드 아래에 한글/영어 제목 배치 (파일명 기반 자동 입력)
        title_kr = st.text_input("📌 한글 제목", value=t_kr)
        title_en = st.text_input("📌 영문 제목", value=t_en)

        # 가사 데이터 자동 연동
        lyrics_context = st.session_state.get('gen_lyrics', "")
        st.text_area("📝 기반 가사 컨텍스트", value=lyrics_context, height=100, disabled=True)

        # [확실함] 15종 이상의 다채로운 효과 메뉴
        styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지 일러스트", "미니멀리즘", "빈티지", "사이버펑크", "초현실주의", "팝 아트", "잉크 드로잉", "스팀펑크", "픽셀 아트", "고딕", "우키요에"]
        s_style = st.selectbox("🎨 예술 스타일", styles)

        lightings = ["부드러운 자연광", "볼류메트릭 안개", "네온 글로우", "시네마틱", "골든 아워", "차가운 달빛", "스튜디오 조명", "강렬한 역광", "에테르 빛", "은은한 촛불", "석양", "드라마틱 명암", "레이저", "보케", "고대비"]
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
            if not lyrics_context: st.error("분석할 가사가 없습니다."); return
            
            with st.spinner("파일명과 가사를 분석하여 최적의 비주얼을 설계 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # 제목 정보를 포함하여 더 정확한 프롬프트 생성
                    prompt = f"""
                    Role: Music Album Visual Director.
                    Task: Generate a 1000-char English image prompt.
                    
                    Song Context:
                    - Title: {title_kr} ({title_en})
                    - Lyrics: {lyrics_context[:800]}
                    
                    Visual Specs:
                    - Style: {s_style} / Lighting: {s_light} / Camera: {s_cam} / Ratio: {s_ratio}
                    
                    Requirements:
                    1. Create a detailed scene description reflecting the song's theme.
                    2. Describe textures, environment, colors, and artistic composition.
                    3. Output ONLY the English prompt. NO bolding (**), NO introductory text.
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")
                except Exception as e:
                    st.error(f"생성 실패: {str(e)}")

        if 'gen_img_prompt' in st.session_state:
            with st.container(border=True):
                st.write("**1. 🎵 Title**")
                st.code(f"{title_kr}_{title_en}")
            with st.container(border=True):
                st.write("**2. 🎨 AI 이미지 생성용 영문 프롬프트 (Midjourney / DALL-E 3)**")
                st.code(st.session_state.gen_img_prompt, language="markdown")
        else:
            st.info("👈 설정을 마친 후 '생성' 버튼을 눌러주세요.")
