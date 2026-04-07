import streamlit as st
import time
import utils

def render_tab1():
    # 왼쪽 메뉴칸을 작게(1), 오른쪽 결과물 칸을 넓게(2.5) 배치
    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        st.subheader("📝 곡 설정 (메뉴)")
        subject = st.text_input("🎯 곡의 주제/메시지", placeholder="예: 지친 하루의 위로")
        
        # 타겟 대상 선택
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
        
        # --- 🎤 보컬 상세 설정 (업그레이드 완료) ---
        st.divider()
        vocal_type = st.selectbox("🎤 보컬 형태", ["선택안함 (가사없는 경음악)", "남자", "여자", "듀엣", "합창"])
        
        male_vocals = [
            "감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", 
            "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", 
            "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", 
            "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", 
            "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"
        ]
        
        female_vocals = [
            "맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", 
            "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련되고 도도한 재즈 보컬", 
            "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", 
            "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", 
            "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"
        ]
        
        duet_vocals = [
            "아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", 
            "그루비한 R&B 소울 듀엣", "남성 2인조 화음 보컬", "여성 2인조 팝 화음 보컬", "에너제틱한 락 보컬 남녀 듀엣", 
            "인디 감성의 나른한 남녀 듀엣", "오페라/크로스오버 스타일 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "서로 주고받는 대화형 뮤지컬 듀엣", 
            "잔잔하고 위로가 되는 포크 듀엣", "재지한 피아노 바 감성의 듀엣", "어두운 분위기의 시네마틱 듀엣", "소년 소녀 느낌의 풋풋한 듀엣", 
            "메인 남성 보컬 & 여성 코러스 화음", "메인 여성 보컬 & 남성 코러스 화음", "신비로운 앰비언트 보컬 듀엣", "폭발적인 가창력 대결 스타일 듀엣"
        ]
        
        choir_vocals = [
            "웅장하고 홀리한 대규모 성가대", "파워풀하고 리드미컬한 흑인 가스펠 합창", "맑고 순수한 어린이 성가대", "신비로운 중세 그레고리안 성가", 
            "장엄하고 시네마틱한 에픽 코러스", "따뜻하고 대중적인 교회 성가대", "천상의 소리 같은 앰비언트 코러스", "강렬하고 비장한 오페라 합창", 
            "경쾌하고 희망찬 청년 연합 찬양대", "속삭이는 듯한 몽환적인 백그라운드 합창"
        ]

        # 선택한 카테고리에 맞춰 디테일 드롭메뉴 출력
        if vocal_type == "남자":
            s_vocal = st.selectbox("👨‍🎤 보컬 스타일 (남자)", male_vocals)
        elif vocal_type == "여자":
            s_vocal = st.selectbox("👩‍🎤 보컬 스타일 (여자)", female_vocals)
        elif vocal_type == "듀엣":
            s_vocal = st.selectbox("🧑‍🤝‍🧑 보컬 스타일 (듀엣)", duet_vocals)
        elif vocal_type == "합창":
            s_vocal = st.selectbox("👨‍👩‍👧‍👦 보컬 스타일 (합창)", choir_vocals)
        else:
            s_vocal = "Instrumental"

        st.divider()

        if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("AI 프롬프트 및 곡 구조를 계산 중입니다..."):
                time.sleep(0.5) 
                
                # 1. 제목 생성
                short_subj = subject.split()[0] if subject else "은혜"
                if target == "대중음악":
                    st.session_state.gen_title_kr = f"{short_subj}의 노래"
                    st.session_state.gen_title_en = "Song of the Heart"
                else:
                    st.session_state.gen_title_kr = f"{short_subj}의 은혜"
                    st.session_state.gen_title_en = "Grace of the Lord"

                # 2. 프롬프트 생성 (경음악 여부에 따른 보컬 지시어 분리)
                if s_vocal == "Instrumental":
                    vocal_prompt = "Vocals: None. This is a purely instrumental track. Absolutely no vocals, no singing, no voices. "
                else:
                    vocal_prompt = f"Vocals: {s_vocal} delivering a deeply emotional, expressive, and dynamic performance. "

                prompt_blocks = [
                    f"Create a high-quality {target} track. ",
                    f"Style & Genre: {s_genre} music. ",
                    f"Emotional Mood: {s_mood}. The overall atmosphere must perfectly capture the essence of '{subject}'. ",
                    f"Tempo & Rhythm: {s_tempo}. ",
                    vocal_prompt,
                    f"Main Instrument Focus: The primary driving instrument is '{s_inst}'. ",
                    f"Session & Arrangement: The AI must automatically arrange and integrate appropriate background session instruments that perfectly complement the main '{s_inst}' without overpowering the melody. ",
                    "Song Structure constraints: Total duration must be between 2 minutes 30 seconds and 8 minutes. ",
                    "Create a complete, fully arranged musical journey containing an [Intro], [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Chorus], [Bridge], [Guitar Solo / Interlude], [Chorus], and [Outro]. ",
                    "Pacing constraints: Keep the Intro, Interlude, and Outro concise and impactful. ",
                    "Production Quality: Billboard-charting studio quality, high fidelity, pristine mixing, wide stereo image. "
                ]
                
                # 800자 이상 확보용 디테일
                detail_padding = (
                    "Ensure the transition between sections is smooth yet distinct. The Chorus should have a strong, memorable hook "
                    "and a fuller arrangement compared to the Verses. The Bridge should introduce a new chord progression "
                    "or a dynamic shift to build tension before the final explosive Chorus. The mixing should balance the "
                    "lead elements perfectly with the backing track. Master the track to industry standards for optimal loudness, clarity, "
                    "and rhythmic groove. Pay special attention to the harmonic richness and spatial depth, allowing the "
                    "reverb and delay to create a massive soundscape."
                )
                
                final_prompt = "".join(prompt_blocks) + detail_padding
                while len(final_prompt) < 800:
                    final_prompt += " Enhance the emotional resonance through careful dynamic automation and EQing."
                st.session_state.gen_prompt = final_prompt[:995]

                # 3. 가사 생성 (경음악일 경우 가사를 뽑지 않음)
                if s_vocal == "Instrumental":
                    st.session_state.gen_lyrics = """[Intro]
(간결하고 임팩트 있는 전주)

[Instrumental]
(가사 없는 경음악 트랙입니다. 편안하게 연주를 감상하세요.)

[Outro]
(여운을 남기는 짧고 깔끔한 후주)"""
                else:
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

    # 오른쪽 결과물 출력 프레임
    with right_col:
        st.subheader("✨ 생성 결과물")
        if st.session_state.get('gen_title_kr'):
            
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / 길이: {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (전/간/후주 포함)**")
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=450, label_visibility="collapsed")
        else:
            st.info("👈 왼쪽에서 곡 설정을 마친 후 '수노 전용 풀버전 생성' 버튼을 눌러주세요.")
