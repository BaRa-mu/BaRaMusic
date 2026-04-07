import streamlit as st
import google.generativeai as genai
import os
import time

# [확실함] Tab 1에서 저장한 API 키를 불러오는 함수
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    return ""

def render_tab2():
    # --- UI 스타일 정의 (Tab 1과 통일감 유지) ---
    st.markdown("""
        <style>
        /* 위젯 간 적절한 수직 간격 */
        [data-testid="stVerticalBlock"] > div { margin-top: 0px !important; margin-bottom: 10px !important; }
        
        /* 텍스트 영역 폰트 크기 */
        .stTextArea textarea { font-size: 13px !important; }
        
        /* 드롭다운 박스 높이 및 폰트 */
        div[data-baseweb="select"] > div {
            height: 35px !important; min-height: 35px !important; font-size: 14px !important;
        }
        
        /* 라벨 폰트 설정 */
        .stSelectbox label, .stTextArea label {
            font-size: 13px !important; font-weight: 600 !important; color: #444 !important;
            margin-bottom: 5px !important; padding-top: 10px !important;
        }
        
        /* 결과창 코드 박스 스타일 */
        .stCode { border: 1px solid #e6e9ef !important; }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])

    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()

        # [연동] Tab 1에서 생성된 가사가 있다면 자동으로 가져옴
        default_lyrics = st.session_state.get('gen_lyrics', "")
        
        context_lyrics = st.text_area(
            "📝 기반 가사 (첫 번째 탭에서 생성 시 자동 입력)", 
            value=default_lyrics, 
            height=250, 
            placeholder="앨범 아트 분위기를 분석할 가사를 입력하거나, 첫 번째 탭에서 가사를 먼저 생성해주세요."
        )

        # 이미지 스타일 선택
        img_styles = [
            "사실적인 사진 (Photorealistic)", 
            "시네마틱 3D 렌더 (Cinematic 3D)", 
            "애니메이션/일러스트 (Anime/Illustration)", 
            "꿈꾸는 듯한 유화 (Dreamy Oil Painting)", 
            "추상적인 예술 (Abstract Art)",
            "사이버펑크/퓨처리스틱 (Cyberpunk)",
            "빈티지 레트로 포스터 (Vintage Poster)",
            "미니멀리즘 (Minimalism)"
        ]
        s_img_style = st.selectbox("🎨 이미지 스타일", img_styles)

        # 화면 비율
        aspect_ratios = ["1:1 (Square - 추천)", "16:9 (Widescreen)", "9:16 (Vertical)"]
        s_aspect = st.selectbox("📐 화면 비율", aspect_ratios)

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성된 이미지 생성 프롬프트")

        if gen_btn:
            if not api_key: st.error("첫 번째 탭에서 API 키를 먼저 설정해주세요."); return
            if not context_lyrics: st.error("분석할 가사 내용이 필요합니다."); return

            with st.spinner("가사의 은유와 분위기를 시각적 언어로 해석하는 중..."):
                try:
                    # [확실함] 최신 Gemini 3.1 Pro 모델 설정
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')

                    # [초강력] 비주얼 컨셉 아티스트 페르소나 부여 프롬프트
                    prompt = f"""
                    Act as a professional visual concept artist for music album covers.
                    Based on the provided Korean song lyrics and desired style, generate a highly detailed, evocative, and precise English image prompt suitable for Midjourney v6 or DALL-E 3.

                    Lyrics Context (Korean):
                    \"\"\"
                    {context_lyrics[:1500]} 
                    \"\"\"

                    Desired Visual Style: {s_img_style}
                    Aspect Ratio: {s_aspect}

                    Output Instructions:
                    1. Analyze the core emotion, metaphors, and imagery of the lyrics.
                    2. Translate these abstract concepts into concrete, descriptive visual elements.
                    3. Describe composition, lighting (e.g., volumetric, neon, soft, dramatic chiascuro), color palette, and specific objects or character expressions.
                    4. Use high-quality, descriptive English adjectives. Do not use generic terms like "photorealistic" if the style is abstract.
                    5. Output ONLY the practical English prompt. No conversational text.
                    6. Remove any markdown bolding (**) from the output.
                    """

                    response = model.generate_content(prompt)
                    # 별표(**) 제거 후 저장
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")

                except Exception as e:
                    st.error(f"프롬프트 생성 실패: {str(e)}")

        # 생성된 결과가 세션에 존재할 때만 출력
        if 'gen_img_prompt' in st.session_state:
            with st.container(border=True):
                st.write("**🎨 미드저니 / DALL-E 3용 영문 프롬프트**")
                # 복사하기 쉽게 st.code 사용
                st.code(st.session_state.gen_img_prompt, language="markdown")
                st.info("💡 위 프롬프트를 복사하여 Midjourney나 DALL-E 3에 입력하면 가사 분위기에 딱 맞는 앨범 아트를 얻을 수 있습니다.")
        else:
            st.info("👈 왼쪽에서 가사 컨텍스트와 스타일을 설정한 후 '생성' 버튼을 눌러주세요.")
