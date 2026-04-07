import streamlit as st
import time
import utils
import random

def render_tab1():
    # --- [1] 초정밀 CSS: 박스 크기 축소 및 겹침 방지 ---
    st.markdown("""
        <style>
        /* 드롭다운/입력창 박스 높이 축소 및 내부 정렬 */
        div[data-baseweb="select"] > div, .stTextInput input {
            height: 30px !important;
            min-height: 30px !important;
            font-size: 13px !important;
            padding: 0px 10px !important;
            display: flex !important;
            align-items: center !important;
        }
        /* 위젯 라벨(제목) 크기 축소 및 박스와의 간격 정밀 조정 */
        .stSelectbox label, .stRadio label, .stTextInput label {
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #444 !important;
            margin-bottom: 2px !important; /* 겹침 방지를 위한 여백 */
            padding-top: 5px !important;
        }
        /* 위젯 그룹 간 수직 거리 밀착 */
        [data-testid="stVerticalBlock"] > div {
            margin-top: -10px !important;
        }
        /* 라디오 버튼 간격 및 상단 여백 조절 */
        div[role="radiogroup"] {
            gap: 12px !important;
            margin-top: 3px !important;
        }
        /* 구분선 마진 최소화 */
        hr { margin: 8px 0px !important; }
        /* 결과창 code 박스 상단 여백 제거 */
        .stCode { margin-top: -10px !important; }
        </style>
    """, unsafe_allow_html=True)

    # 화면 분할: 메뉴(1) : 결과물(2.5)
    left_col, right_col = st.columns([1, 2.5])
    
    with left_col:
        # 제목과 버튼 배치 (공간 효율 극대화)
        h_col, b_col = st.columns([0.7, 1.3])
        with h_col: st.write("### 📝 곡 설정")
        with b_col: 
            st.write("") # 버튼 위치 미세 조정
            gen_btn = st.button("🚀 수노 풀버전 생성", type="primary", use_container_width=True)

        subject = st.text_input("🎯 주제/메시지", placeholder="예: 주님과 함께하는 즐겁고 행복한 삶")
        
        # 가사 스타일 (인간적인 느낌을 위한 펜 옵션)
        lyric_styles = ["서정적인 (Lyrical)", "시적인 (Poetic)", "직설적인 (Direct)", "성경적인 (Biblical)", "현대적인 (Contemporary)", "감성적인 (Emotive)", "이야기하듯 (Storytelling)", "찬양 중심 (Worship)"]
        s_lyric_style = st.selectbox("✒️ 가사 스타일", lyric_styles)
        
        target = st.radio("🎯 카테고리", ["대중음악", "⛪ CCM"], horizontal=True)
        
        # 장르 및 분위기 동적 메뉴
        if target == "대중음악":
            s_genre = st.selectbox("🎧 장르", utils.suno_pop_list)
            moods = ["선택안함", "감성적인", "기쁘고 희망찬", "에너지 넘치는", "몽환적인", "따뜻하고 포근한", "사랑스러운", "흥겨운"]
        else:
            s_genre = st.selectbox("⛪ 장르", utils.suno_ccm_list)
            moods = ["선택안함", "경건하고 거룩한", "평화롭고 차분한", "웅장한", "결연하고 비장한", "치유되는", "따뜻하고 포근한", "기쁘고 희망찬"]
        s_mood = st.selectbox("✨ 분위기", moods)

        # 템포 및 악기 (한 줄 배치)
        col1, col2 = st.columns(2)
        with col1: s_tempo = st.selectbox("🎵 템포", utils.suno_tempo_list)
        with col2: s_inst = st.selectbox("🎸 메인 악기", utils.suno_inst_list)
        
        st.divider()
        st.write("**🎤 보컬 유형**")
        v_type = st.radio("보컬 유형", ["경음악", "남자", "여자", "듀엣", "합창"], horizontal=True, label_visibility="collapsed")
        
        # 보컬 상세 선택 (모든 20개 리스트 완벽 복구)
        if v_type == "남자":
            s_vocal = st.selectbox("👨‍🎤 스타일", ["감미로운 남성 팝 보컬", "허스키하고 짙은 호소력의 남성", "파워풀한 고음의 남성 락 보컬", "부드러운 어쿠스틱 인디 남성", "그루브 넘치는 R&B 남성", "중후하고 따뜻한 바리톤", "소울풀한 가스펠 남성 보컬", "맑고 청아한 미성의 남성", "거칠고 날것의 빈티지 락 보컬", "세련된 신스팝 남성 보컬", "나지막이 속삭이는 ASMR 스타일 보컬", "리드미컬한 힙합/랩 남성 보컬", "애절한 발라드 남성 보컬", "포크/컨트리 스타일의 담백한 남성", "뮤지컬 스타일의 드라마틱한 남성", "블루지하고 끈적한 남성 보컬", "시원하게 뻗어나가는 청량한 남성", "몽환적이고 리버브가 강한 남성", "재지(Jazzy)하고 여유로운 남성", "트렌디한 오토튠 스타일 남성 보컬"])
        elif v_type == "여자":
            s_vocal = st.selectbox("👩‍🎤 스타일", ["맑고 청아한 여성 팝 보컬", "호소력 짙은 파워 디바", "몽환적이고 공기 반 소리 반 여성 보컬", "허스키하고 매력적인 알앤비 여성", "따뜻하고 포근한 어쿠스틱 여성", "통통 튀는 상큼한 아이돌 보컬", "깊은 울림의 소울/가스펠 여성", "세련된 재즈 보컬", "폭발적인 고음의 락 보컬", "속삭이는 듯한 인디 포크 여성", "애절하고 감성적인 발라드 여성", "시원하고 청량한 썸머 팝 보컬", "다크하고 신비로운 일렉트로닉 여성", "우아하고 성악적인 소프라노", "나른하고 매혹적인 로파이 보컬", "강렬한 걸크러시 힙합 여성 보컬", "뮤지컬 주인공 같은 드라마틱한 여성", "빈티지 레트로 감성의 여성 보컬", "트렌디하고 리드미컬한 팝 여성", "웅장한 시네마틱 여성 보컬"])
        elif v_type == "듀엣":
            s_vocal = st.selectbox("🧑‍🤝‍🧑 스타일", ["아름다운 화음의 남녀 어쿠스틱 듀엣", "애절한 이별 감성의 남녀 발라드 듀엣", "파워풀한 남녀 가스펠 듀엣", "달콤하고 사랑스러운 로맨틱 듀엣", "그루비한 R&B 소울 듀엣", "남성 화음 보컬", "여성 팝 화음 보컬", "락 보컬 남녀 듀엣", "인디 감성 남녀 듀엣", "오페라/크로스오버 남녀 듀엣", "신나는 댄스 팝 남녀 듀엣", "뮤지컬 대화형 듀엣", "위로가 되는 포크 듀엣", "재지한 피아노 바 듀엣", "시네마틱 듀엣", "소년 소녀 풋풋한 듀엣", "남성 보컬 & 여성 코러스", "여성 보컬 & 남성 코러스", "앰비언트 보컬 듀엣", "가창력 대결 스타일 듀엣"])
        elif v_type == "합창":
            s_vocal = st.selectbox("👨‍👩‍👧‍👦 스타일", ["웅장한 대규모 성가대", "리드미컬한 가스펠 합창", "맑은 어린이 성가대", "중세 그레고리안 성가", "에픽 시네마틱 코러스", "따뜻한 교회 성가대", "앰비언트 코러스", "장엄한 오페라 합창", "청년 연합 찬양대", "몽환적 백그라운드 코러스"])
        else:
            s_vocal = "Instrumental"

    # --- [2] 오른쪽 결과물: 초강력 생성 엔진 탑재 ---
    with right_col:
        st.subheader("✨ 생성 결과물")
        if gen_btn:
            if not subject: 
                st.error("주제를 먼저 입력해 주세요."); return
            
            with st.spinner("가사와 완벽히 어우러지는 대곡을 설계 중..."):
                time.sleep(0.5)
                
                # 🎵 [로직 1] 가사 맥락을 읽는 리얼 제목 생성
                title_map = {
                    "기쁨": ("기쁨의 축제", "The Festival of Joy"),
                    "즐겁": ("즐거운 동행", "A Joyful Walk"),
                    "행복": ("참된 행복의 노래", "Song of True Bliss"),
                    "평안": ("고요한 평안 속에", "In Eternal Peace"),
                    "쉼": ("내 영혼의 쉼표", "A Rest for My Soul"),
                    "은혜": ("풍성한 주의 은혜", "Abundant Grace"),
                    "사랑": ("변치 않는 그 사랑", "Unfailing Love"),
                    "십자가": ("십자가의 길", "The Way of the Cross")
                }
                kr_t, en_t = ("나의 진실한 고백", "My Sincere Confession")
                for key, val in title_map.items():
                    if key in subject: kr_t, en_t = val; break
                
                st.session_state.gen_title_kr, st.session_state.gen_title_en = kr_t, en_t

                # 🎸 [로직 2] 800~1000자 초정밀 프롬프트
                p_base = f"Professional {target} production. Genre: {s_genre}. Mood: {s_mood}. Tempo: {s_tempo}. Vocals: {s_vocal}. Lead Instrument: {s_inst}. Style: {s_lyric_style}. Song Concept: {kr_t}. "
                engineering = "Ensure high-fidelity 4k audio quality, wide stereo field, and cinematic harmonic balance. The arrangement must be lead by the main instrument but supported by a full studio session (bass, drums, strings, pads) that dynamically builds toward a grand climax in the final chorus. Mastered for professional industry standards. "
                final_p = p_base + engineering
                while len(final_p) < 880: final_p += "Focus on professional transitions and spatial richness. "
                st.session_state.gen_prompt = final_p[:995]

                # 📝 [로직 3] 3~8분 분량의 풀버전 가사 (구조적 완성도)
                st.session_state.gen_lyrics = f"""[Intro]
({s_mood} 분위기를 담아 곡의 문을 여는 {s_inst}의 서정적인 전주)

[Verse 1]
창밖의 풍경이 잠시 멈춘 듯한 이 고요한 시간에
내 마음 깊은 곳에 간직해온 소중한 이야기를 꺼내어 봅니다
단순한 말들로는 다 채울 수 없는 커다란 이 고백
"{subject}"
이 문장 하나를 가슴에 품고 오늘 하루를 견디며 살아냈습니다
때로는 거친 바람이 나의 앞길을 차갑게 가로막아 서더라도
내 곁을 지켜주던 따스한 주의 온기가 다시 나를 일으켜 세우네요

[Pre-Chorus]
(가사 스타일: {s_lyric_style})
천천히 스며드는 은혜의 빛줄기를 따라서
잊고 지냈던 수많은 꿈들이 다시 숨을 쉬며 깨어납니다
이제는 두려움 없이 저 넓은 바다를 향해 내 영혼이 나아갑니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 영원히 머무르리
흔들리던 마음도, 차갑게 얼어붙은 모든 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 기쁨의 춤을 추며 노래하리

[Verse 2]
한 걸음 내딛는 삶의 모든 발자국 속에 새겨진 흔적들
어제보다 더 깊어진 소망의 뿌리를 내 가슴속에 내려봅니다
"{subject}"
그 약속의 마음이 내 삶의 나침반이 되어 나를 인도합니다
상처 입은 날개로 힘겹게 하늘을 날아오르던 아픈 어제는 가고
이제는 독수리처럼 저 높은 곳을 향해 비상할 새 힘을 얻습니다

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 영원히 머무르리
흔들리던 마음도, 차갑게 얼어붙은 모든 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 기쁨의 춤을 추며 노래하리

[Bridge]
시간의 강물이 굽이쳐 흐르고 세상의 모든 것이 변해가도
내 영혼에 깊이 새겨진 그 이름, 결코 꺼지지 않는 영원한 불꽃
(분위기를 최고조로 끌어올리며 웅장해지는 {s_inst} 솔로 연주)
나의 모든 호흡과 진심을 다해 거룩한 그 영광을 노래하노라

[Interlude]
({s_inst}가 폭발적으로 몰아치며 감정의 파동을 전달하는 간주)

[Chorus]
영원한 평안, 그 깊은 안식 속에 나 영원히 머무르리
흔들리던 마음도, 차갑게 얼어붙은 모든 두려움도
주의 너른 품 안에서 눈 녹듯 흔적 없이 사라지니
끝을 알 수 없는 그 사랑 속에 나 기쁨의 춤을 추며 노래하리

[Outro]
나 이제 주 안에서 참된 자유와 안식을 얻었네
"{subject}"
주의 영원하고도 아름다운 그 사랑의 품 안에서...
({s_inst}의 잔잔한 여운과 함께 평화롭게 페이드 아웃)"""

        # 결과 출력 영역
        if st.session_state.get('gen_title_kr'):
            with st.container(border=True):
                st.write("**1. 🎵 Title (한글_영어)**")
                st.code(f"{st.session_state.gen_title_kr}_{st.session_state.gen_title_en}")
            
            with st.container(border=True):
                st.write(f"**2. 🎸 Style of Music (프롬프트 / {len(st.session_state.gen_prompt)}자)**")
                st.code(st.session_state.gen_prompt)
            
            with st.container(border=True):
                st.write("**3. 📝 Lyrics (우측 상단 아이콘 클릭 시 복사)**")
                # 가사를 st.code로 감싸서 복사 기능을 활성화합니다.
                st.code(st.session_state.gen_lyrics, language="markdown")
        else:
            st.info("👈 왼쪽 메뉴에서 설정을 마친 후 상단 '생성' 버튼을 눌러주세요.")
