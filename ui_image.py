import streamlit as st
import time
import os

def render_tab2():
    # [1. 데이터 영역: 절대 수정 금지]
    # 드롭다운 옵션 15개 이상 확보
    STYLES = ["극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", "고딕 호러 스타일", "화려한 바로크 풍", "초 surrealism 예술", "잉크 워시 수묵화", "팝아트 스타일", "스팀펑크 비주얼", "부드러운 파스텔 톤", "빈티지 필름 사진", "Ukiyo-e 일본 판화 풍", "퓨처리즘 SF"]
    MOODS = ["웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어두운 비장미", "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한", "비극적이고 처절한", "기괴하고 독특한", "순수하고 깨끗한", "고딕풍의 신비함", "서정적인 노을빛"]
    LIGHTINGS = ["시네마틱 골든아워", "부드러운 스튜디오 조명", "차가운 달빛 아래", "화려한 네온사인", "자연스러운 아침 햇살", "강렬한 스포트라이트", "신비로운 안개 조명", "촛불의 은은한 빛", "화산 불꽃의 반사", "역광(Rim Light) 효과", "하이키(High Key) 밝은 조명", "로우키(Low Key) 대비 조명", "창가로 비치는 사선 빛", "다채로운 오로라 광원", "심해의 푸른 빛", "태양의 강렬한 직사광", "부드러운 구름 사이 빛", "도시의 가로등 불빛"]
    CAMERAS = ["와이드 파노라마 뷰", "초근접 매크로 샷", "하늘에서 본 버즈아이 뷰", "바닥에서 본 웜즈아이 뷰", "인물 중심 아이레벨", "불안정한 더치 앵글", "어깨 너머 오버더숄더", "어안 렌즈 피쉬아이", "망원 렌즈 아웃포커싱", "깊은 피사계 심도", "로모그래피 감성 앵글", "안개가 낀 듯한 소프트 포커스", "역동적인 로우 앵글", "장엄한 하이 앵글", "시점 샷(POV)", "360도 전방위 샷", "틸트 쉬프트 미니어처 룩", "롱 테이크 시네마 뷰", "클로즈업 바스트 샷", "광각 렌즈 왜곡 샷"]
    
    # 한글 폰트 미리보기 대응 리스트 (15개 이상, 실제 사용될 값)
    FONTS = ["Nanum Brush Script", "Nanum Pen Script", "Dokdo", "Black Han Sans", "Gungsuh", "Batang", "Jeju Myeongjo", "Cafe24 Surround", "Yanolja Yache", "Binggrae", "KOTRA HOPE", "Aggro", "HSS New Spring", "Gana Chocolate", "Bemin DoHyeon", "Gaegu", "Jua", "Yeon Sung"]

    # [2. 사이드바 설정 및 제목 파싱 로직]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 파일 업로드")
        audio_file = st.file_uploader("Browse files", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        # 파일명 파싱 즉시 반영 로직
        if audio_file and st.session_state.get('last_uploaded_audio') != audio_file.name:
            fname_base = os.path.splitext(audio_file.name)[0]
            if "_" in fname_base:
                k_parse, e_parse = fname_base.split("_", 1)
                st.session_state['sync_k_title'] = k_parse
                st.session_state['sync_e_title'] = e_parse
            else:
                st.session_state['sync_k_title'] = fname_base
                st.session_state['sync_e_title'] = fname_base
            st.session_state['last_uploaded_audio'] = audio_file.name

        st.divider()
        st.subheader("🏷️ 이미지 제목 (입력)")
        k_title = st.text_input("한글 제목", value=st.session_state.get('sync_k_title', ""), key="img_k_title_field")
        e_title = st.text_input("영어 제목", value=st.session_state.get('sync_e_title', ""), key="img_e_title_field")
        
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

    # --- [3. CSS 설정: 회색 배경, 긴 면 520px, 강력한 제목 효과] ---
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={"&family=".join([f.replace(" ", "+") for f in FONTS])}&display=swap');
        
        /* 미리보기 프레임: 긴 면 520px 고정 */
        .preview-container {{
            position: relative;
            background-color: #E0E0E0; /* 변경: 생성 전 회색 */
            margin: 0 auto 30px auto;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }}
        /* 16:9 규격 (유튜브 메인) */
        .dim-16-9 {{ width: 520px; height: 292.5px; }}
        /* 9:16 규격 (틱톡 & 숏츠) */
        .dim-9-16 {{ width: 292.5px; height: 520px; }}

        /* 제목 효과: 강력한 화이트 글로우 + 블랙 그림자 */
        .effect-text {{
            color: white;
            text-align: center;
            line-height: 1.1;
            pointer-events: none;
            z-index: 10;
            text-shadow: 
                0 0 15px rgba(255, 255, 255, 0.9), 
                0 0 30px rgba(255, 255, 255, 0.6), 
                3px 3px 5px rgba(0, 0, 0, 1), 
                -1px -1px 0 rgba(0,0,0,1);
        }}

        /* 호버 다운로드 버튼 */
        .hover-download-btn {{
            position: absolute;
            top: 15px; right: 15px;
            background: rgba(0,0,0,0.8);
            color: white; padding: 6px 12px; border-radius: 5px;
            font-size: 13px; opacity: 0; transition: 0.3s; cursor: pointer; z-index: 20;
        }}
        .preview-container:hover .hover-download-btn {{ opacity: 1; }}
        </style>
    """, unsafe_allow_html=True)

    # --- [4. 오른쪽 메인 화면 출력 영역] ---
    if not st.session_state.get('img_gen_done') and not gen_btn:
        # [상태: 생성 전] 회색 화면 중앙 정렬
        # 텍스트 효과는 회색 배경에서도 보이도록 유지
        st.markdown(f"""
            <div class="preview-container dim-16-9">
                <div class="effect-text">
                    <div style="font-family: 'Aggro', cursive; font-size: 48px;">{k_title if k_title else '한글제목'}</div>
                    <div style="font-family: 'Nanum Pen Script', cursive; font-size: 30px; margin-top: 20px;">{e_title if e_title else 'English Title'}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        if gen_btn:
            with st.spinner("이미지 생성 중..."): time.sleep(1.5)
            st.session_state.img_gen_done = True

        # [상태: 생성 후] 실제 이미지 블록
        def render_image_block(label, key_id, ratio_class):
            st.markdown(f"### {label}")
            
            # 개별 조절 바 영역
            with st.container():
                c1, c2, c3 = st.columns(3)
                with c1:
                    kf = st.selectbox("한글 폰트", FONTS, index=11, key=f"kf_{key_id}")
                    # [변경] 한글 미리보기 적용: 드롭다운 아래 폰트 미리보기 박스 배치
                    display_k_raw = k_title if k_title else '한글제목'
                    st.markdown(f'<div style="font-family: \'{kf}\', cursive; font-size: 1.1rem; color: white; background-color:#555; padding: 2px 5px; border-radius:3px; text-align:center;">미리보기: {display_k_raw}</div>', unsafe_allow_html=True)
                    ks = st.slider("한글 크기", 10, 110, 50, key=f"ks_{key_id}")
                with c2:
                    ef = st.selectbox("영어 폰트", FONTS, index=1, key=f"ef_{key_id}")
                    es = st.slider("영어 크기", 10, 100, 30, key=f"es_{key_id}")
                with c3:
                    py = st.slider("상하 위치 (%)", 0, 100, 50, key=f"py_{key_id}")
                    px = st.slider("좌우 위치 (%)", 0, 100, 50, key=f"px_{key_id}")
                spacing = st.slider("제목 간격", 0, 80, 20, key=f"sp_{key_id}")

            st.markdown(f"""
                <div class="preview-container {ratio_class}" style="background-color:#000;">
                    <div class="hover-download-btn">⬇️ Download</div>
                    <img src="https://via.placeholder.com/1280x720.png?text={label}" style="width:100%; height:100%; object-fit:cover;">
                    <div class="effect-text" style="position: absolute; left: {px}%; top: {py}%; transform: translate(-50%, -50%);">
                        <div style="font-family: '{kf}'; font-size: {ks}px;">{k_title}</div>
                        <div style="font-family: '{ef}'; font-size: {es}px; margin-top: {spacing}px;">{e_title}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.divider()

        # 규격별 출력
        render_image_block("유튜브 메인 (16:9)", "main_yt", "dim-16-9")
        render_image_block("틱톡 (9:16)", "fixed_tk", "dim-9-16")
        if shorts_count > 0:
            for i in range(shorts_count):
                render_image_block(f"쇼츠 #{i+1} (9:16)", f"sh_{i}", "dim-9-16")
