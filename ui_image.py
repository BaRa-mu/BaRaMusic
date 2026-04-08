import streamlit as st
import time
import os

def render_tab2():
    # [데이터 영역: 각 드롭메뉴당 15개 이상 옵션]
    STYLES = ["극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", "고딕 호러 스타일", "화려한 바로크 풍", "초현실주의 예술", "잉크 워시 수묵화", "팝아트 스타일", "스팀펑크 비주얼", "부드러운 파스텔 톤", "빈티지 필름 사진", "Ukiyo-e 일본 판화 풍", "퓨처리즘 SF"]
    MOODS = ["웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어두운 비장미", "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한", "비극적이고 처절한", "기괴하고 독특한", "순수하고 깨끗한", "고딕풍의 신비함", "서정적인 노을빛"]
    LIGHTINGS = ["시네마틱 골든아워", "부드러운 스튜디오 조명", "차가운 달빛 아래", "화려한 네온사인", "자연스러운 아침 햇살", "강렬한 스포트라이트", "신비로운 안개 조명", "촛불의 은은한 빛", "화산 불꽃의 반사", "역광(Rim Light) 효과", "하이키(High Key) 밝은 조명", "로우키(Low Key) 대비 조명", "창가로 비치는 사선 빛", "다채로운 오로라 광원", "심해의 푸른 빛", "태양의 강렬한 직사광", "부드러운 구름 사이 빛", "도시의 가로등 불빛"]
    CAMERAS = ["와이드 파노라마 뷰", "초근접 매크로 샷", "하늘에서 본 버즈아이 뷰", "바닥에서 본 웜즈아이 뷰", "인물 중심 아이레벨", "불안정한 더치 앵글", "어깨 너머 오버더숄더", "어안 렌즈 피쉬아이", "망원 렌즈 아웃포커싱", "깊은 피사계 심도", "로모그래피 감성 앵글", "안개가 낀 듯한 소프트 포커스", "역동적인 로우 앵글", "장엄한 하이 앵글", "시점 샷(POV)", "360도 전방위 샷", "틸트 쉬프트 미니어처 룩", "롱 테이크 시네마 뷰", "클로즈업 바스트 샷", "광각 렌즈 왜곡 샷"]
    FONTS = ["Nanum Brush Script", "Nanum Pen Script", "Dokdo", "Black Han Sans", "Gungsuh", "Batang", "Jeju Myeongjo", "Cafe24 Surround", "Yanolja Yache", "Binggrae", "KOTRA HOPE", "Aggro", "HSS New Spring", "Gana Chocolate", "Bemin DoHyeon", "Gaegu", "Jua", "Yeon Sung"]

    # [사이드바 설정 및 파싱 로직]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 파일 업로드")
        # 음원 업로드 시 즉시 파싱하여 세션 스테이트에 반영
        audio_file = st.file_uploader("Browse files", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        if audio_file:
            fname = os.path.splitext(audio_file.name)[0]
            if "_" in fname:
                k, e = fname.split("_", 1)
                st.session_state['k_title_val'] = k
                st.session_state['e_title_val'] = e
            else:
                st.session_state['k_title_val'] = fname
                st.session_state['e_title_val'] = fname

        st.divider()
        st.subheader("🏷️ 이미지 제목 (자동 입력)")
        # 세션 스테이트 값을 불러와서 텍스트 박스에 강제 주입
        k_title = st.text_input("한글 제목", value=st.session_state.get('k_title_val', ""), key="img_k_title_input")
        e_title = st.text_input("영어 제목", value=st.session_state.get('e_title_val', ""), key="img_e_title_input")
        
        st.divider()
        st.subheader("🎨 이미지 생성 상세 설정")
        st.selectbox("🎭 화풍", STYLES, key="sel_style")
        st.selectbox("✨ 분위기", MOODS, key="sel_mood")
        st.selectbox("💡 조명", LIGHTINGS, key="sel_light")
        st.selectbox("📹 카메라", CAMERAS, key="sel_cam")
        
        st.divider()
        st.subheader("🎬 쇼츠 이미지 구성")
        shorts_count = st.slider("쇼츠 이미지 개수 (0~5개)", 0, 5, 0, key="shorts_slider")
        
        st.divider()
        gen_btn = st.button("🚀 이미지 생성 시작", type="primary", use_container_width=True)

    # --- [스타일 및 효과 설정] ---
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={"&family=".join([f.replace(" ", "+") for f in FONTS])}&display=swap');
        
        /* 미리보기 컨테이너: 긴 면 520px 고정 및 검은색 배경 */
        .preview-box {{
            position: relative;
            background-color: #000;
            margin: 0 auto 30px auto;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .ratio-16-9 {{ width: 520px; height: 292.5px; }}
        .ratio-9-16 {{ width: 292.5px; height: 520px; }}

        /* 제목 효과: 글로우 및 그림자 */
        .text-glow {{
            color: white;
            text-align: center;
            line-height: 1.2;
            pointer-events: none;
            text-shadow: 0 0 10px rgba(255,255,255,0.8), 2px 2px 4px rgba(0,0,0,0.9);
            z-index: 10;
        }}

        /* 호버 다운로드 버튼 */
        .download-overlay {{
            position: absolute;
            top: 15px; right: 15px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            opacity: 0;
            transition: 0.3s;
            cursor: pointer;
            z-index: 20;
        }}
        .preview-box:hover .download-overlay {{ opacity: 1; }}
        </style>
    """, unsafe_allow_html=True)

    # --- [오른쪽 메인 출력 영역] ---
    if not st.session_state.get('img_gen_done') and not gen_btn:
        # [상태: 생성 전] 검은색 중앙 정렬 미리보기
        st.markdown(f"""
            <div class="preview-box ratio-16-9">
                <div class="text-glow">
                    <div style="font-family: 'Aggro', cursive; font-size: 45px;">{k_title if k_title else '한글제목'}</div>
                    <div style="font-family: 'Nanum Pen Script', cursive; font-size: 28px; margin-top: 15px;">{e_title if e_title else 'English Title'}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        if gen_btn:
            with st.spinner("음원 분석 및 이미지 생성 중..."):
                time.sleep(1.5)
            st.session_state.img_gen_done = True

        # [상태: 생성 후] 실제 이미지 블록들
        def image_block(label, key_id, ratio_class):
            st.markdown(f"### {label}")
            
            # 조절 바 (사이드바 메뉴와 별개로 이미지 바로 위에 배치)
            with st.container():
                c1, c2, c3 = st.columns(3)
                with c1:
                    kf = st.selectbox("한글 폰트", FONTS, index=11, key=f"f1_{key_id}")
                    ks = st.slider("한글 크기", 10, 120, 50, key=f"s1_{key_id}")
                with c2:
                    ef = st.selectbox("영어 폰트", FONTS, index=1, key=f"f2_{key_id}")
                    es = st.slider("영어 크기", 10, 100, 30, key=f"s2_{key_id}")
                with c3:
                    py = st.slider("상하 위치", 0, 100, 50, key=f"y_{key_id}")
                    spacing = st.slider("제목 간격", 0, 80, 20, key=f"sp_{key_id}")

            # 이미지 출력 (긴 면 520px 준수)
            st.markdown(f"""
                <div class="preview-box {ratio_class}">
                    <div class="download-overlay">⬇️ Download</div>
                    <img src="https://via.placeholder.com/1280x720.png?text={label}" style="width:100%; height:100%; object-fit:cover;">
                    <div class="text-glow" style="position: absolute; top: {py}%; transform: translateY(-50%);">
                        <div style="font-family: '{kf}'; font-size: {ks}px;">{k_title}</div>
                        <div style="font-family: '{ef}'; font-size: {es}px; margin-top: {spacing}px;">{e_title}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.divider()

        # 규격별 렌더링
        image_block("유튜브 메인 (16:9)", "yt", "ratio-16-9")
        image_block("틱톡 (9:16)", "tk", "ratio-9-16")
        if shorts_count > 0:
            for i in range(shorts_count):
                image_block(f"쇼츠 #{i+1} (16:9)", f"sh_{i}", "ratio-16-9")
