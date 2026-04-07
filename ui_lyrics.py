import streamlit as st
import time
import utils

def render_tab1():
    # 메뉴칸(1)과 결과물 칸(2.5) 비율 유지
    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        st.subheader("📝 곡 설정 (메뉴)")
        subject = st.text_input("🎯 곡의 주제/메시지", placeholder="예: 지친 하루의 위로")
        
        # 타겟 카테고리 선택
        target = st.radio("🎯 타겟 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        if target == "대중음악":
            s_genre = st.selectbox("🎧 음악 장르", utils.suno_pop_list)
            pop_moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "어둡고 무거운", "몽환적인", "쓸쓸하고 우울한", "따뜻하고 포근한", "신비로운", "향수를 부르는", "사랑스러운", "흥겨운"]
            s_mood = st.selectbox("✨ 분위기", pop_moods)
        else:
            s_genre = st.selectbox("⛪ 음악 장르", utils.suno_ccm_list)
            ccm_moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬", "감성적인"]
            s_mood = st.selectbox("✨ 분위기", ccm_moods)

        s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        # --- 🎤 보컬 선택 (버튼 스타일) ---
        st.divider()
        st.write("**🎤 보컬 유형 선택**")
        vocal_type = st.radio(
            "보컬 카테고리", 
            ["경음악", "남자", "여자", "듀엣", "합창"], 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 보컬 리스트 데이터
        male_vocals = ["감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"]
        female_vocals = ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련되고 도도한 재즈 보컬", "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"]
        duet_vocals = ["아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", "그루비한 R&B 소울 듀엣", "남성 2인조 화음 보컬", "여성 2인조 팝 화음 보컬", "에너제틱한 락 보컬 남녀 듀엣", "인디 감성의 나른한 남녀 듀엣", "오페라/크로스오버 스타일 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "서로 주고받는 대화형 뮤지컬 듀엣", "잔잔하고 위로가 되는 포크 듀엣", "재지한 피아노 바 감성의 듀엣", "어두운 분위기의 시네마틱 듀엣", "소년 소녀 느낌의 풋풋한 듀엣", "메인 남성 보컬 & 여성 코러스 화음", "메인 여성 보컬 & 남성 코러스 화음", "신비로운 앰비언트 보컬 듀엣", "폭발적인 가창력 대결 스타일 듀엣"]
        choir_vocals = ["웅장하고 홀리한 대규모 성가대", "파워풀하고 리드미컬한 흑인 가스펠 합창", "맑고 순수한 어린이 성가대", "신비로운 중세 그레고리안 성가", "장엄하고 시네마틱한 에픽 코러스", "따뜻하고 대중적인 교회 성가대", "천상의 소리 같은 앰비언트 코러스", "강렬하고 비장한 오페라 합창", "경쾌하고 희망찬 청년 연합 찬양대", "속삭이는 듯한 몽환적인 백그라운드 합창"]

        if vocal_type == "남자": s_vocal = st.selectbox("👨‍🎤 남성 스타일", male_vocals)
        elif vocal_type == "여자": s_vocal = st.selectbox("👩‍🎤 여성 스타일", female_vocals)
        elif vocal_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 듀엣 스타일", duet_vocals)
        elif vocal_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 합창 스타일", choir_vocals)
        else: s_vocal = "Instrumental"

        st.divider()

        if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("AI가 3~8분 분량의 풀버전 곡을 설계 중입니다..."):
                time.sleep(0.8) 
                
                # 1. 제목 생성 (한글제목_영어제목)
                short_s = subject.split()[0]
                st.session_state.gen_title_kr = f"{subject}의 찬양" if target=="⛪ CCM" else f"{subject}의 노래"
                st.session_state.gen_title_en = f"Worship of {short_s}" if target=="⛪ CCM" else f"Song of {short_s}"

                # 2. 프롬프트 생성 (800~1000자, 메인악기 강조 및 상세 세션 지시)
                v_p = "Vocals: None. Pure Instrumental." if s_vocal == "Instrumental" else f"Vocals: {s_vocal}."
                prompt_blocks = [
                    f"Create a professional {target} track. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. ",
                    f"{v_p} Main Instrument Focus: The entire arrangement is led by the '{s_inst}'. ",
                    "Session Arrangement: AI must automatically generate professional background support including melodic bass, steady drums, lush strings, and atmospheric pads that perfectly balance with the main instrument. ",
                    "Structural Timing: This is a full-length song (minimum 3 minutes to 8 minutes). ",
                    "Structure: [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Chorus], [Bridge], [Instrumental Break/Solo], [Chorus], [Chorus], [Outro]. ",
                    "Pacing: Keep the Intro, Interlude, and Outro concise. Ensure dynamic builds between sections. ",
                    "Audio Quality: 4k studio quality, wide stereo image, high-fidelity production, pristine mixing and mastering. "
                ]
                padding = "Apply deep emotional resonance and cinematic spatial depth. The mixing should be industry-standard with clear vocal presence and harmonic richness. Enhance the final output with professional EQ and compression. "
                final_p = "".join(prompt_blocks) + padding
                while len(final_p) < 850: final_p += "Focus on professional arrangement and smooth transitions. "
                st.session_state.gen_prompt = final_p[:995]

                # 3. 가사 생성 (분량 대폭 보강 - 3분 이상 대응)
                if s_vocal == "Instrumental":
                    st.session_state.gen_lyrics = "[Intro]\n(짧고 임팩트 있는 전주)\n\n[Instrumental Section]\n(가사가 없는 연주곡입니다. 멜로디의 흐름에 몸을 맡기세요.)\n\n[Outro]\n(여운을 남기는 깔끔한 후주)"
                else:
                    st.session_state.gen_lyrics = f"""[Intro]
(간결한 {s_inst} 연주로 시작)

[Verse 1]
조용히 흐르는 시간 속에 내 마음을 담아
{subject}의 깊은 고백을 나지막이 읊조려보네
고단했던 하루의 끝에서 나를 기다려준
따스한 그 눈길이 오늘따라 유난히 그립구나
세상 소음에 가려진 작고 여린 나의 목소리
이제는 주님 앞에 모두 다 내려놓으려 하네

[Pre-Chorus]
조금씩 차오르는 은혜의 물결을 따라
기대어 쉴 곳을 찾아 조심스레 발을 내딛네

[Chorus]
영원한 평안 속에 나 거하리라
흔들리는 마음도 폭풍 같은 두려움도
주의 품 안에서 눈 녹듯 다 사라지니
끝없는 그 사랑 안에 나 영원히 노래하리

[Verse 2]
한 걸음 한 걸음 내딛는 삶의 모든 순간
{subject}의 마음이 내 안에 살아 숨 쉬게 하소서
지치고 상처 입은 나의 영혼을 어루만지사
새로운 힘을 얻어 다시 일어설 소망을 주시네
지나온 길 위의 눈물은 이제 기쁨이 되고
내일의 염려마저 소중한 축복으로 변하리

[Chorus]
영원한 평안 속에 나 거하리라
흔들리는 마음도 폭풍 같은 두려움도
주의 품 안에서 눈 녹듯 다 사라지니
끝없는 그 사랑 안에 나 영원히 노래하리

[Bridge]
수많은 계절이 바뀌고 세월이 흘러가도
변치 않는 그 약속 내 가슴 속에 새겨져
(점점 고조되며 웅장해지는 사운드)
마침내 빛나는 영광의 그날을 향해
나의 모든 열정을 다해 부르짖노라

[Interlude]
(고조된 분위기를 이어가는 열정적인 {s_inst} 간주)

[Chorus]
영원한 평안 속에 나 거하리라
흔들리는 마음도 폭풍 같은 두려움도
주의 품 안에서 눈 녹듯 다 사라지니
끝없는 그 사랑 안에 나 영원히 노래하리

[Outro]
나 이제 주님 안에서 참된 안식을 누리네
{subject}의 사랑 안에서...
(잔잔한 여운을 남기는 후주)"""

    # 오른쪽 결과물 출력 프레임
    with right_col:
        st.subheader("✨ 생성 결과물")
        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (전/간/후주 포함 풀버전)**")
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=500, label_visibility="collapsed")
        else:
            st.info("👈 왼쪽 메뉴에서 설정을 마친 후 생성 버튼을 눌러주세요.")
