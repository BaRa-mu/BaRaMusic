import streamlit as st
import re
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("옵션을 선택하고 생성 버튼을 누르면, 수동 타이핑 없이 수노(Suno)에 바로 복사할 수 있는 완벽한 세트가 만들어집니다.")
    
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

    # 기본 프롬프트 조합 (만약의 경우를 대비한 폴백)
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

    # ✨ 생성 버튼
    if st.button("✨ 수노 전용 제목 및 가사 1초 완성", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 가장 먼저 입력해주세요!")
        else:
            with st.spinner("AI가 1000자 분량의 디테일 영문 프롬프트와 메타태그 가사를 작성 중입니다... (약 10초 소요)"):
                
                # 🔥 AI가 템플릿을 복사하지 못하도록 영문으로 아주 강력하고 명확하게 지시
                query = f"""Create a song based on the details below.
Topic: {suno_subject}
Style: {s_selected_genre}, {s_mood}, {s_tempo}, {s_inst}, {s_vocal}

CRITICAL RULES:
1. Do NOT write conversational text like "Here is your song" or "가사 포인트".
2. You MUST strictly use the 4 exact tags below to start each section. Do not use asterisks (**).

TitleKR:
TitleEN:
Prompt:
Lyrics:

For "Prompt:", write a highly detailed, 800 to 1000 character English prompt describing the genre, mood, rhythm, specific instruments, and vocal style. Use comma-separated keywords. No line breaks.
For "Lyrics:", write the full Korean lyrics. You MUST include tags like [Intro], [Verse 1], [Chorus], [Bridge], [Outro].
"""
                
                res_text = utils.generate_ai_text(query)
                
                # AI가 마크다운(**)을 썼을 경우를 대비해 싹 다 지워버림
                clean_text = res_text.replace("**", "").replace("##", "")
                
                t_kr = "제목 생성 오류"
                t_en = "TitleError"
                prmpt = fallback_prompt
                lyr = "가사를 생성하지 못했습니다."

                try:
                    # 🔥 무조건 성공하는 스플릿(Split) 파싱 기법 도입
                    if "TitleKR:" in clean_text and "TitleEN:" in clean_text:
                        t_kr = clean_text.split("TitleKR:")[1].split("TitleEN:")[0].strip()
                    
                    if "TitleEN:" in clean_text and "Prompt:" in clean_text:
                        t_en = clean_text.split("TitleEN:")[1].split("Prompt:")[0].strip()

                    if "Prompt:" in clean_text and "Lyrics:" in clean_text:
                        prmpt = clean_text.split("Prompt:")[1].split("Lyrics:")[0].strip().replace("\n", " ")
                        
                    if "Lyrics:" in clean_text:
                        lyr_raw = clean_text.split("Lyrics:")[1].strip()
                        # AI가 뒤에 쓸데없이 덧붙인 '가사 포인트', '참고:' 등을 무자비하게 잘라버림
                        lyr = re.split(r'\n\s*(가사 포인트|참고:|Note:|설명:)', lyr_raw)[0].strip()

                    # 찌꺼기 괄호 기호 제거
                    t_kr = re.sub(r'[\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\[\]\(\)]', '', t_en).strip()
                    
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    
                    # 프롬프트 1000자 초과 방지
                    st.session_state.final_prompt = prmpt[:995] if len(prmpt) > 10 else fallback_prompt
                    st.session_state.final_lyrics = lyr
                    
                    # 탭 2(이미지 팩토리) 연동을 위한 데이터 넘기기
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 완벽하게 생성되었습니다! 아래의 📋 아이콘을 눌러 수노(Suno AI)에 바로 붙여넣기 하세요.")
                
                except Exception as e:
                    st.error("⚠️ AI가 형식 규칙을 어겼습니다. [생성] 버튼을 다시 한 번 눌러주세요.")
                    # 혹시나 실패해도 아예 안 나오는 것을 막기 위해 원문 출력
                    st.session_state.final_lyrics = clean_text

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 우측 상단의 **📋 (복사) 아이콘**을 누르세요. 수동 편집칸은 100% 제거되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.final_title if st.session_state.final_title else "주제를 적고 생성 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (디테일 음악 프롬프트 - 최대 1000자)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (메타태그 포함 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "생성된 가사가 여기에 표시됩니다.", language="text")