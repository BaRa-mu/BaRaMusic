import streamlit as st
import time
import os
import google.generativeai as genai

def get_api_key():
    if os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f: return f.read().strip()
    return ""

def render_tab2():
    # [확실함] 가사 탭과 동일한 간격 유지
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: 0px !important; margin-bottom: 12px !important; }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            min-height: 32px !important; font-size: 13px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    l_col, r_col = st.columns([1, 2.3])
    
    with l_col:
        st.write("### 🖼️ 앨범 아트 설정")
        api_key = get_api_key()
        
        # 가사 데이터 연동
        context_lyrics = st.text_area("📝 기반 가사 컨텍스트", 
                                     value=st.session_state.get('gen_lyrics', ""), 
                                     height=250)

        s_img_style = st.selectbox("🎨 예술 스타일", ["사실적인 사진", "시네마틱 3D", "유화", "판타지 일러스트", "미니멀리즘"])
        s_ratio = st.selectbox("📐 화면 비율", ["1:1 (Square)", "16:9 (Wide)", "9:16 (Vertical)"])

        st.divider()
        gen_btn = st.button("🚀 이미지 프롬프트 생성", type="primary", use_container_width=True)

    with r_col:
        st.subheader("✨ 생성 결과물")
        
        if gen_btn:
            if not api_key or not context_lyrics: st.error("키와 가사를 확인하세요."); return
            with st.spinner("이미지 프롬프트 설계 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Act as a professional Concept Artist. Generate a detailed English image prompt (800+ chars) for a song album cover based on these lyrics: {context_lyrics[:1000]}. Style: {s_img_style}, Ratio: {s_ratio}. No bolding (**)."
                    
                    res = model.generate_content(prompt).text.replace("**", "")
                    st.session_state.gen_img_prompt = res
                except Exception as e: st.error(f"실패: {str(e)}")

        if 'gen_img_prompt' in st.session_state:
            st.code(st.session_state.gen_img_prompt, language="markdown")
