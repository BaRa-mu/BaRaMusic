import streamlit as st
import time
import os

def render_tab2():
    # [데이터 영역: 절대 수정 금지]
    STYLES = ["극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", "고딕 호러 스타일", "화려한 바로크 풍", "초현실주의 예술", "잉크 워시 수묵화", "팝아트 스타일", "스팀펑크 비주얼", "부드러운 파스텔 톤", "빈티지 필름 사진", "Ukiyo-e 일본 판화 풍", "퓨처리즘 SF"]
    MOODS = ["웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어두운 비장미", "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한", "비극적이고 처절한", "기괴하고 독특한", "순수하고 깨끗한"]
    LIGHTINGS = ["시네마틱 골든아워", "부드러운 스튜디오 조명", "차가운 달빛 아래", "화려한 네온사인", "자연스러운 아침 햇살", "강렬한 스포트라이트", "신비로운 안개 조명", "촛불의 은은한 빛", "화산 불꽃의 반사", "역광(Rim Light) 효과", "하이키(High Key) 밝은 조명", "로우키(Low Key) 대비 조명", "창가로 비치는 사선 빛", "다채로운 오로라 광원", "심해의 푸른 빛", "눈부신 역광", "번쩍이는 번개 조명", "부드러운 무지개 광원"]
    CAMERAS = ["와이드 파노라마 뷰", "초근접 매크로 샷", "하늘에서 본 버즈아이 뷰", "바닥에서 본 웜즈아이 뷰", "인물 중심 아이레벨", "불안정한 더치 앵글", "어깨 너머 오버더숄더", "어안 렌즈 피쉬아이", "망원 렌즈 아웃포커싱", "깊은 피사계 심도", "로모그래피 감성 앵글", "안개가 낀 듯한 소프트 포커스", "역동적인 로우 앵글", "장엄한 하이 앵글", "시점 샷(POV)", "360도 전방위 샷", "틸트 쉬프트 미니어처 룩", "롱 테이크 시네마 뷰"]
    
    FONTS = ["Nanum Brush Script", "Nanum Pen Script", "Dokdo", "Black Han Sans", "Gungsuh", "Batang", "Jeju Myeongjo", "Cafe24 Surround", "Yanolja Yache", "Binggrae", "KOTRA HOPE", "Aggro", "HSS New Spring", "Gana Chocolate", "Bemin DoHyeon"]

    # [사이드바 설정]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 파일 업로드")
        audio_file = st.file_uploader("Browse files", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        # --- [제목 파싱 로직] ---
        if audio_file and (st.session_state.get('last_uploaded_file') != audio_file.name):
            fname = os.path.splitext(audio_file.name)[0]
            if "_" in fname:
                k, e = fname.split("_")[:2]
                st.session_state.k_title = k
                st.session_state.e_title = e
            else:
                st.session_state.k_title = fname
                st.session_state.e_title = fname
            st.session_state.last_uploaded_file = audio_file.name

        st.divider()
        st.subheader("🏷️ 이미지 제목 (입력)")
        k_title = st.text_input("한글 제목", value=st.session_state.get('k_title', ""), key="img_k_title_input")
        e_title = st.text_input("영어 제목", value=st.session_state.get('e_title', ""), key="img_e_title_input")
        
        st.divider()
        st.subheader("🎨 이미지 생성 상세 설정")
        sel_style = st.selectbox("🎭 화풍", STYLES, key="sel_style")
        sel_mood = st.selectbox("✨ 분위기", MOODS, key="sel_mood")
        sel_light = st.selectbox("💡 조명", LIGHTINGS, key="sel_light")
        sel_cam = st.selectbox("📹 카메라", CAMERAS, key="sel_cam")
        
        st.divider()
        st.subheader("🎬 쇼츠 이미지 구성")
        shorts_count = st.slider("쇼츠 이미지 개수 (0~5개)", 0, 5, 0, key="shorts_slider")
        
        st.divider()
        gen_btn = st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True)

    # --- [오른쪽 메인 영역 스타일 설정] ---
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={"&family=".join([f.replace(" ", "+") for f in FONTS])}&display=swap');
        
        .grey-screen {{
            width: 100%; height: 800px;
            background-color: #E0E0E0; border-radius: 15px;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            text-align: center; color: #555555;
        }}
        .image-container {{
            position: relative; width: 100%; border-radius: 10px; overflow: hidden; margin-bottom: 20px;
            background-color: #eee;
        }}
        .ratio-16-9 {{ aspect-ratio: 16 / 9; }}
        .ratio-9-16 {{ aspect-ratio: 9 / 16; max-width: 450px; margin: 0 auto; }}
        
        .overlay-title {{
            position: absolute; width: 100%; text-align: center;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            pointer-events: none;
        }}
        
        .download-btn {{
            position: absolute; top: 10px; right: 10px;
            opacity: 0; transition: 0.3s; z-index: 100;
            background: rgba(0,0,0,0.6); color: white; padding: 5px 10px; border-radius: 5px;
        }}
        .image-container:hover .download-btn {{ opacity: 1; }}
        </style>
    """, unsafe_allow_html=True)

    # --- [메인 로직 시작] ---
    if not st.session_state.get('img_gen_done') and not gen_btn:
        # [상태 0] 생성 전: 중앙 정렬 회색 화면
        st.markdown(f"""
            <div class="grey-screen">
                <div style="font-family: 'Aggro', cursive;">
                    <h1 style="font-size: 60px; margin: 0;">{k_title if k_title else '한글제목'}</h1>
                    <h2 style="font-size: 40px; margin-top: 20px;">{e_title if e_title else 'English Title'}</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        if gen_btn:
            with st.spinner("이미지 생성 중..."):
                time.sleep(2)
            st.session_state.img_gen_done = True

        # [상태 1] 생성 후 결과 출력
        def image_with_controls(label, id_key, ratio_class):
            st.subheader(label)
            
            # 각 이미지별 개별 설정바 (하단 배치)
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                k_f = st.selectbox(f"한글 폰트", FONTS, key=f"kf_{id_key}", index=11)
                k_s = st.slider(f"한글 크기", 10, 150, 60, key=f"ks_{id_key}")
            with col_c2:
                e_f = st.selectbox(f"영어 폰트", FONTS, key=f"ef_{id_key}", index=0)
                e_s = st.slider(f"영어 크기", 10, 100, 40, key=f"es_{id_key}")
            with col_c3:
                spacing = st.slider(f"간격", 0, 100, 20, key=f"sp_{id_key}")
            
            posX = st.slider(f"상하 위치 (%)", 0, 100, 50, key=f"py_{id_key}")
            
            # 이미지 컨테이너 출력
            st.markdown(f"""
                <div class="image-container {ratio_class}">
                    <div class="download-btn">⬇️ Download</div>
                    <img src="https://via.placeholder.com/1280x720.png?text={label}" style="width:100%;">
                    <div class="overlay-title" style="top: {posX}%; transform: translateY(-50%);">
                        <div style="font-family: '{k_f}'; font-size: {k_s}px; color: white; text-shadow: 2px 2px 4px #000;">{k_title}</div>
                        <div style="font-family: '{e_f}'; font-size: {e_s}px; color: white; text-shadow: 2px 2px 4px #000; margin-top: {spacing}px;">{e_title}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 1. 유튜브 메인 (16:9)
        image_with_controls("유튜브 메인 (16:9)", "main", "ratio-16-9")
        st.divider()

        # 2. 틱톡 고정 (9:16)
        image_with_controls("틱톡 (9:16)", "tiktok", "ratio-9-16")
        st.divider()

        # 3. 쇼츠 (16:9)
        if shorts_count > 0:
            for i in range(shorts_count):
                image_with_controls(f"쇼츠 #{i+1} (16:9)", f"shorts_{i}", "ratio-16-9")
