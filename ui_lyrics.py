import streamlit as st
import re
import json
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

    # 기본 프롬프트 조합 (만약의 사태를 대비한 땜빵용)
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
            with st.spinner("AI가 프로 작사가 모드로 곡을 기획하고 있습니다... (약 10초 소요)"):
                
                # 🔥 AI가 딴소리를 절대 못하도록 강제하는 영문 마커 시스템
                query = f"""You are an award-winning lyricist and top-tier music producer.
Create a highly artistic, human-like song based on the following details.

Topic: {suno_subject}
Style: {s_selected_genre}, {s_mood}, {s_tempo}, {s_inst}, {s_vocal}

CRITICAL RULES:
1. AVOID AI cliches: Do NOT use obvious words like "희망의 빛", "새로운 시작", "함께 걸어가요". Write poetic, deeply emotional, and natural Korean lyrics.
2. You MUST format your ENTIRE response exactly using the 4 tags below. Do not add any other words, no greetings, no markdown formatting.

[TITLE_KR]
(Write ONE emotional Korean title here)
[TITLE_EN]
(Write the English translation of the title here)
[PROMPT]
(Write a highly detailed, 800 to 1000 character English prompt describing the genre, mood, rhythm, specific instruments, and vocal style. Use comma-separated keywords. No line breaks.)
[LYRICS]
(Write the full Korean lyrics here. Include tags like [Intro], [Verse 1], [Chorus], [Bridge], [Outro] appropriately.)
"""
                try:
                    # 🔥 가장 핵심: 이상한 JSON 암호문을 뱉는 딥시크 모델을 차단하고, 무조건 텍스트만 뱉는 'gpt-4o' 모델 강제 지정!
                    response = requests.post(
                        "https://text.pollinations.ai/",
                        json={
                            "messages": [{"role": "user", "content": query}],
                            "model": "gpt-4o" 
                        },
                        timeout=45
                    )
                    response.raise_for_status()
                    res_text = response.text
                    
                    # 🔥 2중 방어막: 혹시라도 AI 서버가 JSON 암호문을 보냈다면, 껍질을 까서 텍스트 알맹이만 빼냄
                    try:
                        data = json.loads(res_text)
                        if isinstance(data, dict):
                            if "content" in data: 
                                res_text = data["content"]
                            elif "choices" in data: 
                                res_text = data["choices"][0]["message"]["content"]
                    except:
                        pass # JSON이 아니면 정상적인 텍스트이므로 패스
                    
                    # AI가 쓸데없이 넣는 마크다운 기호 삭제
                    res_text = res_text.replace("**", "").replace("##", "")
                    
                    # 초기값 세팅
                    t_kr = "제목 생성 오류"
                    t_en = "TitleError"
                    prmpt = fallback_prompt
                    lyr = "가사를 생성하지 못했습니다."

                    # 🔥 완벽한 스플릿(Split) 파싱: 강제 마커를 기준으로 정확하게 텍스트를 쪼개서 담음
                    if "[TITLE_KR]" in res_text and "[TITLE_EN]" in res_text:
                        t_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip()
                    
                    if "[TITLE_EN]" in res_text and "[PROMPT]" in res_text:
                        t_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip()

                    if "[PROMPT]" in res_text and "[LYRICS]" in res_text:
                        prmpt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip().replace("\n", " ")
                        
                    if "[LYRICS]" in res_text:
                        lyr_raw = res_text.split("[LYRICS]")[1].strip()
                        # 끝부분에 AI가 덧붙이는 헛소리 방어
                        lyr = re.split(r'\n\s*(가사 포인트|참고:|Note:|설명:)', lyr_raw)[0].strip()

                    # 제목에 붙은 따옴표나 괄호 청소
                    t_kr = re.sub(r'[\"\'\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\"\'\[\]\(\)]', '', t_en).strip()
                    
                    # 화면에 보여줄 최종 데이터 세팅
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    st.session_state.final_prompt = prmpt[:995] if len(prmpt) > 10 else fallback_prompt
                    st.session_state.final_lyrics = lyr
                    
                    # 탭 2(이미지 팩토리) 연동을 위한 데이터 넘기기
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 생성 완료! 아래 우측 상단의 📋 아이콘을 눌러 수노(Suno AI)에 바로 붙여넣기 하세요.")
                
                except Exception as e:
                    st.error("⚠️ 서버 통신 장애가 발생했습니다. [생성] 버튼을 다시 한 번 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 각 박스 우측 상단에 마우스를 올리면 나타나는 **📋 (복사) 아이콘**을 누르세요. 수동 편집칸은 모두 제거되었습니다.")

    st.write("### 1. 🎵 Title (곡 제목)")
    st.code(st.session_state.final_title if st.session_state.final_title else "주제를 적고 생성 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (디테일 음악 프롬프트 - 최대 1000자)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (메타태그 포함 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "생성된 가사가 여기에 표시됩니다.", language="text")