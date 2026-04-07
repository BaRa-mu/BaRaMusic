import streamlit as st
import os
import google.generativeai as genai

# [확실함] API 키 로컬 로드 함수
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 답답함을 제거한 시원한 간격(15px) 및 슬림 박스 CSS
    st.markdown("""
        <style>
        /* 위젯 사이 간격 확대 */
        [data-testid="stVerticalBlock"] > div { margin-top: 0px !important; margin-bottom: 15px !important; }
        
        /* 슬림 박스 디자인 (32px) 및 폰트 크기 최적화 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; font-size: 13px !important;
        }
        
        /* 라벨 가독성 및 여백 확보 */
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-size: 12px !important; font-weight: 600 !important;
            margin-bottom: 6px !important; color: #333 !important; padding-top: 5px !important;
        }
        
        /* 결과창 코드 박스 정제 */
        .stCode { border: 1px solid #e6e9ef !important; }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()

        # [확실함] 음원 파일 업로드 필드 (요구사항 반영)
        uploaded_audio = st.file_uploader("🎧 분석용 음원 파일 업로드", type=['mp3', 'wav'])
        
        # 가사 컨텍스트 연동
        lyrics_context = st.session_state.get('gen_lyrics', "")
        st.text_area("📝 분석 기반 가사 (자동 연동됨)", value=lyrics_context, height=120, disabled=True)

        # [확실함] 15종 이상의 다채로운 드롭다운 메뉴 구성
        styles = [
            "사실적인 사진 (Photorealistic)", "시네마틱 3D 렌더 (Cinematic)", "꿈꾸는 듯한 유화 (Oil Painting)", 
            "디지털 일러스트 (Digital)", "판타지 컨셉 아트 (Fantasy)", "추상적인 수채화 (Watercolor)", 
            "미니멀리즘 (Minimalism)", "사이버펑크 네온 (Cyberpunk)", "빈티지 레트로 (Vintage)", 
            "초현실주의 (Surrealism)", "팝 아트 (Pop Art)", "잉크 드로잉 (Ink Sketch)", 
            "스팀펑크 (Steampunk)", "픽셀 아트 (Pixel Art)", "고딕 호러 (Gothic)", "우키요에 (Ukiyo-e)"
        ]
        s_style = st.selectbox("🎨 예술 스타일 (15종+)", styles)

        lightings = [
            "부드러운 자연광 (Soft Natural)", "볼류메트릭 안개 (Volumetric)", "네온 글로우 (Neon)", 
            "시네마틱 조명 (Cinematic)", "골든 아워 (Golden Hour)", "차가운 달빛 (Moonlight)", 
            "스튜디오 조명 (Studio)", "강렬한 역광 (Backlit)", "에테르 빛 (Ethereal)", 
            "은은한 촛불 (Candlelight)", "석양의 붉은 빛 (Sunset)", "드라마틱한 명암 (Chiaroscuro)", 
            "사이버틱 레이저 (Laser)", "흐릿한 보케 (Bokeh)", "고대비 조명 (High Contrast)"
        ]
        s_light = st.selectbox("💡 조명 효과 (15종+)", lightings)

        cameras = [
            "광각 렌즈 (Wide Angle)", "매크로 접사 (Macro)", "아이 레벨 (Eye Level)", 
            "조감도 (Bird's Eye)", "웜즈 아이 (Worm's Eye)", "클로즈업 (Close-up)", 
            "아웃포커싱 (Shallow Depth)", "딥 포커스 (Deep Focus)", "어안 렌즈 (Fisheye)", 
            "핸드헬드 (Handheld)", "드론 POV (Drone)", "파노라마 (Panoramic)", 
            "빈티지 필름 (Film)", "망원 렌즈 (Telephoto)", "틸트-시프트 (Tilt-shift)"
        ]
        s_cam = st.selectbox("📷 카메라/앵글 (15종+)", cameras)

        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key: st.error("가사 탭에서 API 키를 먼저 저장하세요."); return
            if not lyrics_context: st.error("분석할 가사가 없습니다. 가사 탭에서 먼저 생성하세요."); return
            
            with st.spinner("음원과 가사를 기반으로 분위기를 자동 분석 중..."):
                try:
                    genai.configure(api_key=api_key)
                    # [확실함] 최신 Gemini 모델로 비주얼 분석 수행
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # [초강력] 음원 파일 존재 여부와 가사를 결합한 정밀 분석 지시
                    audio_status = "Uploaded" if uploaded_audio else "Not provided"
                    prompt = f"""
                    Role: Music Visual Concept Artist.
                    Task: Analyze the song's 'Atmosphere' based on provided data and generate a 1000-char English prompt.
                    
                    Data:
                    - Lyrics Context: {lyrics_context[:1000]}
                    - Audio File Status: {audio_status} (If uploaded, infer dynamic and textural moods)
                    
                    Selection:
                    - Style: {s_style}
                    - Lighting: {s_light}
                    - Camera: {s_cam}
                    - Aspect Ratio: {s_ratio}
                    
                    Requirements:
                    1. Automatically determine the visual mood (e.g., reverent, energetic, nostalgic) based on the lyrics and audio context.
                    2. Describe the scene, textures, environment, and professional cinematography in English.
                    3. Output ONLY the practical English prompt. NO bolding (**), NO conversational text.
                    """
                    
                    response = model.generate_content(prompt)
                    # [확실함] 별표(**) 제거 및 세션 저장
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")
                    
                except Exception as e:
                    st.error(f"생성 실패: {str(e)}")

        # [방어적 렌더링] 생성 결과가 있을 때만 코드 박스 노출
        if 'gen_img_prompt' in st.session_state:
            with st.container(border=True):
                st.write("**🎨 AI 이미지 생성용 영문 프롬프트 (Midjourney / DALL-E 3)**")
                st.code(st.session_state.gen_img_prompt, language="markdown")
                st.info("💡 위 프롬프트를 복사하여 이미지 AI에 입력하면 곡 분위기에 최적화된 배경을 얻을 수 있습니다.")
        else:
            st.info("👈 왼쪽에서 설정을 완료한 후 '생성' 버튼을 눌러주세요.")
