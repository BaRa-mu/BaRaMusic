import streamlit as st
import os
import google.generativeai as genai

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: 5px !important; margin-bottom: 15px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; font-size: 13px !important;
        }
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
        lyrics_val = st.session_state.get('gen_lyrics', "")
        context_lyrics = st.text_area("📝 기반 가사 컨텍스트", value=lyrics_val, height=200)

        img_styles = ["사실적인 사진", "시네마틱 3D", "유화", "수채화", "판타지 일러스트", "미니멀리즘", "빈티지", "사이버펑크"]
        s_img_style = st.selectbox("🎨 예술 스타일", img_styles)
        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])
        s_mood = st.selectbox("✨ 분위기", ["웅장한", "따뜻한", "고요한", "밝은", "몽환적인"])

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not api_key: st.error("가사 탭에서 API 키를 먼저 저장하세요."); return
            if not context_lyrics: st.error("가사가 없습니다."); return
            
            with st.spinner("AI 분석 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.1-pro-preview')
                    
                    # [확실함] 구문 오류 방지를 위한 안전한 프롬프트 결합
                    base_prompt = "Role: Music Album Concept Artist. Generate a 1000-character English image prompt. "
                    base_prompt += f"Style: {s_img_style}, Mood: {s_mood}, Ratio: {s_ratio}. "
                    base_prompt += "Analyze these lyrics and describe the scene without bolding (**): "
                    
                    # 가사 결합 시 특수문자 보호
                    final_prompt = base_prompt + "\n\n" + context_lyrics[:1000]
                    
                    response = model.generate_content(final_prompt)
                    st.session_state.gen_img_prompt = response.text.strip().replace("**", "")
                except Exception as e:
                    st.error(f"실패: {str(e)}")

        if 'gen_img_prompt' in st.session_state:
            st.code(st.session_state.gen_img_prompt, language="markdown")
