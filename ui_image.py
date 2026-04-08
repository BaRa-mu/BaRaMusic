import streamlit as st
import time
import os

def render_tab2():
    # [1. 데이터 영역: 드롭다운 옵션 15개 이상]
    STYLES = ["극사실주의 시네마틱", "디즈니 애니메이션 풍", "고전 유화 스타일", "투명한 수채화", "네온 사이버펑크", "신비로운 판타지 일러스트", "정밀한 연필 스케치", "현대적 3D 렌더링", "레트로 8비트 픽셀", "추상적 미니멀리즘", "고딕 호러 스타일", "화려한 바로크 풍", "초현실주의 예술", "잉크 워시 수묵화", "팝아트 스타일"]
    MOODS = ["웅장하고 압도적인", "따뜻하고 포근한", "차가운 도시의", "몽환적이고 신비로운", "어두운 비장미", "밝고 희망찬", "빈티지하고 아련한", "평화롭고 정적인", "강렬하고 폭발적인", "애절하고 슬픈", "거룩하고 성스러운", "에너지 넘치는", "고독하고 쓸쓸한", "우아하고 고전적인", "신선하고 청량한"]
    LIGHTINGS = ["시네마틱 골든아워", "스튜디오 조명", "달빛 아래", "네온사인", "아침 햇살", "스포트라이트", "안개 조명", "촛불 빛", "화산 반사", "역광(Rim Light)", "하이키 조명", "로우키 조명", "창가 사선 빛", "오로라 광원", "심해의 푸른 빛"]
    CAMERAS = ["와이드 파노라마", "매크로 샷", "버즈아이 뷰", "웜즈아이 뷰", "아이레벨", "더치 앵글", "오버더숄더", "피쉬아이", "아웃포커싱", "깊은 피사계 심도", "로모그래피", "소프트 포커스", "로우 앵글", "하이 앵글", "시점 샷(POV)"]
    
    # [한글 폰트 15개 이상]
    K_FONTS = [
        {"name": "나눔손글씨 붓", "family": "Nanum Brush Script"}, {"name": "나눔손글씨 펜", "family": "Nanum Pen Script"},
        {"name": "독도체", "family": "Dokdo"}, {"name": "검은고딕", "family": "Black Han Sans"},
        {"name": "궁서체", "family": "Gungsuh"}, {"name": "바탕체", "family": "Batang"},
        {"name": "제주 명조", "family": "Jeju Myeongjo"}, {"name": "카페24 써라운드", "family": "Cafe24 Surround"},
        {"name": "야놀자 야체", "family": "Yanolja Yache"}, {"name": "빙그레체", "family": "Binggrae"},
        {"name": "코트라 희망체", "family": "KOTRA HOPE"}, {"name": "어그로체", "family": "Aggro"},
        {"name": "HSS새로운봄", "family": "HSS New Spring"}, {"name": "가나초콜릿", "family": "Gana Chocolate"},
        {"name": "배민 도현", "family": "Bemin DoHyeon"}
    ]
    # [영어 폰트 15개 이상]
    E_FONTS = [
        {"name": "Great Vibes", "family": "Great Vibes"}, {"name": "Dancing Script", "family": "Dancing Script"},
        {"name": "Pacifico", "family": "Pacifico"}, {"name": "Shadows Into Light", "family": "Shadows Into Light"},
        {"name": "Satisfy", "family": "Satisfy"}, {"name": "Courgette", "family": "Courgette"},
        {"name": "Lobster", "family": "Lobster"}, {"name": "Permanent Marker", "family": "Permanent Marker"},
        {"name": "Sacramento", "family": "Sacramento"}, {"name": "Yellowtail", "family": "Yellowtail"},
        {"name": "Cookie", "family": "Cookie"}, {"name": "Damion", "family": "Damion"},
        {"name": "Handlee", "family": "Handlee"}, {"name": "Merienda", "family": "Merienda"},
        {"name": "Kaushan Script", "family": "Kaushan Script"}
    ]
    
    EFFECT_LIST = ["강력한 화이트 글로우", "네온 핑크 광채", "딥 블랙 쉐도우", "골든 샤인", "스모키 안개", "3D 입체", "크롬 메탈릭", "불꽃 타오름", "얼음 파편", "글리치 노이즈", "투명 유리", "외부 광채", "더블 쉐도우", "무지개 그라데이션", "다크 글로우"]

    # [2. 사이드바: 제목 파싱 및 설정]
    with st.sidebar:
        st.divider()
        st.subheader("📂 음원 파일 업로드")
        audio_file = st.file_uploader("Browse files", type=["mp3", "wav", "m4a"], key="main_audio_up", label_visibility="collapsed")
        
        # 파일명 파싱 (파일명_English) 즉시 업데이트
        if audio_file:
            base_name = os.path.splitext(audio_file.name)[0]
            if st.session_state.get('last_f') != audio_file.name:
                if "_" in base_name:
                    k_p, e_p = base_name.split("_", 1)
                    st.session_state['k_t_val'] = k_p
                    st.session_state['e_t_val'] = e_p
                else:
                    st.session_state['k_t_val'] = base_name
                    st.session_state['e_t_val'] = base_name
                st.session_state['last_f'] = audio_file.name

        st.divider()
        st.subheader("🏷️ 이미지 제목 (자동 입력)")
        k_title = st.text_input("한글 제목", value=st.session_state.get('k_t_val', ""), key="k_title_input")
        e_title = st.text_input("영어 제목", value=st.session_state.get('e_t_val', ""), key="e_title_input")
        
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

    # --- [3. CSS: 회색 배경, 520px 고정, 폰트/효과 미리보기] ---
    all_fonts = K_FONTS + E_FONTS
    font_imports = "".join([f"@import url('https://fonts.googleapis.com/css2?family={f['family'].replace(' ', '+')}&display=swap');" for f in all_fonts])
    
    st.markdown(f"""
        <style>
        {font_imports}
        
        /* 메뉴 내 폰트 스타일 미리보기 강제 적용 */
        div[data-baseweb="select"] li {{ font-size: 1.1rem !important; padding: 10px !important; }}
        /* 한글 폰트 스타일 */
        { "".join([f'li[id*="option-{i}"] {{ font-family: "{K_FONTS[i]["family"]}", cursive !important; }}' for i in range(len(K_FONTS))]) }
        /* 영어 폰트 스타일 (한글 리스트 뒤에 이어짐) */
        { "".join([f'li[id*="option-{len(K_FONTS)+i}"] {{ font-family: "{E_FONTS[i]["family"]}", cursive !important; }}' for i in range(len(E_FONTS))]) }

        /* 미리보기 프레임: 긴 면 520px 고정 및 회색 배경 */
        .preview-canvas {{
            position: relative;
            background-color: #E0E0E0;
            margin: 0 auto 30px auto;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            justify-content: center; align-items: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }}
        .dim-16-9 {{ width: 520px; height: 292.5px; }}
        .dim-9-16 {{ width: 292.5px; height: 520px; }}

        /* 제목 효과 (화이트 글로우 기본) */
        .title-eff {{
            color: white; text-align: center; line-height: 1.2; pointer-events: none; z-index: 10;
            text-shadow: 0 0 15px rgba(255,255,255,1), 2px 2px 5px rgba(0,0,0,0.8);
        }}
        
        /* 효과 옵션 */
        .glow-w {{ text-shadow: 0 0 20px #fff, 2px 2px 4px #000; }}
        .glow-n {{ text-shadow: 0 0 15px #ff00ff, 0 0 30px #ff00ff, 2px 2px 2px #000; }}
        .sh-deep {{ text-shadow: 5px 5px 12px rgba(0,0,0,1); }}

        /* 다운로드 호버 */
        .dl-hover {{
            position: absolute; top: 15px; right: 15px;
            background: rgba(0,0,0,0.8); color: white; padding: 6px 14px;
            border-radius: 5px; opacity: 0; transition: 0.3s; z-index: 20;
        }}
        .preview-canvas:hover .dl-hover {{ opacity: 1; }}
        </style>
    """, unsafe_allow_html=True)

    # --- [4. 화면 출력 영역] ---
    if not st.session_state.get('img_gen_done') and not gen_btn:
        # [상태: 생성 전] 회색 화면 중앙 제목
        st.markdown(f"""
            <div class="preview-canvas dim-16-9">
                <div class="title-eff">
                    <div style="font-family: 'Aggro', cursive; font-size: 45px;">{k_title if k_title else '한글제목'}</div>
                    <div style="font-family: 'Nanum Pen Script', cursive; font-size: 28px; margin-top: 15px;">{e_title if e_title else 'English Title'}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        if gen_btn:
            with st.spinner("이미지 생성 중..."): time.sleep(1.5)
            st.session_state.img_gen_done = True

        def render_unit(label, key_id, ratio_class):
            st.markdown(f"### {label}")
            with st.container():
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    # **한글폰트는 한글 이름으로, 영어폰트는 영어 이름으로 메뉴 구성**
                    kf_idx = st.selectbox("한글 폰트", range(len(K_FONTS)), format_func=lambda x: K_FONTS[x]["name"], index=11, key=f"kf_{key_id}")
                    ef_idx = st.selectbox("영어 폰트", range(len(E_FONTS)), format_func=lambda x: E_FONTS[x]["name"], index=1, key=f"ef_{key_id}")
                with c2:
                    ks = st.slider("한글 크기", 10, 110, 50, key=f"ks_{key_id}")
                    es = st.slider("영어 크기", 10, 90, 30, key=f"es_{key_id}")
                with c3:
                    py = st.slider("상하 (%)", 0, 100, 50, key=f"y_{key_id}")
                    px = st.slider("좌우 (%)", 0, 100, 50, key=f"x_{key_id}")
                with c4:
                    spacing = st.slider("간격", 0, 100, 20, key=f"sp_{key_id}")
                    eff_sel = st.selectbox("제목 효과 선택", EFFECT_LIST, key=f"eff_{key_id}")

            eff_class = "glow-w" if "글로우" in eff_sel else "glow-n" if "네온" in eff_sel else "sh-deep"

            st.markdown(f"""
                <div class="preview-canvas {ratio_class}" style="background-color:#000;">
                    <div class="dl-hover">⬇️ Download</div>
                    <img src="https://via.placeholder.com/1280x720.png?text={label}" style="width:100%; height:100%; object-fit:cover;">
                    <div class="title-eff {eff_class}" style="position: absolute; left: {px}%; top: {py}%; transform: translate(-50%, -50%);">
                        <div style="font-family: '{K_FONTS[kf_idx]['family']}'; font-size: {ks}px;">{k_title}</div>
                        <div style="font-family: '{E_FONTS[ef_idx]['family']}'; font-size: {es}px; margin-top: {spacing}px;">{e_title}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.divider()

        # 규격별 출력 (숏츠 9:16 적용)
        render_unit("유튜브 메인 (16:9)", "yt", "dim-16-9")
        render_unit("틱톡 (9:16)", "tk", "dim-9-16")
        if shorts_count > 0:
            for i in range(shorts_count):
                render_unit(f"쇼츠 #{i+1} (9:16)", f"sh_{i}", "dim-9-16")
