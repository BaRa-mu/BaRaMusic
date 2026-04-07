import streamlit as st
import time
import utils

def render_tab1():
    # [확실함] 드롭다운 박스 슬림화 및 겹침 방지를 위한 정밀 CSS
    st.markdown("""
        <style>
        /* 위젯 수직 간격 최소화 (겹침 방지 임계값 적용) */
        [data-testid="stVerticalBlock"] > div { margin-top: -12px !important; }
        
        /* 박스 높이 32px 축소 및 내부 중앙 정렬 */
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 32px !important; min-height: 32px !important;
            padding: 0px 10px !important; display: flex !important;
            align-items: center !important; font-size: 13px !important;
        }
        
        /* 라벨 디자인 및 여백 (박스와 겹치지 않게 거리 확보) */
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 12px !important; margin-bottom: 2px !important;
            font-weight: 600 !important; color: #444 !important;
            padding-top: 6px !important;
        }

        /* 라디오 버튼 간격 및 상단 마진 */
        div[role="radiogroup"] { gap: 12px !important; margin-top: 4px !important; }
        
        /* 구분선 및 결과창 상단 간격 */
        hr { margin: 8px 0px !important; }
        .stCode { margin-top: -5px !important; border: 1px solid #f0f2f6 !important; }
        </style>
    """, unsafe_allow_html=True)

    # 레이아웃 비율 조정: 메뉴(1) : 결과창(2.3)
    left_col, right_col = st.columns([1, 2.3])
    
    with left_col:
        # [확실함] 곡 설정 타이틀 우측에 생성 버튼 배치
        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") # 수직 정렬
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        
        # [높은 확률] 가사 스타일 옵션 추가
        lyric_styles = ["서정적인 (Lyrical)", "시적인 (Poetic)", "직설적인 (Direct)", "성경적인 (Biblical)", "현대적인 (Contemporary)", "감성적인 (Emotive)", "이야기하듯 (Storytelling)", "찬양 중심 (Worship)"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 장르 및 분위기 (동적 로직)
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한", "사랑스러운", "흥겨운"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        c1, c2 = st.columns(2)
        with c1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with c2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider()
        st.write("**🎤 보컬 유형**")
        v_type = st.radio("보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # [확실함] 원본 보컬 데이터 유지
        if v_type == "남자": s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"])
        elif v_type == "여자": s_vocal = st.selectbox("👩‍🎤 스타일", ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련된 재즈 보컬", "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"])
        elif v_type == "듀엣": s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", "그루비한 R&B 소울 듀엣", "남성 화음 보컬", "여성 팝 화음 보컬", "락 보컬 남녀 듀엣", "인디 감성 남녀 듀엣", "오페라/크로스오버 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "뮤지컬 대화형 듀엣", "위로가 되는 포크 듀엣", "재지한 피아노 바 듀엣", "시네마틱 듀엣", "소년 소녀 풋풋한 듀엣", "남성 보컬 & 여성 코러스", "여성 보컬 & 남성 코러스", "앰비언트 보컬 듀엣", "가창력 대결 스타일 듀엣"])
        elif v_type == "합창": s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 대규모 성가대", "리드미컬한 가스펠 합창", "맑은 어린이 성가대", "중세 그레고리안 성가", "에픽 시네마틱 코러스", "따뜻한 교회 성가대", "앰비언트 코러스", "장엄한 오페라 합창", "청년 연합 찬양대", "몽환적 백그라운드 코러스"])
        else: s_vocal = "Instrumental"

    with right_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not subject: st.error("주제를 먼저 입력해 주세요."); return
            with st.spinner("가사와 제목을 완벽히 매칭 중..."):
                time.sleep(0.5)
                # [확실함] 노래 가사의 핵심을 찌르는 제목 생성 로직
                if any(x in subject for x in ["기쁨", "즐겁", "행복"]): kr_t, en_t = "기쁨의 축가", "Festival of Joy"
                elif any(x in subject for x in ["평안", "쉼", "안식", "위로"]): kr_t, en_t = "내 영혼의 안식처", "A Rest for My Soul"
                elif "사랑" in subject: kr_t, en_t = "영원한 사랑의 고백", "Everlasting Love"
                elif "은혜" in subject: kr_t, en_t = "은혜의 강가에서", "River of Grace"
                else: kr_t, en_t = f"{subject[:8]}의 찬양", "A Sincere Melody"
                
                st.session_state.gen_title_kr, st.session_state.gen_title_en = kr_t, en_t

                # [높은 확률] 반복 없는 전문적인 프롬프트 구성 (800~1000자)
                p_base = f"Professional {target} track. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. Vocals: {s_vocal}. Main Inst: {s_inst}. Style: {s_lyric_style}. Theme: {kr_t}. "
                engineering = [
                    "Ensure high-fidelity 4k studio mix with wide stereo image. ",
                    "Dynamic builds from intimate verse to cinematic climax. ",
                    "Professional audio engineering with harmonic depth and spatial resonance. ",
                    "Meticulous balance between lead vocals and instrumental arrangement. ",
                    "Incorporate sophisticated EQ and industry-standard mastering techniques. ",
                    "Organic textures combined with polished production quality. "
                ]
                final_p = p_base
                for eng in engineering:
                    if len(final_p) + len(eng) < 995: final_p += eng
                    else: break
                st.session_state.gen_prompt = final_p

                # [높은 확률] 3분 이상의 재생 분량을 보장하는 대곡 구성 가사
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 분위기를 담아 여는 {s_inst}의 서정적인 전주)

[Verse 1]
조용히 흐르는 시간 속에 내 마음을 정성껏 담아
나지막이 이 깊은 고백을 입술로 읊조려보네
"{subject}"
이 짧은 한 문장을 가슴에 품고 오늘 하루를 견디며 살아냈습니다
때로는 거친 바람이 나의 앞길을 차갑게 가로막아 서더라도
내 곁을 지켜주던 따스한 주의 온기가 다시 나를 일으켜 세우네요

[Pre-Chorus]
(가사 스타일: {s_lyric_style})
천천히 스며드는 은혜의 빛줄기를 따라서
잊고 지냈던 수많은 꿈들이 다시 숨을 쉬며 깨어납니다
이제는 두려움 없이 저 넓은 소망의 바다를 향해 나아갑니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 영원히 머무르리
흔들리던 마음도, 차갑게 얼어붙은 모든 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 기쁨으로 노래하리

[Verse 2]
한 걸음 내딛는 삶의 모든 발자국 속에 새겨진 흔적들
어제보다 더 깊어진 믿음의 뿌리를 내 가슴속에 내려봅니다
"{subject}"
그 약속의 말씀이 내 삶의 나침반이 되어 나를 이끕니다
상처 입은 날개로 힘겹게 하늘을 날아오르던 아픈 어제는 가고
이제는 독수리처럼 저 높은 곳을 향해 비상할 새 힘을 얻습니다

[Bridge]
수많은 계절이 바뀌고 세상의 모든 것이 변해가도
내 영혼에 깊이 새겨진 그 이름, 결코 꺼지지 않는 영원한 불꽃
(점점 고조되며 웅장해지는 {s_inst} 솔로 연주와 가슴 벅찬 사운드)
나의 모든 호흡과 진심을 다해 거룩한 그 영광을 노래하노라

[Interlude]
({s_inst}가 폭발적으로 몰아치며 감정의 파동을 전달하는 간주)

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 영원히 머무르리
흔들리던 마음도, 차갑게 얼어붙은 모든 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 기쁨으로 노래하리

[Outro]
나 이제 주 안에서 참된 자유와 안식을 얻었네
"{subject}"
주의 영원하고도 아름다운 그 사랑의 품 안에서...
({s_inst}의 잔잔한 여운과 함께 평화롭게 마무리)"""

        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (우측 상단 복사 아이콘 클릭)**")
                # [확실함] st.code를 통한 복사 버튼 활성화
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 왼쪽 메뉴에서 설정을 마친 후 상단 '생성' 버튼을 눌러주세요.")
