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

    # 세션 상태 초기화
    if 'final_title' not in st.session_state: st.session_state.final_title = ""
    if 'final_prompt' not in st.session_state: st.session_state.final_prompt = ""
    if 'final_lyrics' not in st.session_state: st.session_state.final_lyrics = ""

    # 생성 버튼
    if st.button("✨ 수노 전용 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 프로듀서가 되어 디테일한 영문 프롬프트와 메타태그 가사를 작성 중입니다..."):
                # 🔥 가장 결과가 좋았던 한국어 지시문으로 100% 원상 복구!
                query = f"""
                당신은 세계 최고의 음악 프로듀서이자 작사가입니다.
                다음 요소를 바탕으로 Suno AI에서 사용할 수 있는 완벽한 음악 생성 세트를 만들어주세요.
                
                - 주제: '{suno_subject}'
                - 장르: {s_selected_genre}
                - 분위기: {s_mood}
                - 템포: {s_tempo}
                - 악기: {s_inst}
                - 보컬: {s_vocal}
                
                응답 형식은 반드시 아래 4가지 항목을 정확히 포함해야 합니다. 다른 말은 절대 하지 마세요.
                
                한글제목: (곡 내용에 맞는 감성적인 한글 제목 1개)
                영문제목: (한글 제목의 의미를 담은 영문 제목 1개)
                음악프롬프트: (선택된 옵션을 모두 포함하여 곡의 리듬, 사운드 질감, 악기 연주 기법 등을 영문으로 매우 디테일하게 묘사할 것. 전문가가 편곡 지시서를 쓰듯 500자 이상으로 꽉 채워서 영어로만 작성할 것. 줄바꿈 없이 한 문단으로 쓸 것.)
                가사: (주제에 맞는 감동적인 가사. 반드시 [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge], [Outro] 대괄호 메타태그를 곡의 흐름에 맞게 포함할 것)
                """
                
                res_text = utils.generate_ai_text(query)
                
                try:
                    # 1. 항목별 파싱 (잘 작동하던 정규식 복구)
                    match_kr = re.search(r"한글제목:\s*([^\n]+)", res_text)
                    match_en = re.search(r"영문제목:\s*([^\n]+)", res_text)
                    match_prompt = re.search(r"음악프롬프트:\s*(.+?)(?=\n*가사:)", res_text, re.DOTALL | re.IGNORECASE)
                    match_lyrics = re.search(r"가사:\s*(.*)", res_text, re.DOTALL | re.IGNORECASE)
                    
                    # 🔥 2. 제목만 요구하신 대로 `한글_영어` 형태로 완벽하게 강제 결합!
                    title_kr = match_kr.group(1).strip() if match_kr else "제목생성실패"
                    title_en = match_en.group(1).strip() if match_en else "TitleError"
                    st.session_state.final_title = f"{title_kr}_{title_en}"

                    # 3. 프롬프트 저장 (1000자 제한)
                    if match_prompt and len(match_prompt.group(1).strip()) > 10:
                        raw_prompt = match_prompt.group(1).strip().replace("\n", " ")
                        st.session_state.final_prompt = raw_prompt[:995] 
                    else:
                        st.session_state.final_prompt = fallback_prompt

                    # 4. 가사 저장
                    if match_lyrics:
                        st.session_state.final_lyrics = match_lyrics.group(1).strip()
                    else:
                        # 파싱 실패 시 원문 전체라도 넣어서 에러 방지
                        clean_res = res_text.replace("한글제목:", "").replace("영문제목:", "")
                        st.session_state.final_lyrics = clean_res.strip()

                    st.success("🎉 작사 및 디테일 프롬프트 설계가 완료되었습니다! 우측 상단 📋 아이콘을 눌러 복사하세요.")
                
                except Exception as e:
                    st.error("⚠️ AI 서버 응답이 지연되었습니다. [생성] 버튼을 한 번 더 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 각 박스 우측 상단에 마우스를 올리면 나타나는 **📋 (복사) 아이콘**을 누르세요. 수동 편집칸은 모두 삭제되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.final_title if st.session_state.final_title else "생성 버튼을 누르면 한글_영문 제목이 표시됩니다.", language="text")
    
    st.write("### 2. 🎸 Style of Music (디테일 음악 프롬프트 - 최대 1000자)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (메타태그 포함 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "생성된 가사가 여기에 표시됩니다.", language="text")