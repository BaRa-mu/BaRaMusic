import streamlit as st
import time
import os
import google.generativeai as genai

# [확실함] API 키 로컬 로드
def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 간격을 넓히고 답답함을 제거한 이미지 탭 전용 CSS
    st.markdown("""
        <style>
        /* 위젯 사이 간격을 15px로 넓혀 답답함 해소 */
        [data-testid="stVerticalBlock"] > div { margin-top: 5px !important; margin-bottom: 15px !important; }
        
        /* 박스 높이는 32px 슬림 유지, 폰트 정렬 최적화 */
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; font-size: 13px !important;
        }
        
        /* 라벨 가독성 확보 */
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-size: 12px !important; font-weight: 600 !important;
            margin-bottom: 6px !important; color: #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()

        # 가사 탭 데이터 연동
        context_lyrics = st.text_area("📝 기반 가사 컨텍스트", 
                                     value=st.session_state.get('gen_lyrics', ""), 
                                     height=200, 
                                     placeholder="가사를 입력하거나 첫 탭에서 생성하세요.")

        # [확실함] 건드리지 않는 정밀 이미지 스타일 메뉴
        img_styles = [
            "사실적인 사진 (Photorealistic)", "시네마틱 3D 렌더 (Cinematic 3D)", 
            "꿈꾸는 듯한 유화 (Oil Painting)", "추상적인 수채화 (Abstract Watercolor)", 
            "신비로운 판타지 일러스트 (Fantasy)", "현대적인 미니멀리즘 (Minimalism)", 
            "빈티지 레트로 포스터 (Vintage)", "사이버펑크 네온 (Cyberpunk)"
        ]
        s_img_style = st.selectbox("🎨 예술 스타일", img_styles)
        
        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])
        s_mood = st.selectbox("✨ 비주얼 분위기", ["웅장하고 장엄한", "따뜻하고 포근한", "어둡고 고요한", "희망차고 밝은", "몽환적이고 신비로운"])

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key: st.error("가사 탭에서 API 키를 먼저 저장하세요."); return
            if not context_lyrics: st.error("분석할 가사가 없습니다."); return
            
            with st.spinner("가사의 은유를 시각적 프롬프트로 변환 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # [초강력] 이미지 프롬프트 생성 지시문
                    prompt = f"""
                    Role: Professional Concept Artist for Music Album Covers.
                    Task: Create a highly detailed English image generation prompt.
                    
                    Lyrics to analyze:
                    {context_lyrics[:1000]}
                    
                    Requirements:
                    1. Analyze the core theme and emotions of the lyrics.
                    2. Describe the scene, lighting, color palette, and composition in English.
                    3. Style: {s_img_style} / Mood: {s_mood} / Ratio: {s_ratio}.
                    4. Total length should be around 800-1000 characters for high precision.
                    5. Output ONLY the English prompt. NO bolding (**), NO introductory text.
                    """
                    
                    response = model.generate_content(prompt)
                    # [확실함] 별표(**) 제거 처리
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")
                    
                except Exception as e:
                    st.error(f"생성 실패: {str(e)}")

        # 결과 출력 (방어적 렌더링)
        if 'gen_img_prompt' in st.session_state:
            with st.container(border=True):
                st.write("**🎨 AI 이미지 생성용 영문 프롬프트 (Midjourney / DALL-E)**")
                st.code(st.session_state.gen_img_prompt, language="markdown")
                st.info("💡 위 텍스트를 복사하여 이미지 생성 AI에 입력하세요.")
        else:
            st.info("👈 왼쪽에서 설정을 마친 후 생성 버튼을 눌러주세요.")

[검증]
* **A 영향**: `margin-bottom: 15px`를 적용하여 왼쪽 메뉴의 답답함을 구조적으로 해결함. [확실함]
* **B 영향**: 가사 탭의 `st.session_state`를 공유하여 데이터 재입력의 번거로움을 제거함. [확실함]
* **회귀 가능성**: 모델명을 고정하고 별표 제거 로직을 삽입하여 가독성 저해 요소를 사전 차단함. [Certain]
