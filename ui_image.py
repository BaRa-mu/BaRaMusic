import streamlit as st
import os
import utils

def render_tab2():
    st.header("🎨 이미지 팩토리 (개별 맞춤 렌더링)")
    
    # --- [변경사항: 1단계(배경생성)와 2단계(텍스트/효과 편집)로 구조 완벽 격리] ---
    aud_parsing = st.file_uploader("🎧 음원 업로드 (제목 파싱용/선택사항)", type=['wav', 'mp3'])
    
    t_kr_def = st.session_state.get('gen_title_kr', "")
    t_en_def = st.session_state.get('gen_title_en', "")
    if aud_parsing:
        base = os.path.splitext(aud_parsing.name)[0]
        parts = base.split('_')
        t_kr_def = parts[0]
        t_en_def = parts[1] if len(parts) > 1 else ""
        
    c1, c2 = st.columns(2)
    with c1: global_tk = st.text_input("📌 기본 한글 제목 (초기값)", value=t_kr_def)
    with c2: global_te = st.text_input("📌 기본 영문 제목 (초기값)", value=t_en_def)
    
    st.divider()
    st.subheader("🖼️ 1단계: 배경 이미지 생성 및 등록")
    prompt = st.text_input("🤖 AI 배경 프롬프트", "cinematic beautiful sky, peaceful, 4k")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        gen_m = st.checkbox("📺 메인(16:9)", value=True)
        up_m = st.file_uploader("메인 배경", type=['jpg','png'], key="upm_bg")
    with col_i2:
        gen_t = st.checkbox("📱 틱톡(9:16)", value=False)
        up_t = st.file_uploader("틱톡 배경", type=['jpg','png'], key="upt_bg")
    with col_i3:
        num_s = st.slider("✂️ 쇼츠(9:16)", 0, 6, 0, key="num_s_bg")
        up_s = [st.file_uploader(f"쇼츠 {i+1} 배경", type=['jpg','png'], key=f"img_up_{i}") for i in range(num_s)]

    if st.button("✨ 1단계: 베이스 배경 렌더링", type="primary", use_container_width=True):
        if gen_m: st.session_state.bg_m = utils.prepare_background(1280, 720, prompt, 1, "bg_m.png", up_m)
        if gen_t: st.session_state.bg_t = utils.prepare_background(720, 1280, prompt, 2, "bg_t.png", up_t)
        for i in range(num_s):
            st.session_state[f'bg_s_{i}'] = utils.prepare_background(720, 1280, prompt, 10+i, f"bg_s_{i}.png", up_s[i])
        st.success("✅ 베이스 배경 생성 완료! 아래에서 개별 텍스트 및 효과를 설정하세요.")

    if st.session_state.get('bg_m') or st.session_state.get('bg_t') or any(st.session_state.get(f'bg_s_{i}') for i in range(6)):
        st.divider()
        st.subheader("⚙️ 2단계: 이미지 개별 텍스트 & 효과 디자인")
        
        tabs_labels = []
        if st.session_state.get('bg_m'): tabs_labels.append("📺 메인")
        if st.session_state.get('bg_t'): tabs_labels.append("📱 틱톡")
        for i in range(6): 
            if st.session_state.get(f'bg_s_{i}'): tabs_labels.append(f"✂️ 쇼츠 {i+1}")
            
        if not tabs_labels: return
        tabs = st.tabs(tabs_labels)
        t_idx = 0
        
        def render_text_editor(bg_key, res_key, res_name, is_landscape):
            col1, col2 = st.columns([1, 1.2])
            with col1:
                st.image(st.session_state[bg_key], caption="원본 배경")
            with col2:
                tk = st.text_input("한글 제목", value=global_tk, key=f"tk_{res_key}")
                te = st.text_input("영문 제목", value=global_te, key=f"te_{res_key}")
                
                c_a, c_b = st.columns(2)
                with c_a: fnt = st.selectbox("글씨체", list(utils.font_links.keys()), key=f"fnt_{res_key}")
                with c_b: fx = st.selectbox("효과", utils.effects_list, key=f"fx_{res_key}")
                
                sz = st.slider("크기", 30, 150, 60 if is_landscape else 45, key=f"sz_{res_key}")
                yp = st.slider("위치(%)", 5, 95, 15, key=f"yp_{res_key}")
                
                if st.button("🖌️ 이 이미지에 적용", key=f"btn_{res_key}"):
                    st.session_state[res_key] = utils.apply_text_to_image(
                        st.session_state[bg_key], tk, te, fnt, sz, yp, 15, fx, f"{res_key}.png"
                    )
            
            if st.session_state.get(res_key) and os.path.exists(st.session_state[res_key]):
                st.success("적용 완료!")
                st.image(st.session_state[res_key], caption="최종 결과물")
                with open(st.session_state[res_key], "rb") as f:
                    st.download_button(f"⬇️ {res_name} 다운로드", f.read(), res_name, key=f"dl_{res_key}")

        if st.session_state.get('bg_m'):
            with tabs[t_idx]: render_text_editor('bg_m', 'res_m', 'Main.png', True)
            t_idx += 1
        if st.session_state.get('bg_t'):
            with tabs[t_idx]: render_text_editor('bg_t', 'res_t', 'TikTok.png', False)
            t_idx += 1
        for i in range(6):
            if st.session_state.get(f'bg_s_{i}'):
                with tabs[t_idx]: render_text_editor(f'bg_s_{i}', f'res_s_{i}', f'Short_{i+1}.png', False)
                t_idx += 1
    # -----------------------------------------------------------------------------------