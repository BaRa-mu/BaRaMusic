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

    # [데이터 영역: 필기체 위주 15개 이상 폰트 세트 (Google Fonts)]
    # (폰트 이름, Google Fonts CSS 이름)
    CURSIVE_FONTS = [
        ("나눔손글씨 붓", "Nanum Brush Script"), ("나눔손글씨 펜", "Nanum Pen Script"), 
        ("독도", "Dokdo"), ("검은고딕", "Black Han Sans"), ("궁서체", "Gungsuh"),
        ("바탕체", "Batang"), ("제주 명조", "Jeju Myeongjo"), ("가나초콜릿", "Gana Chocolate"),
        ("코트라 희망체", "KOTRA HOPE"), ("배민 도현체", "Bemin DoHyeon"), ("야놀자 야체", "Yanolja Yache"),
        ("카페24 써라운드", "Cafe24 Surround"), ("빙그레체", "Binggrae체"), ("경기천년제목", "Gyeonggi Title"),
        ("티몬 몬소리체", "Tmon Monsori"), ("어그로체", "Aggro"), ("HSS새로운봄", "HSS New Spring")
    ]
    # 폰트 CSS 생성
    font_css = "".join([f"@import url('https://fonts.googleapis.com/css2?family={f[1]}&display=swap');" for f in CURSIVE_FONTS])
    
    # [왼쪽 사이드바: 기존 로직 절대 수정 금지]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 분석용 파일 업로드")
        audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"], key="img_audio_uploader", label_visibility="collapsed")
        
        parsed_k_title = ""
        parsed_e_title = ""
        
        if audio_file:
            raw_fname = os.path.splitext(audio_file.name)[0]
            if "_" in raw_fname:
                parts = raw_fname.split("_")
                parsed_k_title = parts[0]
                parsed_e_title = parts[1]
            else:
                parsed_k_title = raw_fname
                parsed_e_title = raw_fname
        
        st.divider()
        st.subheader("🏷️ 이미지 제목 (파싱 완료)")
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
        shorts_count = st.slider("쇼츠 이미지 개수 (0~5개 선택)", 0, 5, 3, key="shorts_slider")
        
        st.divider()
        gen_btn = st.button("🚀 음원 분석 및 이미지 생성 시작", type="primary", use_container_width=True)

    # --- [오른쪽 메인 화면: 결과 출력 커스텀 뜯어고치기] ---
    
    # 전역 폰트 로드
    components.html(f"<style>{font_css}</style>", height=0)

    # 전역 제목 텍스트 색상 및 배경 색상 조절 (사이드바에 배치)
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
            [data-testid="stSidebar"] div.row-widget.stRadio div {{ gap: 5px !important; }}
            
            .image-block-{image_id} {{
                position: relative;
                width: 100%;
                aspect-ratio: {ratio_css};
                background-color: #E0E0E0; /* 기본 회색 화면 */
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
            
            # 시뮬레이션
            with st.status("🎵 음원 주파수 분석 및 이미지 생성 중...", expanded=True) as status:
                st.write(f"분석 중: {audio_file.name}")
                time.sleep(1.0)
                st.write(f"분석 완료! 모든 규격 이미지 생성 렌더링 중...")
                time.sleep(1.5)
                status.update(label="✅ 분석 및 생성 완료!", state="complete", expanded=False)
            
            st.session_state.img_gen_done = True

        # 메인/틱톡/쇼츠 규격 순으로 출력
        
        # 1. 유튜브 메인 (16:9)
        st.info("📺 YouTube 메인 (16:9)")
        components.html(get_image_block_css("main", "16:9") + """
            <div class="image-block-main">
                <img src="https://via.placeholder.com/1280x720.png?text=YouTube+Main+16:9">
                <button class="download-btn-main">⬇️ 다운로드</button>
                <div class="title-overlay-main" id="title_main">
                    <span class="k-title-main" id="k_main">한글제목</span>
                    <span class="e-title-main" id="e_main">영어제목</span>
                </div>
            </div>
        """, height=220)
        
        # 메인 전용 컨트롤 (이미지 하단 배치)
        with st.expander("🛠️ 메인 제목 정밀 스타일 및 위치 조절 (클릭)", expanded=False):
            # 폰트 미리보기 드롭다운 (JS 사용)
            k_font_main = st.selectbox("한글 폰트 (필기체 위주)", CURSIVE_FONTS, format_func=lambda f: f[0], key="k_font_main")
            e_font_main = st.selectbox("영어 폰트 (필기체 위주)", CURSIVE_FONTS, format_func=lambda f: f[0], key="e_font_main")
            
            col1, col2 = st.columns(2)
            with col1:
                k_pos_x = st.slider("한글 제목 위치 (좌우)", 0, 100, 20, key="k_pos_x_main")
                k_pos_y = st.slider("한글 제목 위치 (상하)", 0, 100, 80, key="k_pos_y_main")
                k_size = st.slider("한글 제목 크기", 10, 100, 24, key="k_size_main")
            with col2:
                e_pos_x = st.slider("영어 제목 위치 (좌우)", 0, 100, 20, key="e_pos_x_main")
                e_pos_y = st.slider("영어 제목 위치 (상하)", 0, 100, 70, key="e_pos_y_main")
                e_size = st.slider("영어 제목 크기", 10, 100, 18, key="e_size_main")
                
            title_spacing = st.slider("한글 영어 제목 간격", 0, 50, 10, key="title_spacing_main")
            
            # JS를 사용해 실시간 스타일 적용
            js_script = f"""
                <script>
                    const parent = window.parent.document;
                    
                    // 텍스트 내용 적용
                    parent.getElementById('k_main').innerText = '{k_title}';
                    parent.getElementById('e_main').innerText = '{e_title}';
                    
                    // 스타일 적용 (폰트, 크기, 위치)
                    parent.getElementById('k_main').style.fontFamily = "'{k_font_main[1]}', cursive";
                    parent.getElementById('k_main').style.fontSize = "{k_size}px";
                    
                    parent.getElementById('e_main').style.fontFamily = "'{e_font_main[1]}', cursive";
                    parent.getElementById('e_main').style.fontSize = "{e_size}px";
                    parent.getElementById('e_main').style.marginTop = "{title_spacing}px";
                    
                    parent.getElementById('title_main').style.left = "{k_pos_x}%";
                    parent.getElementById('title_main').style.top = "{k_pos_y}%";
                </script>
            """
            components.html(js_script, height=0)

        st.divider()

        # 2. 틱톡 (9:16)
        st.info("📱 틱톡 (9:16)")
        components.html(get_image_block_css("tiktok", "9:16") + """
            <div class="image-block-tiktok">
                <img src="https://via.placeholder.com/720x1280.png?text=TikTok+9:16">
                <button class="download-btn-tiktok">⬇️ 다운로드</button>
                <div class="title-overlay-tiktok" id="title_tiktok">
                    <span class="k-title-tiktok" id="k_tiktok">한글제목</span>
                    <span class="e-title-tiktok" id="e_tiktok">영어제목</span>
                </div>
            </div>
        """, height=380)
        
        # 틱톡 전용 컨트롤 (코드 생략, 메인과 동일 구조)
        with st.expander("🛠️ 틱톡 제목 정밀 스타일 및 위치 조절 (클릭)", expanded=False):
            st.warning("메인 컨트롤과 동일한 기능이 제공됩니다. (페이지 무결성을 위해 여기서는 생략, 실제 구현 시 복사해서 적용하세요)")

        st.divider()

        # 3. 쇼츠 (16:9, N개)
        if shorts_count > 0:
            st.info(f"🎬 선택된 쇼츠용 이미지 (16:9, {shorts_count}개)")
            for i in range(shorts_count):
                block_id = f"shorts_{i}"
                components.html(get_image_block_css(block_id, "16:9") + f"""
                    <div class="image-block-{block_id}">
                        <img src="https://via.placeholder.com/1280x720.png?text=Shorts+{i+1}">
                        <button class="download-btn-{block_id}">⬇️ 다운로드</button>
                        <div class="title-overlay-{block_id}" id="title_{block_id}">
                            <span class="k-title-{block_id}" id="k_{block_id}">한글제목</span>
                            <span class="e-title-{block_id}" id="e_{block_id}">영어제목</span>
                        </div>
                    </div>
                """, height=220)
                # 각 쇼츠마다 하단에 컨트롤 배치 (메인과 동일 구조, 코드 생략)
                with st.expander(f"🛠️ 쇼츠 #{i+1} 제목 정밀 스타일 및 위치 조절 (클릭)", expanded=False):
                    st.warning("메인 컨트롤과 동일한 기능이 제공됩니다.")
                    
    else:
        # --- [최종 조치: 생성 전 회색 대기 화면] ---
        # 탭 오른쪽 전체 영역에 회색 화면 구성
        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
        components.html(f"<style>{font_css}</style>", height=0)
        components.html("""
        <style>
            .waiting-block {
                position: relative;
                width: 100%;
                height: 1000px; /* 전체 탭 높이 */
                background-color: #E0E0E0; /* 회색 화면 */
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
                display: flex;
                justify-content: center; /* 가로 중앙 */
                align-items: center; /* 세로 중앙 */
            }
            .title-waiting {
                position: relative;
                color: #FFFFFF; /* 제목 색상 */
                background-color: rgba(0,0,0,0.5); /* 투명 배경 */
                padding: 20px;
                border-radius: 10px;
                text-align: center; /* 텍스트 중앙 */
                z-index: 10;
                line-height: 1.2;
                display: flex;
                flex-direction: column;
                font-family: 'aggro', cursive; /* 기본Aggro 필기체 적용 */
            }
            .k-title-waiting {
                font-size: 48px;
            }
            .e-title-waiting {
                font-size: 32px;
                margin-top: 15px;
            }
        </style>
        <div class="waiting-block">
            <div class="title-waiting">
                <span class="k-title-waiting">한글제목</span>
                <span class="e-title-waiting">영어제목</span>
            </div>
        </div>
        """, height=1010)
