import streamlit as st
import re
import utils
import google.generativeai as genai

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    
    # 🔑 구글 API 키 입력창
    st.info("💡 'Google AI Studio'에서 발급받은 Gemini API 키를 입력하세요.")
    user_api_key = st.text_input("🔑 구글 Gemini API 키 입력", type="password", help="키를 입력해야 가사 생성이 작동합니다.")

    st.divider()
    st.write("주제와 장르를 선택하면 3~4분 분량의 대곡 가사와 1000자 디테일 프롬프트를 생성합니다.")
    
    suno_subject = st.text_input("🎯 곡의 주제/메시지 (예: 새벽 기도 후 주님과 함께 걷는 길)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: s_pop = st.selectbox("🎧 대중음악 장르", utils.suno_pop_list)
    with col_s2: s_ccm = st.selectbox("⛪ CCM / 예배음악 장르", utils.suno_ccm_list)

    col_s3, col_s4, col_s5 = st.columns(3)
    with col_s3: s_mood = st.selectbox("✨ 곡의 분위기", utils.suno_moods_list)
    with col_s4: s_tempo = st.selectbox("🥁 템포 (속도)", utils.suno_tempo_list)
    with col_s5: s_vocal = st.selectbox("🎤 보컬 구성", [v for v in utils.suno_vocals_list if not v.startswith("---")])

    s_selected_genre = s_ccm if s_ccm != "선택안함" else (s_pop if s_pop != "선택안함" else "")
    
    # 세션 상태 초기화
    if 'final_title' not in st.session_state: st.session_state.final_title = ""
    if 'final_prompt' not in st.session_state: st.session_state.final_prompt = ""
    if 'final_lyrics' not in st.session_state: st.session_state.final_lyrics = ""

    if st.button("🚀 수노 전용 풀버전 제목/가사/프롬프트 생성", type="primary", use_container_width=True):
        if not user_api_key:
            st.error("⚠️ API 키를 먼저 입력해주세요!")
        elif not suno_subject: 
            st.error("🎯 곡의 주제를 입력해주세요!")
        else:
            with st.spinner("구글 고성능 AI(Gemini 2.0)가 대곡을 작사하고 있습니다..."):
                try:
                    # 1. API 설정
                    genai.configure(api_key=user_api_key)
                    
                    # 2. 리스트에서 확인된 gemini-2.0-flash 모델 강제 지정
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    query = f"""You are a professional award-winning lyricist and music producer. 
Write a LONG, FULL-LENGTH song (3-4 minutes) in Korean. 

Topic: {suno_subject}
Genre: {s_selected_genre}
Mood: {s_mood}
Tempo: {s_tempo}
Vocals: {s_vocal}

[INSTRUCTIONS]
1. TITLE: Create a poetic Korean title and its English translation.
2. LYRICS: Write at least 30-40 lines. Structure: [Intro] -> [Verse 1] -> [Pre-Chorus] -> [Chorus] -> [Verse 2] -> [Pre-Chorus] -> [Chorus] -> [Bridge] -> [Guitar Solo] -> [Chorus] -> [Outro].
3. PROMPT: Write an 800-1000 character English prompt. Describe instruments, rhythm, sound texture, and vocal emotion in extreme detail.
4. NO CLICHES: Do not use robotic phrases. Use deep, human-like emotional expressions.
5. FORMAT: Output ONLY the tags below.

[TITLE_KR] (Korean Title)
[TITLE_EN] (English Title)
[PROMPT] (English Prompt)
[LYRICS] (Full Lyrics)
"""
                    response = model.generate_content(query)
                    res_text = response.text.replace("**", "").replace("##", "")
                    
                    # 데이터 파싱
                    t_kr = "제목오류"; t_en = "TitleError"; prmpt = ""; lyr = "생성실패"

                    if "[TITLE_KR]" in res_text and "[TITLE_EN]" in res_text:
                        t_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip()
                    if "[TITLE_EN]" in res_text and "[PROMPT]" in res_text:
                        t_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip()
                    if "[PROMPT]" in res_text and "[LYRICS]" in res_text:
                        prmpt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip().replace("\n", " ")
                    if "[LYRICS]" in res_text:
                        lyr = res_text.split("[LYRICS]")[1].strip()

                    # 특수문자 제거 및 세션 저장
                    t_kr = re.sub(r'[\"\'\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\"\'\[\]\(\)]', '', t_en).strip()
                    
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    st.session_state.final_prompt = prmpt[:995]
                    st.session_state.final_lyrics = lyr
                    
                    # 이미지 탭 연동용
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 작사가 완료되었습니다! 아래 복사존에서 우측 상단 📋 아이콘을 눌러 복사하세요.")
                
                except Exception as e:
                    st.error(f"⚠️ 오류 발생: {e}")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 각 박스 우측 상단의 **📋 (복사) 아이콘**을 누르세요.")

    st.write("### 1. 🎵 Title (곡 제목 - 한글_영문)")
    st.code(st.session_state.final_title if st.session_state.final_title else "주제를 적고 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (1000자 디테일 프롬프트)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else "여기에 디테일 프롬프트가 표시됩니다.", language="text")

    st.write("### 3. 📝 Lyrics (3~4분 분량 풀버전 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "여기에 가사가 표시됩니다.", language="text")