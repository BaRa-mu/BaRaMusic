import streamlit as st
import re
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("옵션을 선택하고 버튼을 누르면 수노(Suno)에 바로 복사/붙여넣기 할 수 있는 완벽한 세트가 만들어집니다.")
    
    suno_subject = st.text_input("🎯 곡의 주제/메시지 (필수 입력, 예: 지친 하루의 위로, 십자가의 사랑)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: s_pop = st.selectbox("🎧 대중음악 장르 (CCM 선택 시 무시됨)", utils.suno_pop_list)
    with col_s2: s_ccm = st.selectbox("⛪ CCM / 예배음악 장르", utils.suno_ccm_list)

    col_s3, col_s4 = st.columns(2)
    with col_s3: s_mood = st.selectbox("✨ 곡의 분위기", utils.suno_moods_list)
    with col_s4: s_tempo = st.selectbox("🥁 템포 (속도)", utils.suno_tempo_list)
    
    col_s5, col_s6 = st.columns(2)
    with col_s5: s_inst = st.selectbox("🎹 주요 악기", utils.suno_inst_list)
    with col_s6: s_vocal = st.selectbox("🎤 보컬 구성", [v for v in utils.suno_vocals_list if not v.startswith("---")])

    # 기본 프롬프트 조합 (AI 실패 시 방어용)
    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    fallback_parts = []
    if s_selected_genre: fallback_parts.append(utils.extract_eng(s_selected_genre))
    if s_mood != "선택안함": fallback_parts.append(utils.extract_eng(s_mood))
    if s_tempo != "선택안함": fallback_parts.append(utils.extract_eng(s_tempo))
    if s_inst != "선택안함": fallback_parts.append(utils.extract_eng(s_inst))
    if s_vocal != "선택안함": fallback_parts.append(utils.extract_eng(s_vocal))
    fallback_prompt = ", ".join(fallback_parts)

    # 🌟 세션 상태 초기화 (처음 로드 시 빈칸 방지)
    if 'final_title' not in st.session_state: st.session_state.final_title = ""
    if 'final_prompt' not in st.session_state: st.session_state.final_prompt = ""
    if 'final_lyrics' not in st.session_state: st.session_state.final_lyrics = ""

    # 생성 버튼
    if st.button("✨ 수노 전용 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 곡을 기획하고 있습니다. 1000자 분량의 영문 프롬프트와 가사를 작성 중입니다..."):
                # 🔥 AI가 앵무새처럼 질문을 따라하지 못하도록, 지시문은 영어로 강력하게 통제합니다.
                query = f"""Write a song based on the following details.
Topic: {suno_subject}
Genre: {s_selected_genre}
Mood: {s_mood}
Tempo: {s_tempo}
Instruments: {s_inst}
Vocal: {s_vocal}

You MUST follow this EXACT structure. Do not include any other words, explanations, or your own comments.

===TITLE===
(Write one Korean title and one English title separated by an underscore. Example: 밤하늘의 별_Stars in the Night Sky)

===PROMPT===
(Write a highly detailed, 800 to 1000 character long English music prompt. Describe the musical texture, rhythm, specific instruments, vocal style, and atmosphere in rich detail using comma-separated keywords and phrases. Make it as descriptive as possible.)

===LYRICS===
(Write the song lyrics in Korean based on the topic. You MUST include structural meta-tags like [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Bridge], [Guitar Solo], [Outro] appropriately throughout the song.)
"""
                
                res_text = utils.generate_ai_text(query)
                
                # 🔥 확실한 마커(===마커===)를 통해 텍스트를 완벽하게 분리 추출
                try:
                    match_title = re.search(r"===TITLE===\s*(.+?)(?=\n*===PROMPT===)", res_text, re.DOTALL | re.IGNORECASE)
                    match_prompt = re.search(r"===PROMPT===\s*(.+?)(?=\n*===LYRICS===)", res_text, re.DOTALL | re.IGNORECASE)
                    match_lyrics = re.search(r"===LYRICS===\s*(.*)", res_text, re.DOTALL | re.IGNORECASE)
                    
                    st.session_state.final_title = match_title.group(1).strip() if match_title else "제목 생성 에러_Title Error"
                    
                    if match_prompt:
                        raw_prompt = match_prompt.group(1).strip().replace("\n", " ")
                        st.session_state.final_prompt = raw_prompt[:995] # 수노 1000자 제한 맞춤
                    else:
                        st.session_state.final_prompt = fallback_prompt
                        
                    if match_lyrics:
                        st.session_state.final_lyrics = match_lyrics.group(1).strip()
                    else:
                        st.session_state.final_lyrics = "가사 생성에 실패했습니다. 다시 생성해주세요."
                        
                    st.success("🎉 생성 완료! 아래 📋 아이콘을 눌러 수노(Suno AI)에 바로 붙여넣기 하세요.")
                
                except Exception as e:
                    st.error("⚠️ AI 응답이 불안정합니다. 버튼을 한 번 더 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 우측 상단 모서리에 마우스를 올리면 나타나는 **📋 (복사) 아이콘**을 누르세요. 불필요한 수동 편집칸은 모두 삭제되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.final_title if st.session_state.final_title else "생성 버튼을 누르면 한글_영문 제목이 표시됩니다.", language="text")
    
    st.write("### 2. 🎸 Style of Music (디테일 음악 프롬프트 - 최대 1000자)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (메타태그 포함 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "생성된 가사가 여기에 표시됩니다.", language="text")