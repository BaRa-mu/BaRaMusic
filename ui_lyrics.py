import streamlit as st
import time
import utils

def render_tab1():
    st.header("📝 수노(Suno AI) 완벽 프롬프트 & 가사 생성기")
    
    # 왼쪽 메뉴칸을 작게(1), 오른쪽 결과물 칸을 넓게(2.5) 배치
    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        subject = st.text_input("🎯 곡의 주제/메시지", placeholder="예: 지친 하루의 위로")
        
        # 타겟 대상 선택 (이 선택에 따라 아래 장르와 분위기 메뉴가 바뀜)
        target = st.radio("🎯 타겟 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 타겟에 따른 장르 및 분위기 동적 변경
        if target == "대중음악":
            s_genre = st.selectbox("🎧 음악 장르", utils.suno_pop_list)
            pop_moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "어둡고 무거운", "몽환적인", "쓸쓸하고 우울한", "따뜻하고 포근한", "신비로운", "향수를 부르는", "사랑스러운", "흥겨운"]
            s_mood = st.selectbox("✨ 분위기", pop_moods)
        else:
            s_genre = st.selectbox("⛪ 음악 장르", utils.suno_ccm_list)
            ccm_moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬", "감성적인"]
            s_mood = st.selectbox("✨ 분위기", ccm_moods)

        # 기존 템포, 악기, 보컬 드롭메뉴는 원본 그대로 유지
        s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        s_vocal = st.selectbox("🎤 보컬", utils.suno_vocals_list)

        if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("AI 프롬프트 및 곡 구조를 계산 중입니다..."):
                time.sleep(0.8) # 생성 딜레이 연출
                
                # 1. 제목 생성 (한글_영어 조합 픽스, 괄호 중복 제거)
                short_subj = subject.split()[0] if subject else "은혜"
                if target == "대중음악":
                    st.session_state.gen_title_kr = f"{short_subj}의 노래"
                    st.session_state.gen_title_en = "Song of the Heart"
                else:
                    st.session_state.gen_title_kr = f"{short_subj}의 빛"
                    st.session_state.gen_title_en = "Light of Grace"

                # 2. 프롬프트 생성 (무조건 800자 이상 ~ 1000자 미만)
                # 메인 악기를 강조하고 나머지 세션은 AI가 알아서 채우도록 명령 포함
                prompt_blocks = [
                    f"Style & Genre: {s_genre} music. ",
                    f"Emotional Mood: {s_mood}. The overall atmosphere must perfectly capture the essence of '{subject}'. ",
                    f"Tempo & Rhythm: {s_tempo}. ",
                    f"Vocals: {s_vocal} delivering a deeply emotional, expressive, and dynamic performance. ",
                    f"Main Instrument Focus: The primary driving instrument is '{s_inst}'. ",
                    f"Session & Arrangement: The AI must automatically arrange and integrate appropriate background session instruments (such as subtle bass, drums, strings, pads, or synthesizers) that perfectly complement the main '{s_inst}' and elevate the {s_genre} style. ",
                    "Song Structure constraints: Total duration must be between 2 minutes 30 seconds and 8 minutes. ",
                    "Create a complete, fully arranged musical journey containing an [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Chorus], [Bridge], [Interlude], [Chorus], and [Outro]. ",
                    "Pacing constraints: Keep the Intro, Interlude, and Outro concise and impactful. Do not excessively drag out instrumental sections unless the thematic focus explicitly requires it. ",
                    "Production Quality: Billboard-charting studio quality, high fidelity, pristine mixing, wide stereo image, dynamic range spanning from intimate quiet moments to expansive grand climaxes. "
                ]
                
                # 800자를 넘기기 위한 고품질 디테일 묘사 추가
                detail_padding = (
                    "Ensure the transition between sections is smooth yet distinct. The Chorus should have a strong, memorable hook "
                    "and a fuller arrangement compared to the Verses. The Bridge should introduce a new chord progression "
                    "or a dynamic shift to build tension before the final explosive Chorus. The mixing should balance the "
                    "main vocal perfectly with the backing track, ensuring every lyric is understandable while the music "
                    "retains its full emotional power. Master the track to industry standards for optimal loudness, clarity, "
                    "and rhythmic groove. Pay special attention to the harmonic richness and spatial depth."
                )
                
                final_prompt = "".join(prompt_blocks) + detail_padding
                
                # 혹시 800자가 안 될 경우를 대비한 추가 패딩
                if len(final_prompt) < 800:
                    final_prompt += " Enhance the emotional resonance through careful dynamic automation and EQing."
                
                # 1000자 미만 컷
                st.session_state.gen_prompt = final_prompt[:995]

                # 3. 가사 생성 (2분 30초 ~ 8분 길이에 맞춘 풀버전, 전/간/후주 포함)
                st.session_state.gen_lyrics = f"""[Intro]
(간결하고 임팩트 있는 {s_inst} 전주)

[Verse 1]
조용히 눈을 감고 생각에 잠겨
{subject}의 의미를 되새겨보는 시간
바람에 스치는 작은 기억들마저
오늘따라 내 마음을 두드리네

[Pre-Chorus]
조금씩 선명해지는 저 빛을 향해
떨리는 두 손을 모아보네

[Chorus]
내 안에 가득 찬 이 마음을 노래해
어둠을 지나 마침내 찾은 이 길
아무리 먼 곳이라도 닿을 수 있게
나의 모든 걸 담아 부르리

[Verse 2]
때로는 흔들리고 넘어진다 해도
다시 일어설 힘이 내게 있으니
서툰 걸음으로 걷는 이 순간마저
소중한 나의 내일이 될 테니까

[Pre-Chorus]
조금씩 선명해지는 저 빛을 향해
떨리는 두 손을 모아보네

[Chorus]
내 안에 가득 찬 이 마음을 노래해
어둠을 지나 마침내 찾은 이 길
아무리 먼 곳이라도 닿을 수 있게
나의 모든 걸 담아 부르리

[Bridge]
수많은 날들이 지나고 변한다 해도
가슴 속 깊이 새겨진 이 마음은
영원히 꺼지지 않는 불꽃처럼
나를 숨 쉬게 하네

[Interlude]
(분위기를 고조시키는 짧은 {s_inst} 간주)

[Chorus]
내 안에 가득 찬 이 마음을 노래해
어둠을 지나 마침내 찾은 이 길
아무리 먼 곳이라도 닿을 수 있게
나의 모든 걸 담아 부르리

[Outro]
영원히 빛나리
(여운을 남기는 짧고 깔끔한 후주)"""

    # 오른쪽 결과물 출력 프레임 (넓은 영역)
    with right_col:
        if st.session_state.get('gen_title_kr'):
            st.write("### 📌 생성 결과물")
            
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / 길이: {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (전/간/후주 포함 풀버전 가사)**")
                # 가사가 길기 때문에 text_area를 써서 복사하기 쉽게 만듭니다.
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=400, label_visibility="collapsed")