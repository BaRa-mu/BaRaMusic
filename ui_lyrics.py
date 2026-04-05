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

    # 생성 버튼
    if st.button("✨ 수노 전용 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 프로듀서가 되어 1000자 분량의 디테일한 영문 프롬프트와 가사를 작성 중입니다... (약 10초 소요)"):
                # 🔥 AI에게 불필요한 말(가사 포인트 등)을 절대 금지하고, 1000자 프롬프트를 꽉 채우도록 강력하게 강제함
                query = f"""
                당신은 세계 최고의 음악 프로듀서이자 작사가입니다.
                다음 요소를 바탕으로 Suno AI 음악 생성용 데이터를 작성하세요.
                주제: '{suno_subject}', 장르: {s_selected_genre}, 분위기: {s_mood}, 템포: {s_tempo}, 악기: {s_inst}, 보컬: {s_vocal}
                
                [엄격한 규칙]
                1. 절대 부연 설명, 인사말, "가사 포인트", "작성 완료했습니다" 같은 해설을 적지 마세요.
                2. 가사 안에 괄호를 치고 (기타가 흐르며) 같은 지시문도 절대 적지 마세요. 오직 부를 가사와 [Intro], [Verse], [Chorus] 등의 대괄호 메타태그만 적으세요.
                3. [프롬프트] 섹션은 반드시 영어로만 작성하며, 곡의 악기 구성, 질감, 리듬, 코러스의 웅장함, 보컬 톤 등을 묘사하는 단어들을 쉼표(,)로 나열하여 800자에서 1000자 사이로 매우 길고 화려하게 꽉 채워주세요.
                
                응답은 반드시 아래 3개의 섹션 태그를 그대로 포함하여 작성하세요.
                
                [제목]
                (한글제목_EnglishTitle 형태로 딱 1줄만 작성)
                
                [프롬프트]
                (영문 800~1000자 분량의 디테일한 스타일 프롬프트)
                
                [가사]
                [Intro]
                (가사시작...)
                """
                
                res_text = utils.generate_ai_text(query)
                
                # 🔥 3개의 강제 마커를 기준으로 완벽하게 텍스트를 파싱
                try:
                    match_title = re.search(r"\[제목\]\s*(.+?)(?=\n*\[프롬프트\])", res_text, re.DOTALL | re.IGNORECASE)
                    match_prompt = re.search(r"\[프롬프트\]\s*(.+?)(?=\n*\[가사\])", res_text, re.DOTALL | re.IGNORECASE)
                    match_lyrics = re.search(r"\[가사\]\s*(.*)", res_text, re.DOTALL | re.IGNORECASE)
                    
                    st.session_state.gen_title_kr = match_title.group(1).strip() if match_title else "제목_Title"
                    
                    if match_prompt and len(match_prompt.group(1).strip()) > 20:
                        raw_prompt = match_prompt.group(1).strip().replace("\n", " ")
                        # 수노 1000자 제한 방지
                        st.session_state.gen_prompt = raw_prompt[:990] 
                    else:
                        st.session_state.gen_prompt = fallback_prompt
                        
                    st.session_state.s_lyrics = match_lyrics.group(1).strip() if match_lyrics else "가사를 생성하지 못했습니다. 다시 시도해주세요."
                    
                    st.success("🎉 생성 완료! 아래 📋 아이콘을 눌러 수노(Suno AI)에 바로 붙여넣기 하세요.")
                
                except Exception as e:
                    st.error("⚠️ AI 서버 응답이 지연되었습니다. [생성] 버튼을 한 번 더 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 원클릭 복사존")
    st.info("💡 각 박스 우측 상단에 마우스를 올리면 나타나는 **📋 (복사) 아이콘**을 누르면 내용이 복사됩니다. 수동 입력칸은 제거되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.get('gen_title_kr', '주제를 적고 생성 버튼을 누르세요.'), language="text")
    
    st.write("### 2. 🎸 Style of Music (음악 프롬프트)")
    st.code(st.session_state.get('gen_prompt', fallback_prompt) if st.session_state.get('gen_prompt', fallback_prompt) else "옵션을 선택하세요.", language="text")

    st.write("### 3. 📝 Lyrics (가사)")
    st.code(st.session_state.get('s_lyrics', '생성된 가사가 여기에 표시됩니다.') if st.session_state.get('s_lyrics', '').strip() else "가사를 생성하거나 입력하세요.", language="text")