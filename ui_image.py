import streamlit as st
import time

def render_tab2():
    # [데이터 영역: 드롭다운 메뉴당 15개 이상 옵션 확보]
    STYLES = ["극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", "고딕 호러 스타일", "화려한 바로크 풍", "초현실주의 예술", "잉크 워시 수묵화", "팝아트 스타일", "스팀펑크 비주얼", "부드러운 파스텔 톤", "빈티지 필름 사진"]
    MOODS = ["웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어둡고 비장한", "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한"]
    LIGHTINGS = ["시네마틱 골든아워", "부드러운 스튜디오 조명", "차가운 달빛 아래", "화려한 네온사인", "자연스러운 아침 햇살", "강렬한 스포트라이트", "신비로운 안개 조명", "촛불의 은은한 빛", "화칸 불꽃의 반사", "역광(Rim Light) 효과", "하이키(High Key) 밝은 조명", "로우키(Low Key) 대비 조명", "창가로 비치는 사선 빛", "다채로운 오로라 광원", "심해의 푸른 빛"]
    CAMERAS = ["와이드 파노라마 뷰", "초근접 매크로 샷", "하늘에서 본 버즈아이 뷰", "바닥에서 본 웜즈아이 뷰", "인물 중심 아이레벨", "불안정한 더치 앵글", "어깨 너머 오버더숄더", "어안 렌즈 피쉬아이", "망원 렌즈 아웃포커싱", "깊은 피사계 심도", "로모그래피 감성 앵글", "안개가 낀 듯한 소프트 포커스", "역동적인 로우 앵글", "장엄한 하이 앵글", "시점 샷(POV)"]

    # [왼쪽 사이드바: 모든 설정 몰아넣기]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 파일 업로드")
        # 음원 파일 업로드 (Browse files)
        audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        st.divider()
        st.subheader("🏷️ 이미지 제목 입력")
        k_title = st.text_input("한글 제목", placeholder="예: 은혜의 아침", key="img_k_title_input")
        e_title = st.text_input("영어 제목", placeholder="예: Morning of Grace", key="img_e_title_input")
        
        st.divider()
        st.subheader("🎨 생성 상세 설정")
        sel_style = st.selectbox("🎭 화풍 선택", STYLES, key="sel_style")
        sel_mood = st.selectbox("✨ 분위기 선택", MOODS, key="sel_mood")
        sel_light = st.selectbox("💡 조명 연출", LIGHTINGS, key="sel_light")
        sel_cam = st.selectbox("📹 카메라 워킹", CAMERAS, key="sel_cam")
        
        st.divider()
        st.subheader("📱 쇼츠용 추가 생성 (16:9)")
        shorts_count = st.slider("쇼츠 이미지 개수 선택 (0-5개)", 0, 5, 3, key="shorts_slider")
        
        st.divider()
        # 이미지 생성 버튼 (음원 분석 포함)
        gen_btn = st.button("🚀 음원 분석 및 이미지 생성 시작", type="primary", use_container_width=True)

    # --- [메인 화면: 결과 출력] ---
    if gen_btn or st.session_state.get('img_gen_done'):
        if gen_btn:
            if not audio_file:
                st.error("⚠️ 음원 파일을 먼저 업로드해주세요.")
                return
            
            # 음원 분석 시뮬레이션
            with st.status("🎵 음원 주파수 및 분위기 분석 중...", expanded=True) as status:
                st.write("오디오 트랙 분석 중...")
                time.sleep(1.5)
                st.write(f"결과 반영: {sel_mood} 분위기 감지됨")
                time.sleep(1)
                st.write("이미지 생성 엔진 가동...")
                time.sleep(1.5)
                status.update(label="✅ 분석 및 생성 완료!", state="complete", expanded=False)
            
            st.session_state.img_gen_done = True

        # 1. 제목 출력 (따로따로 코드박스)
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.subheader("🇰🇷 한글 제목")
            st.code(k_title if k_title else "제목 없음", language="text")
        with col_t2:
            st.subheader("🇺🇸 영어 제목")
            st.code(e_title if e_title else "No_Title", language="text")

        st.divider()

        # 2. 고정 규격 이미지 생성 결과 (YouTube / TikTok)
        st.subheader("📺 메인 및 틱톡 규격 (고정)")
        col_img1, col_img2 = st.columns([16, 9])
        with col_img1:
            st.info("🖼️ YouTube 메인 (16:9)")
            st.image("https://via.placeholder.com/1280x720.png?text=Main+YouTube+16:9", use_container_width=True)
        with col_img2:
            st.info("📱 TikTok (9:16)")
            st.image("https://via.placeholder.com/720x1280.png?text=TikTok+9:16", use_container_width=True)

        st.divider()

        # 3. 쇼츠 규격 이미지 결과 (선택 개수만큼)
        if shorts_count > 0:
            st.subheader(f"🎬 쇼츠용 추가 이미지 (16:9, {shorts_count}개)")
            s_cols = st.columns(shorts_count)
            for i in range(shorts_count):
                with s_cols[i]:
                    st.image(f"https://via.placeholder.com/1280x720.png?text=Shorts+{i+1}", caption=f"Shorts Image {i+1}", use_container_width=True)
    else:
        st.info("👈 왼쪽 사이드바에서 음원을 업로드하고 설정을 마친 뒤 생성 버튼을 눌러주세요.")
