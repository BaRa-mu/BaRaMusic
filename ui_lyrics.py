import streamlit as st
import re
import requests
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

    # 기본 프롬프트 조합 (AI 실패 시 땜빵용)
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
            with st.spinner("AI가 곡을 기획하고 있습니다. 잠시만 기다려주세요... (약 10초 소요)"):
                
                # 🔥 가장 완벽하게 작동했던 '한국어 직설법' 지시문으로 롤백 및 강화!
                query = f"""다음 조건으로 노래를 작사하고 음악 스타일을 묘사해주세요.

[조건]
주제: {suno_subject}
장르: {s_selected_genre}
분위기: {s_mood}
템포: {s_tempo}
악기: {s_inst}
보컬: {s_vocal}

반드시 아래 [출력 양식]에 적힌 딱 4가지 항목만 출력하세요. 인사말, "가사 포인트", "작성 완료" 같은 부연 설명은 절대 금지합니다.

[출력 양식]
한글제목: (주제에 맞는 감성적인 한글 제목 딱 1개)
영문제목: (한글 제목의 영문 번역 딱 1개)
음악프롬프트: (장르, 분위기, 보컬, 악기 등을 포함하여 곡의 질감과 리듬을 영어로 묘사한 800자 분량의 매우 긴 영문 프롬프트. 쉼표로만 구분해서 작성)
가사:
[Intro]
(가사 내용)
[Verse 1]
(가사 내용)
[Chorus]
(가사 내용)
[Outro]
"""
                try:
                    # 🔥 앵무새 버그를 일으키던 JSON 방식을 버리고, 순수 텍스트(Plain Text) 전송 방식으로 완벽 패치!
                    response = requests.post(
                        "https://text.pollinations.ai/",
                        data=query.encode('utf-8'),
                        headers={'Content-Type': 'text/plain'},
                        timeout=45
                    )
                    response.raise_for_status()
                    res_text = response.text
                    
                    # 마크다운 찌꺼기 싹 제거
                    clean_text = res_text.replace("**", "").replace("##", "")
                    
                    t_kr = "제목 생성 오류"
                    t_en = "TitleError"
                    prmpt = fallback_prompt
                    lyr = "가사를 생성하지 못했습니다."

                    # 정규식으로 항목별 파싱
                    match_kr = re.search(r"한글제목:\s*([^\n]+)", clean_text)
                    match_en = re.search(r"영문제목:\s*([^\n]+)", clean_text)
                    match_prompt = re.search(r"음악프롬프트:\s*(.+?)(?=\n*가사:)", clean_text, re.DOTALL)
                    match_lyrics = re.search(r"가사:\s*(.*)", clean_text, re.DOTALL)

                    if match_kr: t_kr = match_kr.group(1).strip()
                    if match_en: t_en = match_en.group(1).strip()
                    
                    # 🔥 제목 앞뒤에 붙은 불필요한 따옴표, 괄호 완벽히 박멸
                    t_kr = re.sub(r'[\"\'\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\"\'\[\]\(\)]', '', t_en).strip()
                    
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    
                    if match_prompt and len(match_prompt.group(1).strip()) > 20:
                        raw_prompt = match_prompt.group(1).strip().replace("\n", " ")
                        st.session_state.final_prompt = raw_prompt[:995] # 1000자 초과 컷
                    else:
                        st.session_state.final_prompt = fallback_prompt

                    if match_lyrics:
                        lyr_raw = match_lyrics.group(1).strip()
                        # 뒤에 AI가 헛소리로 붙인 '가사 포인트' 같은 것들 자르기
                        lyr = re.split(r'\n\s*(가사 포인트|참고:|Note:|설명:)', lyr_raw)[0].strip()
                        st.session_state.final_lyrics = lyr
                    else:
                        st.session_state.final_lyrics = clean_text # 만약 파싱 다 실패하면 원문 통째로 뱉음

                    # 탭 2(이미지 팩토리) 연동용 세션 저장
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 생성 완료! 아래 📋 아이콘을 눌러 수노(Suno)에 바로 붙여넣기 하세요.")
                
                except Exception as e:
                    st.error("⚠️ AI 서버 응답이 지연되었습니다. [생성] 버튼을 한 번 더 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 우측 상단의 **📋 (복사) 아이콘**을 누르세요. 수동 편집칸은 모두 제거되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.final_title if st.session_state.final_title else "주제를 적고 생성 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (디테일 음악 프롬프트 - 최대 1000자)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (메타태그 포함 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "생성된 가사가 여기에 표시됩니다.", language="text")