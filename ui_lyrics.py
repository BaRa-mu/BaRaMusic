import streamlit as st

# [절대 보존] 가사 스타일 데이터 (각 15종 이상)
CCM_STYLES = ["묵상과 고백", "선포와 찬양", "회개와 결단", "동행과 인도", "십자가의 사랑", "성령의 임재", "소망과 위로", "경배와 영광", "제자의 길", "중보와 간구", "은혜의 강가", "어린이 찬양", "현대적 워십", "고전적 찬송가풍", "새벽녘 기도"]
POP_STYLES = ["애절한 이별", "풋풋한 첫사랑", "도시의 밤(City Pop)", "레트로 감성", "청춘의 꿈", "사회적 메시지", "힙합 스웨그", "일상의 소소함", "몽환적인 밤", "여행과 자유", "짝사랑의 고백", "계절의 변화", "서사적 스토리텔링", "치유와 힐링", "파티와 축제"]

def render_tab1():
    with st.sidebar:
        st.header("🎵 가사 생성 설정")
        genre = st.radio("📂 음악 장르", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
        style_list = CCM_STYLES if genre == "CCM" else POP_STYLES
        selected_style = st.selectbox(f"✨ {genre} 스타일 (15종+)", style_list, key="style_sel")
        
        subject = st.text_input("💡 핵심 키워드", key="l_subject")
        mood = st.selectbox("🌈 전체 무드", ["밝고 희망찬", "차분하고 정적인", "웅장하고 힘있는", "서정적인"], key="l_mood")
        user_input = st.text_area("📝 상세 내용", height=150, key="l_input")
        
        if st.button("🚀 AI 가사 생성 시작", type="primary", use_container_width=True):
            if user_input:
                with st.spinner("가사 작성 중..."):
                    st.session_state.gen_lyrics = f"[{genre} - {selected_style}]\n주제: {subject}\n\nAI가 생성한 가사 본문입니다..."
                    st.success("완료!")
            else: st.warning("내용을 입력하세요.")

    # 오른쪽 메인 출력
    st.title("✍️ 가사 결과물")
    if st.session_state.get('gen_lyrics'):
        st.session_state.gen_lyrics = st.text_area("📝 결과 편집", value=st.session_state.gen_lyrics, height=450, key="l_edit")
    else: st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
