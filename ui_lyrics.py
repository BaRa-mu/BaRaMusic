import streamlit as st
import re
import json
import requests
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("옵션을 선택하고 생성 버튼을 누르면 수노(Suno)에 바로 복사할 수 있는 '풀버전' 가사와 프롬프트가 만들어집니다.")
    
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

    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    fallback_parts = []
    if s_selected_genre: fallback_parts.append(utils.extract_eng(s_selected_genre))
    if s_mood != "선택안함": fallback_parts.append(utils.extract_eng(s_mood))
    if s_tempo != "선택안함": fallback_parts.append(utils.extract_eng(s_tempo))
    if s_inst != "선택안함": fallback_parts.append(utils.extract_eng(s_inst))
    if s_vocal != "선택안함": fallback_parts.append(utils.extract_eng(s_vocal))
    fallback_prompt = ", ".join(fallback_parts)

    if 'final_title' not in st.session_state: st.session_state.final_title = ""
    if 'final_prompt' not in st.session_state: st.session_state.final_prompt = ""
    if 'final_lyrics' not in st.session_state: st.session_state.final_lyrics = ""

    if st.button("✨ 수노 전용 풀버전 제목/가사/프롬프트 완성", type="primary", use_container_width=True):
        if not suno_subject: 
            st.error("🎯 곡의 주제를 먼저 입력해주세요!")
        else:
            with st.spinner("구글 엔진 기반의 GPT-4o가 3~4분 분량의 대곡을 작사하고 있습니다... (약 15초 소요)"):
                
                # 🔥 AI에게 3~4분 분량의 아주 긴 가사를 쓰라고 강력하게 명령함
                query = f"""You are a professional award-winning lyricist. 
Write a LONG, FULL-LENGTH song (3-4 minutes duration) in Korean. 
Topic: {suno_subject}
Style: {s_selected_genre}, {s_mood}, {s_tempo}, {s_inst}, {s_vocal}

[CRITICAL RULES]
1. LENGTH: The song must be LONG. Verse 1, Verse 2, and Bridge must each have at least 6-8 lines.
2. STRUCTURE: Follow this structure: [Intro] -> [Verse 1] -> [Pre-Chorus] -> [Chorus] -> [Verse 2] -> [Pre-Chorus] -> [Chorus] -> [Bridge] -> [Chorus] -> [Outro].
3. QUALITY: Avoid AI cliches. Use poetic, deep, emotional, and human-like Korean expressions.
4. FORMAT: Output ONLY the 4 tags below. No conversational text, no JSON, no asterisks.

[TITLE_KR]
(Emotional Korean Title)
[TITLE_EN]
(English Translation of the title)
[PROMPT]
(A highly detailed, 800-1000 character English music prompt including genre, mood, specific instruments, rhythm, and vocal texture. Fill it with rich musical keywords.)
[LYRICS]
(The full-length Korean lyrics with Suno-style meta-tags)
"""
                try:
                    response = requests.post(
                        "https://text.pollinations.ai/",
                        json={
                            "messages": [{"role": "user", "content": query}],
                            "model": "gpt-4o",
                            "seed": random.randint(1, 99999)
                        },
                        timeout=60
                    )
                    response.raise_for_status()
                    res_text = response.text
                    
                    # 만약 JSON 응답이 올 경우를 대비한 필터링
                    try:
                        data = json.loads(res_text)
                        if isinstance(data, dict):
                            res_text = data.get("content", data.get("choices", [{}])[0].get("message", {}).get("content", res_text))
                    except: pass
                    
                    res_text = res_text.replace("**", "").replace("##", "")
                    
                    t_kr = "제목 생성 오류"; t_en = "TitleError"; prmpt = fallback_prompt; lyr = "가사 생성 실패"

                    # 완벽한 4단 분리 파싱
                    if "[TITLE_KR]" in res_text and "[TITLE_EN]" in res_text:
                        t_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip()
                    if "[TITLE_EN]" in res_text and "[PROMPT]" in res_text:
                        t_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip()
                    if "[PROMPT]" in res_text and "[LYRICS]" in res_text:
                        prmpt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip().replace("\n", " ")
                    if "[LYRICS]" in res_text:
                        lyr_raw = res_text.split("[LYRICS]")[1].strip()
                        lyr = re.split(r'\n\s*(가사 포인트|참고:|Note:|설명:)', lyr_raw)[0].strip()

                    t_kr = re.sub(r'[\"\'\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\"\'\[\]\(\)]', '', t_en).strip()
                    
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    st.session_state.final_prompt = prmpt[:995] if len(prmpt) > 50 else fallback_prompt
                    st.session_state.final_lyrics = lyr
                    
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 대곡의 작사가 완료되었습니다! 아래 📋 아이콘을 눌러 수노(Suno)에 복사하세요.")
                
                except Exception as e:
                    st.error("⚠️ 서버 통신 장애가 발생했습니다. 버튼을 한 번 더 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 각 박스 우측 상단의 **📋 (복사) 아이콘**을 누르세요.")

    st.write("### 1. 🎵 Title (곡 제목 - 한글_영문)")
    st.code(st.session_state.final_title if st.session_state.final_title else "생성 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (1000자 디테일 프롬프트)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else fallback_prompt, language="text")

    st.write("### 3. 📝 Lyrics (3~4분 분량 풀버전 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "가사가 여기에 표시됩니다.", language="text")