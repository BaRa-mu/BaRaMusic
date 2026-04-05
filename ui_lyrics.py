import streamlit as st
import re
import json
import requests
import utils
import google.generativeai as genai

# 🔥 사용자 제공 구글 API 키
GOOGLE_API_KEY = "AIzaSyBSE1hRoUQwZ3mKjnWDTl4doOkEAP9r1jw"
genai.configure(api_key=GOOGLE_API_KEY)

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    st.write("구글의 최첨단 AI 엔진을 사용하여 3~4분 분량의 가사와 1000자 프롬프트를 생성합니다.")
    
    suno_subject = st.text_input("🎯 곡의 주제/메시지 (필수 입력, 예: 지친 하루의 위로, 십자가의 사랑)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: s_pop = st.selectbox("🎧 대중음악 장르 (CCM 선택 시 무시됨)", utils.suno_pop_list)
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
        if not suno_subject: 
            st.error("🎯 곡의 주제를 먼저 입력해주세요!")
        else:
            with st.spinner("AI 프로듀서가 최적의 모델을 찾아 접속 중입니다..."):
                
                query = f"""You are a professional award-winning lyricist. 
Write a LONG, FULL-LENGTH song (3-4 minutes duration) in Korean. 
Topic: {suno_subject}
Style: {s_selected_genre}, {s_mood}, {s_tempo}, {s_vocal}

[CRITICAL RULES]
1. LENGTH: The song must be LONG. Follow structure: [Intro] -> [Verse 1] -> [Pre-Chorus] -> [Chorus] -> [Verse 2] -> [Pre-Chorus] -> [Chorus] -> [Bridge] -> [Chorus] -> [Outro].
2. QUALITY: Avoid AI cliches. Use poetic, deep, emotional Korean.
3. PROMPT: Write a highly detailed, 800-1000 character English music prompt.
4. FORMAT: Output ONLY the 4 tags below.

[TITLE_KR] 한글제목
[TITLE_EN] English Title
[PROMPT] English detailed prompt
[LYRICS] Full lyrics
"""
                res_text = ""
                # 🔥 무적의 모델 자동 탐색 리스트 (작동하는 놈 하나는 무조건 걸립니다)
                model_candidates = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
                
                success = False
                for model_name in model_candidates:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(query)
                        res_text = response.text
                        if "[TITLE_KR]" in res_text:
                            success = True
                            break
                    except:
                        continue
                
                # 🔥 모든 구글 모델이 실패할 경우 (API 키 문제 등) -> 즉시 100% 작동하는 백업 엔진 가동!
                if not success:
                    try:
                        response = requests.post(
                            "https://text.pollinations.ai/",
                            json={"messages": [{"role": "user", "content": query}], "model": "gpt-4o"},
                            timeout=30
                        )
                        res_text = response.text
                        # 만약 JSON 응답일 경우 껍질 까기
                        try:
                            data = json.loads(res_text)
                            res_text = data.get("content", data.get("choices", [{}])[0].get("message", {}).get("content", res_text))
                        except: pass
                    except:
                        st.error("⚠️ 모든 AI 서버가 응답하지 않습니다. 잠시 후 다시 시도해주세요.")
                        st.stop()

                # --- 파싱 및 정제 시작 ---
                res_text = res_text.replace("**", "").replace("##", "")
                t_kr = "제목 생성 오류"; t_en = "TitleError"; prmpt = ""; lyr = "가사 생성 실패"

                try:
                    if "[TITLE_KR]" in res_text and "[TITLE_EN]" in res_text:
                        t_kr = res_text.split("[TITLE_KR]")[1].split("[TITLE_EN]")[0].strip()
                    if "[TITLE_EN]" in res_text and "[PROMPT]" in res_text:
                        t_en = res_text.split("[TITLE_EN]")[1].split("[PROMPT]")[0].strip()
                    if "[PROMPT]" in res_text and "[LYRICS]" in res_text:
                        prmpt = res_text.split("[PROMPT]")[1].split("[LYRICS]")[0].strip().replace("\n", " ")
                    if "[LYRICS]" in res_text:
                        lyr = res_text.split("[LYRICS]")[1].strip()

                    t_kr = re.sub(r'[\"\'\[\]\(\)]', '', t_kr).strip()
                    t_en = re.sub(r'[\"\'\[\]\(\)]', '', t_en).strip()
                    
                    st.session_state.final_title = f"{t_kr}_{t_en}"
                    st.session_state.final_prompt = prmpt[:995] if len(prmpt) > 20 else prmpt
                    st.session_state.final_lyrics = lyr
                    
                    # 탭 2 연동 데이터 저장
                    st.session_state.gen_title_kr = t_kr
                    st.session_state.gen_title_en = t_en
                    
                    st.success("🎉 AI가 최적의 경로를 찾아 생성을 완료했습니다!")
                except:
                    st.error("⚠️ AI 응답 형식이 깨졌습니다. 한 번 더 버튼을 눌러주세요.")

    st.divider()
    st.subheader("📋 수노(Suno) 전용 원클릭 복사존")
    st.info("💡 각 박스 우측 상단의 **📋 (복사) 아이콘**을 누르세요.")

    st.write("### 1. 🎵 Title (곡 제목 - 한글_영문)")
    st.code(st.session_state.final_title if st.session_state.final_title else "생성 버튼을 누르세요.", language="text")
    
    st.write("### 2. 🎸 Style of Music (1000자 디테일 프롬프트)")
    st.code(st.session_state.final_prompt if st.session_state.final_prompt else "옵션을 선택하고 생성하세요.", language="text")

    st.write("### 3. 📝 Lyrics (3~4분 분량 풀버전 가사)")
    st.code(st.session_state.final_lyrics if st.session_state.final_lyrics else "가사가 여기에 표시됩니다.", language="text")