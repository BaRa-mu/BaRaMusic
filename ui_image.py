import streamlit as st
import time
import os
import streamlit.components.v1 as components

def render_tab2():
    # [데이터 영역: 절대 수정 금지]
    STYLES = [
        "극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", 
        "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", 
        "고딕 호러 스타일", "화려한 바로크 풍", "초현실주의 예술", "잉크 워시 수묵화", "팝아트 스타일", 
        "스팀펑크 비주얼", "부드러운 파스텔 톤", "빈티지 필름 사진", "Ukiyo-e 일본 판화 풍", "퓨처리즘 SF"
    ]
    MOODS = [
        "웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어두운 비장미", 
        "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", 
        "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한",
        "비극적이고 처절한", "기괴하고 독특한", "순수하고 깨끗한"
    ]
    LIGHTINGS = [
        "시네마틱 골든아워", "부드러운 스튜디오 조명", "차가운 달빛 아래", "화려한 네온사인", "자연스러운 아침 햇살", 
        "강렬한 스포트라이트", "신비로운 안개 조명", "촛불의 은은한 빛", "화산 불꽃의 반사", "역광(Rim Light) 효과", 
        "하이키(High Key) 밝은 조명", "로우키(Low Key) 대비 조명", "창가로 비치는 사선 빛", "다채로운 오로라 광원", 
        "심해의 푸른 빛", "눈부신 역광", "번쩍이는 번개 조명", "부드러운 무지개 광원"
    ]
    CAMERAS = [
        "와이드 파노라마 뷰", "초근접 매크로 샷", "하늘에서 본 버즈아이 뷰", "바닥에서 본 웜즈아이 뷰", "인물 중심 아이레벨", 
        "불안정한 더치 앵글", "어깨 너머 오버더숄더", "어안 렌즈 피쉬아이", "망원 렌즈 아웃포커싱", "깊은 피사계 심도", 
        "로모그래피 감성 앵글", "안개가 낀 듯한 소프트 포커스", "역동적인 로우 앵글", "장엄한 하이 앵글", "시점 샷(POV)",
        "360도 전방위 샷", "틸트 쉬프트 미니어처 룩", "롱 테이크 시네마 뷰"
    ]
    
    # [데이터 영역: 각 드롭메뉴당 15개 이상 전문 옵션 확보]
    # (폰트 이름, Google Fonts CSS 이름)
    CURSIVE_FONTS = [
        ("나눔손글씨 붓", "Nanum Brush Script"), ("나눔손글씨 펜", "Nanum Pen Script"), 
        ("독도", "Dokdo"), ("검은고딕", "Black Han Sans"), ("궁서체", "Gungsuh"),
        ("바탕체", "Batang"), ("제주 명조", "Jeju Myeongjo"), ("가나초콜릿", "Gana Chocolate"),
        ("코트라 희망체", "KOTRA HOPE"), ("배민 도현체", "Bemin DoHyeon"), ("야놀자 야체", "Yanolja Yache"),
        ("카페24 써라운드", "Cafe24 Surround"), ("빙그레체", "Binggrae체"), ("경기천년제목", "Gyeonggi Title"),
        ("티몬 몬소리체", "Tmon Monsori"), ("어그로체", "Aggro"), ("HSS새로운봄", "HSS New Spring")
    ]
    # English Script Fonts for Title (Google Fonts)
    ENGLISH_SCRIPT_FONTS = [
        ("Great Vibes", "Great+Vibes"), ("Dancing Script", "Dancing+Script"), ("Pacifico", "Pacifico"),
        ("Rochester", "Rochester"), ("Playball", "Playball"), ("Allura", "Allura"),
        ("Courgette", "Courgette"), ("Tangerine", "Tangerine"), ("Parisienne", "Parisienne"),
        ("Cookie", "Cookie"), ("Sacramento", "Sacramento"), ("Pinyon Script", "Pinyon+Script"),
        ("Mr De Haviland", "Mr+De+Haviland"), ("Lovers Quarrel", "Lovers+Quarrel"), ("Clicker Script", "Clicker+Script")
    ]
    
    # [데이터 영역: 강력한 제목 효과 드롭다운 (15개 이상)]
    TEXT_EFFECTS = [
        "강렬한 네온 글로우", "고급진 금박 레터링", "몽환적인 스모크 효과", "세련된 하이라이트 그림자", "신비로운 오로라 광채",
        "투박한 잉크 워시", "화려한 바로크 보석", "도시적인 사이버펑크 그림자", "빈티지 필름 노이즈 그림자", "목가적인 수채화 그라데이션",
        "우아한 진주 펄 효과", "현대적인 3D 입체 텍스트", "긴박한 긴장감 넘치는 폰트", "담백하고 소박한 필기체", "슬프고 서정적인 수묵화 효과",
        "장엄하고 거룩한 합창단 효과", "신나는 에너제틱한 컬러 그라데이션"
    ]

    # 폰트 CSS 생성
    font_css = "".join([f"@import url('https://fonts.googleapis.com/css2?family={f[1]}&display=swap');" for f in CURSIVE_FONTS])
    font_css += "".join([f"@import url('https://fonts.googleapis.com/css2?family={f[1]}&display=swap');" for f in ENGLISH_SCRIPT_FONTS])

    # [왼쪽 사이드바: 기존 로직 절대 수정 금지]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 분석용 파일 업로드")
        # 음원 파일 업로드
        audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        # 파일명 파싱 로직 (파일명_English 형식 대응)
        parsed_k_title = ""
        parsed_e_title = ""
        
        if audio_file:
            # 확장자 제외 파일명 추출
            raw_fname = os.path.splitext(audio_file.name)[0]
            # 파일명이 '한글제목_영어제목' 형식일 경우 파싱
            if "_" in raw_fname:
                parts = raw_fname.split("_")
                parsed_k_title = parts[0]
                parsed_e_title = parts[1]
            else:
                # 구분자 없을 시 파일명을 그대로 사용
                parsed_k_title = raw_fname
                parsed_e_title = raw_fname
        
        st.divider()
        st.subheader("🏷️ 이미지 제목 (파싱 완료)")
        # 파싱된 값을 기본값으로 설정
        k_title = st.text_input("한글 제목", value=parsed_k_title, placeholder="파일명에서 자동 추출됨", key="img_k_title_input")
        e_title = st.text_input("영어 제목", value=parsed_e_title, placeholder="파일명에서 자동 추출됨", key="img_e_title_input")
        
        st.divider()
        st.subheader("🎨 이미지 생성 상세 설정")
        sel_style = st.selectbox("🎭 화풍 (Style)", STYLES, key="sel_style")
        sel_mood = st.selectbox("✨ 분위기 (Atmosphere)", MOODS, key="sel_mood")
        sel_light = st.selectbox("💡 조명 (Lighting)", LIGHTINGS, key="sel_light")
        sel_cam = st.selectbox("📹 카메라 (Camera)", CAMERAS, key="sel_cam")
        
        st.divider()
        st.subheader("🎬 쇼츠 이미지 구성 (16:9)")
        # 쇼츠용 이미지 개수 (16:9, 0~5개 선택)
        shorts_count = st.slider("쇼츠 이미지 개수 (0~5개 선택)", 0, 5, 3, key="shorts_slider")
        
        st.divider()
        gen_btn = st.button("🚀 음원 분석 및 이미지 생성 시작", type="primary", use_container_width=True)

    # --- [오른쪽 메인 화면: 결과 출력 커스텀 뜯어고치기] ---
    
    # 전역 폰트 및 제목 스타일 CSS (사이드바에 배치)
    with st.sidebar:
        st.divider()
        st.subheader("🛠️ 제목 스타일 전역 설정")
        t_color = st.color_picker("제목 색상", "#FFFFFF", key="title_color")
        b_color = st.color_picker("제목 배경 색상", "#000000", key="title_bg_color")
        b_opacity = st.slider("배경 투명도", 0, 100, 50, key="title_bg_opacity")
        t_bg_color = f"rgba({int(b_color[1:3],16)}, {int(b_color[3:5],16)}, {int(b_color[5:7],16)}, {b_opacity/100})"

    # CSS 함수: 각 이미지 블록에 적용될 스타일 (호버 다운로드, 제목 레이어링)
    def get_image_block_css(image_id, aspect_ratio):
        ratio_css = "16/9" if aspect_ratio == "16:9" else "9/16"
        return f"""
        <style>
            .image-block-{image_id} {{
                position: relative;
                width: 100%;
                aspect-ratio: {ratio_css};
                background-color: #eee;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 10px;
            }}
            .image-block-{image_id} img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            /* 다운로드 버튼 (호버 시 생성) */
            .download-btn-{image_id} {{
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: rgba(0,0,0,0.7);
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                opacity: 0;
                transition: opacity 0.3s;
                z-index: 20;
            }}
            .image-block-{image_id}:hover .download-btn-{image_id} {{
                opacity: 1;
            }}
            
            /* 제목 텍스트 오버레이 */
            .title-overlay-{image_id} {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                color: {t_color};
                background-color: {t_bg_color};
                padding: 10px;
                border-radius: 5px;
                z-index: 10;
                line-height: 1.2;
                display: flex;
                flex-direction: column;
            }}
        </style>
        """

    # 메인 로직 영역
    if gen_btn or st.session_state.get('img_gen_done'):
        if gen_btn:
            if not audio_file:
                st.error("⚠️ 음원 파일을 먼저 업로드해 주세요.")
                return
            
            # 음원 분석 및 생성 프로세스 시뮬레이션
            with st.spinner("🎵 업로드된 음원 주파수 분석 및 규격별 이미지 생성 중..."):
                time.sleep(2.0)
            st.session_state.img_gen_done = True

        # 메인/틱톡/쇼츠 규격 순으로 출력
        
        # 1. 유튜브 메인 (16:9)
        st.info("📺 YouTube 메인 (16:9)")
        col_main_img, col_main_ctrl = st.columns([16, 9])
        with col_main_img:
            # 제목 레이어링 CSS 로드
            components.html(font_css + get_image_block_css("main", "16:9") + f"""
                <div class="image-block-main">
                    <img src="https://via.placeholder.com/1280x720.png?text=YouTube+Main+16:9">
                    <button class="download-btn-main">⬇️ 다운로드</button>
                    <div class="title-overlay-main" id="title_main">
                        <span class="k-title-main" id="k_main">한글제목</span>
                        <span class="e-title-main" id="e_main">영어제목</span>
                    </div>
                </div>
            """, height=220)
            
        with col_main_ctrl:
            # **[핵심] 각 이미지 하단에 효과 선택 드롭메뉴 및 정밀 조절바 배치**
            with st.expander("🛠️ 메인 제목 및 스타일 정밀 조절바 (클릭)", expanded=False):
                # 한글 제목 설정
                st.subheader("🇰🇷 한글 제목 스타일")
                # 필기체 위주 15개 이상 폰트 세트
                k_font_main = st.selectbox("한글 폰트 (필기체 위주)", CURSIVE_FONTS, format_func=lambda f: f[0], key="k_font_main")
                k_size_main = st.slider("한글 제목 크기", 10, 100, 24, key="k_size_main")
                k_pos_x_main = st.slider("한글 제목 위치 (좌우)", 0, 100, 20, key="k_pos_x_main")
                k_pos_y_main = st.slider("한글 제목 위치 (상하)", 0, 100, 80, key="k_pos_y_main")
                
                # 영어 제목 설정
                st.subheader("🇺🇸 English Title Style")
                # English Script Fonts 세트
                e_font_main = st.selectbox("영어 폰트 (필기체 위주)", ENGLISH_SCRIPT_FONTS, format_func=lambda f: f[0], key="e_font_main")
                e_size_main = st.slider("영어 제목 크기", 10, 100, 18, key="e_size_main")
                e_pos_x_main = st.slider("영어 제목 위치 (좌우)", 0, 100, 20, key="e_pos_x_main")
                e_pos_y_main = st.slider("영어 제목 위치 (상하)", 0, 100, 70, key="e_pos_y_main")
                
                # **[핵심] 강력한 제목 효과 드롭메뉴 (15개 이상)**
                st.subheader("↔️ 제목 간격 및 공통 효과")
                title_spacing_main = st.slider("한글 영어 제목 간격", 0, 50, 10, key="title_spacing_main")
                main_effect = st.selectbox("✨ 강력한 제목 효과 선택", TEXT_EFFECTS, key="main_effect")
                
                # JS를 사용해 실시간 스타일 적용
                js_script = f"""
                    <script>
                        const parent = window.parent.document;
                        parent.getElementById('k_main').innerText = '{k_title}';
                        parent.getElementById('e_main').innerText = '{e_title}';
                        
                        parent.getElementById('k_main').style.fontFamily = "'{k_font_main[1]}', cursive";
                        parent.getElementById('k_main').style.fontSize = "{k_size_main}px";
                        parent.getElementById('k_main').style.left = "{k_pos_x_main}%";
                        parent.getElementById('k_main').style.top = "{k_pos_y_main}%";
                        
                        parent.getElementById('e_main').style.fontFamily = "'{e_font_main[1]}', cursive";
                        parent.getElementById('e_main').style.fontSize = "{e_size_main}px";
                        parent.getElementById('e_main').style.left = "{e_pos_x_main}%";
                        parent.getElementById('e_main').style.top = "{e_pos_y_main}%";
                        parent.getElementById('e_main').style.marginTop = "{title_spacing_main}px";
                    </script>
                """
                components.html(js_script, height=0)

        st.divider()

        # 2. 틱톡 (9:16)
        st.info("📱 틱톡 (9:16)")
        col_tiktok_img, col_tiktok_ctrl = st.columns([9, 16])
        with col_tiktok_img:
            components.html(font_css + get_image_block_css("tiktok", "9:16") + f"""
                <div class="image-block-tiktok">
                    <img src="https://via.placeholder.com/720x1280.png?text=TikTok+9:16">
                    <button class="download-btn-tiktok">⬇️ 다운로드</button>
                    <div class="title-overlay-tiktok" id="title_tiktok">
                        <span class="k-title-tiktok" id="k_tiktok">한글제목</span>
                        <span class="e-title-tiktok" id="e_tiktok">영어제목</span>
                    </div>
                </div>
            """, height=380)
            
        with col_tiktok_ctrl:
            # **[핵심] 틱톡 이미지에도 효과 선택 드롭메뉴 및 정밀 조절바 배치**
            with st.expander("🛠️ 틱톡 제목 및 스타일 정밀 조절바 (클릭)", expanded=False):
                # 한글 제목 설정
                st.subheader("🇰🇷 한글 제목 스타일")
                k_font_tiktok = st.selectbox("한글 폰트 (필기체 위주)", CURSIVE_FONTS, format_func=lambda f: f[0], key="k_font_tiktok")
                k_size_tiktok = st.slider("한글 제목 크기", 10, 100, 24, key="k_size_tiktok")
                k_pos_x_tiktok = st.slider("한글 제목 위치 (좌우)", 0, 100, 20, key="k_pos_x_tiktok")
                k_pos_y_tiktok = st.slider("한글 제목 위치 (상하)", 0, 100, 80, key="k_pos_y_tiktok")
                
                # 영어 제목 설정
                st.subheader("🇺🇸 English Title Style")
                e_font_tiktok = st.selectbox("영어 폰트 (필기체 위주)", ENGLISH_SCRIPT_FONTS, format_func=lambda f: f[0], key="e_font_tiktok")
                e_size_tiktok = st.slider("영어 제목 크기", 10, 100, 18, key="e_size_tiktok")
                e_pos_x_tiktok = st.slider("영어 제목 위치 (좌우)", 0, 100, 20, key="e_pos_x_tiktok")
                e_pos_y_tiktok = st.slider("영어 제목 위치 (상하)", 0, 100, 70, key="e_pos_y_tiktok")
                
                # 강력한 제목 효과 드롭메뉴
                st.subheader("↔️ 제목 간격 및 공통 효과")
                title_spacing_tiktok = st.slider("한글 영어 제목 간격", 0, 50, 10, key="title_spacing_tiktok")
                tiktok_effect = st.selectbox("✨ 강력한 제목 효과 선택", TEXT_EFFECTS, key="tiktok_effect")
                
                js_script_tiktok = f"""
                    <script>
                        const parent = window.parent.document;
                        parent.getElementById('k_tiktok').innerText = '{k_title}';
                        parent.getElementById('e_tiktok').innerText = '{e_title}';
                        
                        parent.getElementById('k_tiktok').style.fontFamily = "'{k_font_tiktok[1]}', cursive";
                        parent.getElementById('k_tiktok').style.fontSize = "{k_size_tiktok}px";
                        parent.getElementById('k_tiktok').style.left = "{k_pos_x_tiktok}%";
                        parent.getElementById('k_tiktok').style.top = "{k_pos_y_tiktok}%";
                        
                        parent.getElementById('e_tiktok').style.fontFamily = "'{e_font_tiktok[1]}', cursive";
                        parent.getElementById('e_tiktok').style.fontSize = "{e_size_tiktok}px";
                        parent.getElementById('e_tiktok').style.left = "{e_pos_x_tiktok}%";
                        parent.getElementById('e_tiktok').style.top = "{e_pos_y_tiktok}%";
                        parent.getElementById('e_tiktok').style.marginTop = "{title_spacing_tiktok}px";
                    </script>
                """
                components.html(js_script_tiktok, height=0)

        st.divider()

        # 3. 쇼츠 (16:9, N개)
        if shorts_count > 0:
            st.info(f"🎬 선택된 쇼츠용 이미지 (16:9, {shorts_count}개)")
            s_cols = st.columns(shorts_count)
            for i in range(shorts_count):
                with s_cols[i]:
                    block_id = f"shorts_{i}"
                    # 제목 레이어링 CSS 로드
                    components.html(font_css + get_image_block_css(block_id, "16:9") + f"""
                        <div class="image-block-{block_id}">
                            <img src="https://via.placeholder.com/1280x720.png?text=Shorts+{i+1}">
                            <button class="download-btn-{block_id}">⬇️ 다운로드</button>
                            <div class="title-overlay-{block_id}" id="title_{block_id}">
                                <span class="k-title-{block_id}" id="k_{block_id}">한글제목</span>
                                <span class="e-title-{block_id}" id="e_{block_id}">영어제목</span>
                            </div>
                        </div>
                    """, height=220)
                    
                    # **[핵심] 모든 쇼츠 이미지 개별 하단에도 효과 선택 드롭메뉴 및 정밀 조절바 배치**
                    with st.expander(f"🛠️ 쇼츠 #{i+1} 제목 및 스타일 정밀 조절바 (클릭)", expanded=False):
                        # 한글 제목 설정
                        st.subheader("🇰🇷 한글 제목 스타일")
                        k_font_s = st.selectbox("한글 폰트 (필기체 위주)", CURSIVE_FONTS, format_func=lambda f: f[0], key=f"k_font_s_{i}")
                        k_size_s = st.slider("한글 제목 크기", 10, 100, 24, key=f"k_size_s_{i}")
                        k_pos_x_s = st.slider("한글 제목 위치 (좌우)", 0, 100, 20, key=f"k_pos_x_s_{i}")
                        k_pos_y_s = st.slider("한글 제목 위치 (상하)", 0, 100, 80, key=f"k_pos_y_s_{i}")
                        
                        # 영어 제목 설정
                        st.subheader("🇺🇸 English Title Style")
                        e_font_s = st.selectbox("영어 폰트 (필기체 위주)", ENGLISH_SCRIPT_FONTS, format_func=lambda f: f[0], key=f"e_font_s_{i}")
                        e_size_s = st.slider("영어 제목 크기", 10, 100, 18, key=f"e_size_s_{i}")
                        e_pos_x_s = st.slider("영어 제목 위치 (좌우)", 0, 100, 20, key=f"e_pos_x_s_{i}")
                        e_pos_y_s = st.slider("영어 제목 위치 (상하)", 0, 100, 70, key=f"e_pos_y_s_{i}")
                        
                        # 강력한 제목 효과 드롭메뉴
                        st.subheader("↔️ 제목 간격 및 공통 효과")
                        title_spacing_s = st.slider("한글 영어 제목 간격", 0, 50, 10, key=f"title_spacing_s_{i}")
                        s_effect = st.selectbox("✨ 강력한 제목 효과 선택", TEXT_EFFECTS, key=f"s_effect_{i}")
                        
                        js_script_s = f"""
                            <script>
                                const parent = window.parent.document;
                                parent.getElementById('k_{block_id}').innerText = '{k_title}';
                                parent.getElementById('e_{block_id}').innerText = '{e_title}';
                                
                                parent.getElementById('k_{block_id}').style.fontFamily = "'{k_font_s[1]}', cursive";
                                parent.getElementById('k_{block_id}').style.fontSize = "{k_size_s}px";
                                parent.getElementById('k_{block_id}').style.left = "{k_pos_x_s}%";
                                parent.getElementById('k_{block_id}').style.top = "{k_pos_y_s}%";
                                
                                parent.getElementById('e_{block_id}').style.fontFamily = "'{e_font_s[1]}', cursive";
                                parent.getElementById('e_{block_id}').style.fontSize = "{e_size_s}px";
                                parent.getElementById('e_{block_id}').style.left = "{e_pos_x_s}%";
                                parent.getElementById('e_{block_id}').style.top = "{e_pos_y_s}%";
                                parent.getElementById('e_{block_id}').style.marginTop = "{title_spacing_s}px";
                            </script>
                        """
                        components.html(js_script_s, height=0)
    else:
        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
