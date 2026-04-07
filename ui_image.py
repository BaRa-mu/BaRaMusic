import streamlit as st
import os
import utils

def render_tab2():
    st.header("🎨 이미지 팩토리 (디자인 & 다운로드)")
    aud_parsing = st.file_uploader("🎧 음원 업로드 (제목 파싱용)", type=['wav', 'mp3'])
    
    t_kr = st.session_state.get('gen_title_kr', "")
    t_en = st.session_state.get('gen_title_en', "")
    if aud_parsing:
        base = os.path.splitext(aud_parsing.name)[0]
        parts = base.split('_')
        t_kr = parts[0]
        t_en = parts[1] if len(parts) > 1 else ""
        
    c1, c2 = st.columns(2)
    with c1: t_kr = st.text_input("📌 한글 제목", value=t_kr)
    with c2: t_en = st.text_input("📌 영문 제목", value=t_en)
    
    d1, d2, d3, d4 = st.columns(4)
    with d1: font = st.selectbox("글씨체", list(utils.font_links.keys()))
    with d2: size = st.slider("크기", 30, 120, 60)
    with d3: y_pos = st.slider("위치(%)", 5, 95, 15)
    with d4: spc = st.slider("한영 간격", 0, 50, 15)
    
    prompt = st.text_input("🤖 AI 배경 프롬프트", "cinematic beautiful sky, peaceful, 4k")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        gen_m = st.checkbox("📺 메인(16:9)", value=True)
        up_m = st.file_uploader("메인 배경", type=['jpg','png'])
    with col_i2:
        gen_t = st.checkbox("📱 틱톡(9:16)", value=False)
        up_t = st.file_uploader("틱톡 배경", type=['jpg','png'])
    with col_i3:
        num_s = st.slider("✂️ 쇼츠(9:16)", 0, 6, 0)
        up_s = [st.file_uploader(f"쇼츠 {i+1} 배경", type=['jpg','png'], key=f"img_up_{i}") for i in range(num_s)]

    if st.button("✨ 디자인 이미지 렌더링", type="primary", use_container_width=True):
        if gen_m: st.session_state.res_m = utils.design_and_save_image(1280, 720, prompt, 1, t_kr, t_en, font, size, y_pos, spc, "dm.png", up_m)
        if gen_t: st.session_state.res_t = utils.design_and_save_image(720, 1280, prompt, 2, t_kr, t_en, font, int(size*0.75), y_pos, spc, "dt.png", up_t)
        st.session_state.res_s = [utils.design_and_save_image(720, 1280, prompt, 10+i, t_kr, t_en, font, int(size*0.75), y_pos, spc, f"ds_{i}.png", up_s[i]) for i in range(num_s)]
        st.success("✅ 이미지 생성 완료!")

    if st.session_state.get('res_m') or st.session_state.get('res_t') or st.session_state.get('res_s'):
        st.divider()
        cols = st.columns(3)
        idx = 0
        if st.session_state.get('res_m'):
            with cols[idx%3]: 
                st.image(st.session_state.res_m)
                st.download_button("⬇️ 가로 다운", open(st.session_state.res_m, "rb"), "Main.png")
            idx+=1
        if st.session_state.get('res_t'):
            with cols[idx%3]: 
                st.image(st.session_state.res_t)
                st.download_button("⬇️ 틱톡 다운", open(st.session_state.res_t, "rb"), "TikTok.png")
            idx+=1
        for i, p in enumerate(st.session_state.get('res_s', [])):
            with cols[idx%3]: 
                st.image(p)
                st.download_button(f"⬇️ 쇼츠{i+1} 다운", open(p, "rb"), f"Short_{i+1}.png")
            idx+=1