import streamlit as st
import os

# --- [확실함] 1. 도메인별 가사 스타일 상수 데이터 (각 15종 이상) ---
CCM_STYLES = [
    "묵상과 고백", "선포와 찬양", "회개와 결단", "동행과 인도", "십자가의 사랑", 
    "성령의 임재", "소망과 위로", "경배와 영광", "제자의 길", "중보와 간구", 
    "은혜의 강가", "어린이 찬양", "현대적 워십", "고전적 찬송가풍", "새벽녘 기도"
]

POP_STYLES = [
    "애절한 이별", "풋풋한 첫사랑", "도시의 밤(City Pop)", "레트로 감성", "청춘의 꿈", 
    "사회적 메시지", "힙합 스웨그", "일상의 소소함", "몽환적인 밤", "여행과 자유", 
    "짝사랑의 고백", "계절의 변화", "서사적 스토리텔링", "치유와 힐링", "파티와 축제"
]

def render_tab1():
    # --- [확실함] 2. UI 겹침 방지 및 안전 압축 CSS ---
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div { margin-top: -10px !important; margin-bottom: 0px !important; }
        .stSelectbox label, .stTextInput label, .stTextArea label { 
            margin-bottom: 2px !important; /* 겹침 방지 최소 간격 */
            padding-top: 6px !important; 
            font-size: 12px !important; 
            font-weight: 600 !important;
        }
        div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
            height: 32px !important; min-height: 32px !important; font-size: 13px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.write("### ✍️ 가사 생성 상세 설정")
    
    # [책임 분리] 장르 선택 후 스타일 동적 바인딩
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        genre = st.radio("📂 음악 장르", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
    
    with row1_col2:
        style_list = CCM_STYLES if genre == "CCM" else POP_STYLES
        selected_style = st.selectbox(f"🎵 {genre} 스타일 (15종+)", style_list, key="style_sel")

    row2_col1, row2_col2 = st.columns([1, 1])
    with row2_col1:
        subject = st.text_input("💡 핵심 키워드", placeholder="예: 하나님의 사랑, 노을 지는 바다", key="l_subject")
    with row2_col2:
        mood = st.selectbox("🌈 전체적 무드", ["밝고 희망찬", "차분하고 정적인", "웅장하고 힘있는", "슬프고 서정적인"], key="l_mood")

    # 가사 입력창 (여백 개선)
    st.write(f"**현재 설정:** {genre} > {selected_style} ({mood})")
    user_input = st.text_area("📝 곡의 배경이나 가사에 담고 싶은 내용을 적어주세요.", 
                             height=150, 
                             key="l_input",
                             placeholder="구체적일수록 고품질 가사가 생성됩니다.")

    st.divider()
    
    if st.button("🚀 AI 가사 생성 시작", type="primary", use_container_width=True):
        if not user_input:
            st.warning("내용을 입력해야 가사를 만들 수 있습니다.")
            return
        
        with st.spinner("영감을 불러오는 중..."):
            # 실제 API 호출 전 프롬프트 구성 (구조적 결합)
            st.session_state.gen_lyrics = f"[{genre} - {selected_style}]\n주제: {subject}\n무드: {mood}\n\n(AI가 생성한 가사 본문...)"
            st.success("가사 생성이 완료되었습니다!")

    # 결과 편집 영역
    if st.session_state.get('gen_lyrics'):
        with st.container(border=True):
            st.session_state.gen_lyrics = st.text_area("📝 생성된 가사 편집", 
                                                      value=st.session_state.gen_lyrics, 
                                                      height=250, 
                                                      key="l_edit")
