import streamlit as st
import os
import utils

def render_tab2():
    st.header("🎨 이미지 팩토리 (제목 파싱 및 디자인)")
    st.write("수노에서 완성한 음원(`한글제목_영문제목.mp3`)을 올리면 제목이 자동으로 분리되어 입력됩니다.")
    
    audio_for_parsing = st.file_uploader("🎧 수노 다운로드 음원 업로드", type=['wav', 'mp3'])
    
    t_kr = st.session_state.gen_title_kr
    t_en = st.session_state.gen_title_en
    if audio_for_parsing:
        base = os.path.splitext(audio_for_parsing.name)[0]
        parts = base.split('_')
        t_kr = parts[0]
        t_en = parts[1] if len(parts) > 1 else ""
        
    c_t1, c_t2 = st.columns(2)
    with c_t1: t_kr = st.text_input("📌 렌더링용 한글 제목 (수정 가능)", value=t_kr)
    with c_t2: t_en = st.text_input("📌 렌더링용 영문 제목 (수정 가능)", value=t_en)
    
    st.divider()
    st.subheader("⚙️ 2-1. 제목 텍스트 디자인 옵션")
    d1, d2, d3, d4 = st.columns(4)
    with d1: font_choice = st.selectbox("글씨체", list(utils.font_links.keys()))
    with d2: title_size = st.slider("메인 글씨 크기", 30, 120, 60)
    with d3: y_pos_percent = st.slider("Y축 위치 (%)", 5, 95, 15)
    with d4: line_spacing = st.slider("한영 줄간격", 0, 50, 15)
    
    st.divider()
    st.subheader("🎨 2-2. AI 배경 이미지 자동 생성 옵션")
    st.write("직접 이미지를 업로드하지 않으면 아래 설정대로 초고화질 AI 그림을 그려줍니다.")
    img_subject = st.text_input("🎯 배경에 그릴 사물/주제 (예: 창밖을 바라보는 고양이)")

    col_ig1, col_ig2 = st.columns(2)
    with col_ig1: img_pop_choice = st.selectbox("🎧 대중음악 느낌 이미지", list(utils.img_pop_genres.keys()))
    with col_ig2: img_ccm_choice = st.selectbox("⛪ CCM/홀리 느낌 이미지", list(utils.img_ccm_genres.keys()))

    col_is1, col_is2 = st.columns(2)
    with col_is1:
        img_mood_choice = st.selectbox("✨ 그림 분위기", list(utils.img_moods.keys()))
        img_style_choice = st.selectbox("🖌️ 그림 스타일", list(utils.img_styles.keys()))
    with col_is2:
        img_light_choice = st.selectbox("💡 조명 느낌", list(utils.img_lightings.keys()))
        img_color_choice = st.selectbox("🌈 색감", list(utils.img_colors.keys()))

    with st.expander("🎬 카메라/날씨/시대 디테일 설정"):
        col_is3, col_is4 = st.columns(2)
        with col_is3:
            img_camera_choice = st.selectbox("🎥 카메라 앵글", list(utils.img_cameras.keys()))
            img_time_choice = st.selectbox("⏰ 시간대", list(utils.img_times.keys()))
            img_weather_choice = st.selectbox("☁️ 날씨", list(utils.img_weathers.keys()))
        with col_is4:
            img_era_choice = st.selectbox("🏰 시대/배경", list(utils.img_eras.keys()))
            img_effect_choice = st.selectbox("✨ 특수효과", list(utils.img_effects.keys()))

    st.divider()
    st.subheader("🖼️ 2-3. 생성할 이미지 수량 및 직접 업로드")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        gen_main = st.checkbox("📺 메인 (가로 16:9)", value=True)
        img_up_main = st.file_uploader("직접 배경 올리기 (가로)", type=['jpg','png'])
    with col_i2:
        gen_tiktok = st.checkbox("📱 틱톡 풀영상 (세로 9:16)", value=False)
        img_up_tiktok = st.file_uploader("직접 배경 올리기 (세로)", type=['jpg','png'])
    with col_i3:
        num_s_img = st.slider("✂️ 쇼츠 이미지 (세로) 개수", 0, 6, 0)
        img_up_shorts = []
        for i in range(num_s_img):
            img_up_shorts.append(st.file_uploader(f"쇼츠 {i+1} 직접 올리기", type=['jpg','png'], key=f"s_img_{i}"))

    if st.button("✨ 선택한 이미지 모두 렌더링", type="primary", use_container_width=True):
        if not audio_for_parsing and not t_kr: st.error("제목이 비어있습니다. 음원을 올리거나 제목을 직접 적어주세요!")
        else:
            with st.spinner("이미지를 생성하고 텍스트를 정밀하게 입히고 있습니다..."):
                st.session_state.img_res_main = None
                st.session_state.img_res_tiktok = None
                st.session_state.img_res_shorts = []
                
                img_sel_genre = utils.img_ccm_genres[img_ccm_choice] if img_ccm_choice != "선택안함" else utils.img_pop_genres[img_pop_choice]
                prompt_parts = [
                    img_subject, img_sel_genre, utils.img_moods[img_mood_choice], utils.img_styles[img_style_choice], 
                    utils.img_lightings[img_light_choice], utils.img_colors[img_color_choice], utils.img_cameras[img_camera_choice],
                    utils.img_times[img_time_choice], utils.img_weathers[img_weather_choice], utils.img_eras[img_era_choice], utils.img_effects[img_effect_choice],
                    "masterpiece", "best quality", "4k resolution"
                ]
                final_img_prompt = ", ".join([p for p in prompt_parts if p])
                
                if gen_main:
                    st.session_state.img_res_main = utils.design_and_save_image(1280, 720, final_img_prompt, 111, t_kr, t_en, font_choice, title_size, y_pos_percent, line_spacing, "designed_main.png", img_up_main)
                if gen_tiktok:
                    st.session_state.img_res_tiktok = utils.design_and_save_image(720, 1280, final_img_prompt, 222, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, "designed_tiktok.png", img_up_tiktok)
                for i in range(num_s_img):
                    path = utils.design_and_save_image(720, 1280, final_img_prompt, 333+i, t_kr, t_en, font_choice, int(title_size*0.75), y_pos_percent, line_spacing, f"designed_short_{i+1}.png", img_up_shorts[i])
                    st.session_state.img_res_shorts.append(path)
                    
            st.success("🎉 디자인 완료! 아래에서 이미지를 미리보고 다운로드하세요.")
            
    if st.session_state.get('img_res_main') or st.session_state.get('img_res_tiktok') or st.session_state.get('img_res_shorts'):
        st.subheader("📥 완성된 이미지 미리보기 및 다운로드")
        res_cols = st.columns(3)
        col_idx = 0
        
        if st.session_state.get('img_res_main'):
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_res_main, caption="메인 (16:9)")
                with open(st.session_state.img_res_main, "rb") as f: st.download_button("⬇️ 가로 이미지 다운로드", f, "Main_Cover.png", "image/png", use_container_width=True)
            col_idx += 1
            
        if st.session_state.get('img_res_tiktok'):
            with res_cols[col_idx % 3]:
                st.image(st.session_state.img_res_tiktok, caption="틱톡 (9:16)")
                with open(st.session_state.img_res_tiktok, "rb") as f: st.download_button("⬇️ 세로 이미지 다운로드", f, "TikTok_Cover.png", "image/png", use_container_width=True)
            col_idx += 1
            
        if st.session_state.get('img_res_shorts'):
            for i, p in enumerate(st.session_state.img_res_shorts):
                with res_cols[col_idx % 3]:
                    st.image(p, caption=f"쇼츠 {i+1} (9:16)")
                    with open(p, "rb") as f: st.download_button(f"⬇️ 쇼츠 {i+1} 다운로드", f, f"Shorts_{i+1}_Cover.png", "image/png", use_container_width=True, key=f"btn_s_{i}")
                col_idx += 1