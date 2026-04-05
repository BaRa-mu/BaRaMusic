import streamlit as st
import re
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("주제, 장르, 분위기 등을 세밀하게 선택하면 AI가 맞춤형 메타태그 가사와 디테일한 영문 음악 프롬프트를 자동으로 생성합니다.")
    
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

    # AI 생성 전 기본 폴백 프롬프트 (단순 조합)
    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    fallback_parts = []
    if s_selected_genre: fallback_parts.append(utils.extract_eng(s_selected_genre))
    if s_mood != "선택안함": fallback_parts.append(utils.extract_eng(s_mood))
    if s_tempo != "선택안함": fallback_parts.append(utils.extract_eng(s_tempo))
    if s_inst != "선택안함": fallback_parts.append(utils.extract_eng(s_inst))
    if s_vocal != "선택안함": fallback_parts.append(utils.extract_eng(s_vocal))
    fallback_prompt = ", ".join(fallback_parts)

    if st.button("✨ AI 제목, 프롬프트, 가사 자동 생성 (디테일 모드)", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 프로듀서가 되어 디테일한 영문 프롬프트와 메타태그 가사를 작성 중입니다..."):
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
                
                # 🔥 무적 방어막: AI가 어떻게 대답하든 에러가 나지 않도록 예외 처리 완벽 적용
                try:
                    # 1. 한글 제목 추출
                    match_kr = re.search(r"한글제목:\s*([^\n]+)", res_text)
                    st.session_state.gen_title_kr = match_kr.group(1).strip() if match_kr else "생성된 제목"

                    # 2. 영문 제목 추출
                    match_en = re.search(r"영문제목:\s*([^\n]+)", res_text)
                    st.session_state.gen_title_en = match_en.group(1).strip() if match_en else ""

                    # 3. 음악 프롬프트 추출 (음악프롬프트: 와 가사: 사이의 텍스트)
                    match_prompt = re.search(r"음악프롬프트:\s*(.+?)(?=\n*가사:)", res_text, re.DOTALL | re.IGNORECASE)
                    if match_prompt and len(match_prompt.group(1).strip()) > 10:
                        st.session_state.gen_prompt = match_prompt.group(1).strip()
                    else:
                        st.session_state.gen_prompt = fallback_prompt # 파싱 실패시 기본 조합 사용

                    # 4. 가사 추출 (가사: 이후 모든 텍스트)
                    match_lyrics = re.search(r"가사:\s*(.*)", res_text, re.DOTALL | re.IGNORECASE)
                    if match_lyrics:
                        st.session_state.s_lyrics = match_lyrics.group(1).strip()
                    else:
                        # 양식을 아예 안 지켰을 경우 통째로 가사칸에 넣음
                        st.session_state.s_lyrics = res_text.replace("한글제목:", "").replace("영문제목:", "").strip()

                    st.success("🎉 작사 및 디테일 프롬프트 설계가 완료되었습니다! 우측 상단 📋 아이콘을 눌러 복사하세요.")
                
                except Exception as e:
                    # 혹시라도 상상 못한 에러가 터져도 앱이 죽지 않게 보호
                    st.error("⚠️ AI 응답 형식이 불안정하여 기본 모드로 대체합니다. 다시 한 번 버튼을 눌러주세요.")
                    st.session_state.gen_prompt = fallback_prompt
                    st.session_state.s_lyrics = res_text

    st.divider()
    st.subheader("🛠️ 가사 및 제목 수동 에디터 (수정 시 하단 복사존에 실시간 반영)")
    col_r1, col_r2 = st.columns(2)
    with col_r1: st.session_state.gen_title_kr = st.text_input("📌 한글 제목", value=st.session_state.gen_title_kr)
    with col_r2: st.session_state.gen_title_en = st.text_input("📌 영문 제목", value=st.session_state.gen_title_en)
    
    st.write("📌 가사 구조 태그 삽입 (클릭 시 가사 맨 끝에 추가됨)")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("[Intro] 추가"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Intro]\n"
    if c2.button("[Verse] 추가"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Verse]\n"
    if c3.button("[Chorus] 추가"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Chorus]\n"
    if c4.button("[Bridge] 추가"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Bridge]\n"
    if c5.button("[Outro] 추가"): st.session_state.s_lyrics = st.session_state.get('s_lyrics', '') + "\n[Outro]\n"
    
    # 여기서 입력된 값이 바로 세션에 실시간 저장됨
    st.session_state.s_lyrics = st.text_area("가사 작성칸", value=st.session_state.get('s_lyrics', ''), height=200)

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("우측 상단의 네모난 📋 복사 아이콘을 누르면 1초 만에 깔끔하게 복사됩니다.")

    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        st.write("**1. 🎵 곡 제목 (Title)**")
        combined_title = f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}" if st.session_state.gen_title_en else st.session_state.gen_title_kr
        st.code(combined_title if combined_title.strip('_') else "주제를 적고 생성 버튼을 누르세요.", language="text")
        
    with col_c2:
        st.write("**2. 🎸 디테일 음악 스타일 (Style of Music)**")
        display_prompt = st.session_state.get('gen_prompt', fallback_prompt)
        st.code(display_prompt if display_prompt else "옵션을 선택하세요.", language="text")

    st.write("**3. 📝 가사 (Lyrics - 메타태그 포함)**")
    st.code(st.session_state.get('s_lyrics', '생성된 가사가 여기에 표시됩니다.') if st.session_state.get('s_lyrics', '').strip() else "가사를 생성하거나 입력하세요.", language="text")