import streamlit as st
import re
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("주제, 장르, 분위기 등을 세밀하게 선택하면 AI가 맞춤형 메타태그 프롬프트와 가사를 자동으로 작사합니다.")
    
    suno_subject = st.text_input("🎯 곡의 주제/메시지 (필수 입력, 예: 지친 하루의 위로, 첫사랑의 설렘)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: s_pop = st.selectbox("🎧 대중음악 장르 (CCM 선택 시 무시됨)", utils.suno_pop_list)
    with col_s2: s_ccm = st.selectbox("⛪ CCM / 예배음악 장르", utils.suno_ccm_list)

    col_s3, col_s4 = st.columns(2)
    with col_s3: s_mood = st.selectbox("✨ 곡의 분위기", utils.suno_moods_list)
    with col_s4: s_tempo = st.selectbox("🥁 템포 (속도)", utils.suno_tempo_list)
    
    col_s5, col_s6 = st.columns(2)
    with col_s5: s_inst = st.selectbox("🎹 주요 악기", utils.suno_inst_list)
    with col_s6: s_vocal = st.selectbox("🎤 보컬 구성", [v for v in utils.suno_vocals_list if not v.startswith("---")])

    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    prompt_parts = []
    if s_selected_genre: prompt_parts.append(utils.extract_eng(s_selected_genre))
    if s_mood != "선택안함": prompt_parts.append(utils.extract_eng(s_mood))
    if s_tempo != "선택안함": prompt_parts.append(utils.extract_eng(s_tempo))
    if s_inst != "선택안함": prompt_parts.append(utils.extract_eng(s_inst))
    if s_vocal != "선택안함": prompt_parts.append(utils.extract_eng(s_vocal))
    final_suno_prompt = ", ".join(prompt_parts)[:1000]

    if st.button("✨ AI 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 수노 양식에 맞춰 완벽한 가사를 작성하고 있습니다..."):
                query = f"주제: '{suno_subject}', 장르: {s_selected_genre}, 분위기: {s_mood}, 템포: {s_tempo}, 보컬: {s_vocal}. 이 곡의 한글제목, 영문제목, 그리고 수노(Suno)에 바로 복사해서 쓸 가사를 써줘. 가사에는 반드시 [Intro], [Verse 1], [Chorus], [Verse 2], [Bridge], [Guitar Solo], [Outro] 같은 대괄호 메타태그를 곡의 흐름에 맞게 적재적소에 넣어줘. 응답형식:\n한글제목:\n영문제목:\n가사:\n"
                res_text = utils.generate_ai_text(query)
                
                match_kr = re.search(r"한글제목:\s*(.+)", res_text)
                match_en = re.search(r"영문제목:\s*(.+)", res_text)
                match_lyrics = re.search(r"가사:\s*(.*)", res_text, re.DOTALL)
                
                st.session_state.gen_title_kr = match_kr.group(1).strip() if match_kr else "제목 생성 실패"
                st.session_state.gen_title_en = match_en.group(1).strip() if match_en else ""
                st.session_state.gen_lyrics = match_lyrics.group(1).strip() if match_lyrics else res_text
                st.session_state.gen_prompt = final_suno_prompt
                
            st.success("🎉 작사가 완료되었습니다! 아래 복사존에서 우측 상단 아이콘을 눌러 수노에 복사하세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")

    st.write("**1. 🎵 Title (곡 제목)**")
    combined_title = f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}" if st.session_state.gen_title_en else st.session_state.gen_title_kr
    st.code(combined_title if combined_title.strip('_') else "주제를 적고 생성 버튼을 누르세요.", language="text")
    
    st.write("**2. 🎸 Style of Music (음악 스타일 - 최대 1000자 자동조절)**")
    st.code(st.session_state.get('gen_prompt', final_suno_prompt) if st.session_state.get('gen_prompt', final_suno_prompt) else "옵션을 선택하세요.", language="text")

    st.write("**3. 📝 Lyrics (가사 - 메타태그 포함)**")
    st.code(st.session_state.get('gen_lyrics', '생성된 가사가 여기에 표시됩니다.'), language="text")