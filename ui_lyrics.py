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
        
        # --- 🎤 보컬 선택 (버튼 스타일로 변경) ---
        st.divider()
        st.write("**🎤 보컬 유형 선택**")
        # 버튼형 선택을 위해 radio의 horizontal 옵션 사용
        vocal_type = st.radio(
            "보컬 카테고리", 
            ["경음악", "남자", "여자", "듀엣", "합창"], 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 각 카테고리별 20개 이상의 풍성한 리스트 (합창 10개)
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

        # 버튼 선택 결과에 따라 세부 드롭메뉴 표시
        if vocal_type == "남자":
            s_vocal = st.selectbox("👨‍🎤 남성 보컬 상세 스타일", male_vocals)
        elif vocal_type == "여자":
            s_vocal = st.selectbox("👩‍🎤 여성 보컬 상세 스타일", female_vocals)
        elif vocal_type == "듀엣":
            s_vocal = st.selectbox("🧑‍🤝‍🧑 듀엣 상세 스타일", duet_vocals)
        elif vocal_type == "합창":
            s_vocal = st.selectbox("👨‍👩‍👧‍👦 합창 상세 스타일", choir_vocals)
        else:
            s_vocal = "Instrumental"

        st.divider()

        if st.button("🚀 수노 전용 풀버전 생성", type="primary", use_container_width=True):
            if not subject: 
                st.error("주제를 먼저 입력해 주세요.")
                return
            
            with st.spinner("AI가 곡 구성을 설계 중입니다..."):
                time.sleep(0.5) 
                
                # 1. 제목 생성
                short_subj = subject.split()[0] if subject else "은혜"
                st.session_state.gen_title_kr = f"{short_subj}의 노래" if target=="대중음악" else f"{short_subj}의 은혜"
                st.session_state.gen_title_en = "Song of Heart" if target=="대중음악" else "Grace of Lord"

                # 2. 프롬프트 생성 (800~1000자 최적화)
                v_prompt = "Vocals: None. Pure Instrumental track." if s_vocal == "Instrumental" else f"Vocals: {s_vocal}."
                
                prompt_blocks = [
                    f"Create a professional {target} track. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. ",
                    f"{v_prompt} Main Instrument: Focus heavily on the '{s_inst}'. ",
                    "Arrangement: AI should automatically provide full session support (bass, drums, strings, etc.) that complements the main instrument. ",
                    "Structure: Include [Intro], [Verse 1], [Chorus], [Verse 2], [Chorus], [Bridge], [Interlude], [Chorus], [Outro]. ",
                    "Duration: 2:30 to 8:00 minutes. Keep transitions smooth and impactful. ",
                    "Quality: Studio grade, wide stereo, cinematic depth, high fidelity, polished mix. "
                ]
                
                padding = "Master this track for optimal clarity and emotional resonance. Ensure the arrangement dynamically builds toward the final chorus. Use professional audio engineering techniques to balance the soundscape perfectly. "
                final_p = "".join(prompt_blocks) + padding
                while len(final_p) < 850: final_p += "Enhance the spatial richness and harmonic balance. "
                st.session_state.gen_prompt = final_p[:995]

                # 3. 가사 생성 (경음악 여부 반영)
                if s_vocal == "Instrumental":
                    st.session_state.gen_lyrics = "[Intro]\n(전주)\n\n[Instrumental Section]\n(연주곡입니다)\n\n[Outro]\n(후주)"
                else:
                    st.session_state.gen_lyrics = f"[Intro]\n(짧은 {s_inst} 전주)\n\n[Verse 1]\n{subject}의 마음을 담아 노래해\n[Chorus]\n영원한 평안 속에 거하리\n[Verse 2]\n새로운 힘을 내게 주시네\n[Bridge]\n(간주 후 고조되는 부분)\n[Chorus]\n영원한 평안 속에 거하리\n[Outro]\n(깔끔한 후주)"

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
                st.write("**3. 📝 Lyrics (전/간/후주 포함)**")
                st.text_area("가사 복사", st.session_state.gen_lyrics, height=450, label_visibility="collapsed")
        else:
            st.info("👈 왼쪽 메뉴에서 설정을 마친 후 생성 버튼을 눌러주세요.")
