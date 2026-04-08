--- ui_lyrics.py
+++ ui_lyrics.py
@@ -20,89 +20,89 @@
 def render_tab1():
-st.markdown("""
-
-.stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }
-.block-container { padding-top: 1rem !important; }
-[data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] .stTextInput input { height: 38px !important; font-size: 14px !important; }
-[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label { font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px !important; }
-
-""", unsafe_allow_html=True)
-with st.sidebar:
-    st.header("음악 생성 설정")
-    subject = st.text_input("💡 곡 주제", key="l_subject")
-    target = st.radio("🎯 타깃 설정", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
-    lyric_mood = st.selectbox(f"✨ {target} 가사 분위기", MOODS[target], key="mood_sel")
-    genre = st.selectbox(f"🎸 {target} 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
-    song_atm = st.selectbox("🌈 곡 분위기 상세", SONG_ATMOSPHERES, key="song_atm_sel")
-    tempo = st.select_slider("⏱️ 템포", options=["매우 느림", "느림", "보통", "빠름", "매우 빠름"], value="보통")
-    v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
-    vocal_style = st.selectbox(f"🗣️ {v_type} 스타일 상세", VOCALS[v_type], key="v_style_sel")
-    main_inst = st.selectbox("🎹 메인 악기 선택", INSTRUMENTS, key="inst_sel")
-    st.divider()
-    strict_end = st.checkbox("가사 종료 시 즉시 곡 종료", value=True, key="strict_end_check")
-
-    if st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True):
-        st.session_state.res_title = "은혜의항해_VoyageOfGrace"
-        
-        ending_tags = "\n\n[Outro]\n(Natural fade out to silence)\n[END]\n[Hard Stop]\n[Silence]"
-        st.session_state.res_lyrics = f"""[Verse 1]
-{subject}의 빛이 어두운 방안을 비추고
-지친 내 영혼에 새로운 숨결을 불어넣네
-세상의 소음 속에서도 들려오는 그 음성
-나의 발걸음을 인도하시는 따스한 손길
-[Chorus]
-오 영원한 그 사랑 {lyric_mood}한 선율 속에
-우리 모두 하나 되어 기쁨으로 노래해
-{song_atm}한 리듬이 온 땅을 가득 채울 때
-{subject}의 영광이 우리 삶에 피어나리
-[Verse 2]
-광야 같은 길을 걸어도 나는 두렵지 않네
-구름 기둥과 불 기둥으로 나를 지키시니
-때로는 거친 파도가 나를 덮쳐와도
-바다를 가르시는 주님의 능력을 믿네
-[Chorus]
-오 영원한 그 사랑 {lyric_mood}한 선율 속에
-우리 모두 하나 되어 기쁨으로 노래해
-{song_atm}한 리듬이 온 땅을 가득 채울 때
-{subject}의 영광이 우리 삶에 피어나리
-[Bridge]
-하늘의 문이 열리고 축복의 비가 내리네
-간절한 우리의 기도가 보좌 앞에 닿을 때
-치유와 회복의 역사가 지금 시작되리
-소망의 닻을 내리고 흔들리지 않으리
-[Verse 3]
-마지막 날에 주님 앞에 서는 그 순간까지
-맡겨진 소명의 길을 묵묵히 걸어가리
-눈물로 씨를 뿌리는 자 기쁨으로 거두리니
-약속의 땅 향해 힘차게 전진해 나가세
-[Chorus]
-오 영원한 그 사랑 {lyric_mood}한 선율 속에
-우리 모두 하나 되어 기쁨으로 노래해
-{song_atm}한 리듬이 온 땅을 가득 채울 때
-{subject}의 영광이 우리 삶에 피어나리""" + ending_tags
-        session_info = SESSION_MAP.get(main_inst, "Full Orchestration")
-        p_style = f"A professional high-fidelity {genre} track for the {target} market. Mood: {lyric_mood}, {song_atm}. Tempo: {tempo}. Long duration composition targeted for 3-8 minutes of continuous flow. "
-        p_vocal = f"Vocal Performance: This production features a {vocal_style} through a {v_type} lead performance. The recording requires meticulous vocal processing with high-end studio gear to achieve crystalline clarity and deep emotional resonance. Harmonies should be rich, professional, and stylistic of the {genre} tradition. "
-        p_inst = f"Instrumentation and Soundstage: The arrangement is anchored by {main_inst} providing the primary harmonic and melodic foundation. This is augmented by a carefully curated session including {session_info}. The stereo field must be wide, immersive, and balanced across all frequency spectrums. "
-        p_tech = "Engineering Specs: 24-bit studio quality, professional mastering with warm analog-style saturation on the low-end and silky-smooth air in the high-frequency range. Dynamic range should be carefully managed to allow the emotional bridge to soar before landing on a powerful, celebratory final chorus. "
-        p_end = f"Structural Constraint: { 'CRITICAL: NO looping and NO repetition of song sections once the lyrics conclude. The track MUST end naturally and definitively into absolute silence following the [END] tag.' if strict_end else 'Standard end.' } "
-        p_detail = f"Detailed Production Analysis: The arrangement for '{subject}' must prioritize a sophisticated and highly nuanced harmonic progression that resonates deeply with {target} listeners. The {main_inst} should lead with a rhythmic and lyrical foundation that integrates perfectly with the emotive {vocal_style}. The sonic environment must mirror a world-class studio recording, ensuring total absence of digital artifacts or monotonous loops. Each instrument in the {session_info} should be strategically placed within the 3D stereo field, providing a lush, immersive depth. The dynamic range should allow the emotional bridge to soar before landing on a celebratory final chorus. Care should be taken to respect {genre} foundations while injecting modern energy. The transition from the {lyric_mood} mood to the {song_atm} atmosphere must feel organic and earned. Final check: the song MUST terminate into absolute silence immediately after the concluding lyrics, ensuring a one-take, definitive performance that captures the essence of {subject} without artificial time extension. This track must maintain professional industry standards, ensuring the balance between the {main_inst} and the {v_type} vocals remains consistent throughout the mix. No additional instrumental filler should be added after the lyrics are completed. Meticulous care in the mastering stage is required to preserve the {song_atm} character while keeping the low-end punchy."
-        
-        full_p = (p_style + p_vocal + p_inst + p_tech + p_end + p_detail).strip()
-        st.session_state.res_prompt = full_p[:1000]
-
-if st.session_state.get('res_title'):
-    st.subheader("🏷️ 곡 제목 (한글_영어)")
-    st.code(st.session_state.res_title, language="text")
-    
-    st.divider()
-
-    st.subheader("📝 생성 가사 (편집 및 수정)")
-
-    # ✅ 여기만 변경됨 (동적 높이)
-    lyrics = st.session_state.res_lyrics
-    line_count = lyrics.count("\n") + 1
-    dynamic_height = min(1500, max(300, line_count * 25))
-
-    st.text_area("가사 본문", value=lyrics, height=dynamic_height, key="lyrics_final_view", help="여기서 가사를 자유롭게 수정하세요.")
-
-    if st.button("📋 가사 전체 복사"):
-        st.code(st.session_state.res_lyrics, language="text")
-        
-    st.divider()
-
-    st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
-    st.text_area("프롬프트 확인 (700~1000자)", value=st.session_state.res_prompt, height=600, key="prompt_final_view")
-
-    if st.button("📋 프롬프트 복사"):
-        st.code(st.session_state.res_prompt, language="text")
-else:
-    st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
+    st.markdown("""
+        <style>
+        .stTabs [data-baseweb="tab-list"] { justify-content: flex-start !important; gap: 20px !important; }
+        .block-container { padding-top: 1rem !important; }
+        [data-testid="stSidebar"] div[data-baseweb="select"] > div, [data-testid="stSidebar"] .stTextInput input { height: 38px !important; font-size: 14px !important; }
+        [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label { font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px !important; }
+        </style>
+    """, unsafe_allow_html=True)
+
+    with st.sidebar:
+        st.header("음악 생성 설정")
+        subject = st.text_input("💡 곡 주제", key="l_subject")
+        target = st.radio("🎯 타깃 설정", ["CCM", "대중음악"], horizontal=True, key="genre_sel")
+        lyric_mood = st.selectbox(f"✨ {target} 가사 분위기", MOODS[target], key="mood_sel")
+        genre = st.selectbox(f"🎸 {target} 장르", CCM_GENRES if target == "CCM" else POP_GENRES, key="genre_list_sel")
+        song_atm = st.selectbox("🌈 곡 분위기 상세", SONG_ATMOSPHERES, key="song_atm_sel")
+        tempo = st.select_slider("⏱️ 템포", options=["매우 느림", "느림", "보통", "빠름", "매우 빠름"], value="보통")
+        v_type = st.radio("🎤 보컬 유형", ["남성", "여성", "듀엣"], horizontal=True, key="v_type_sel")
+        vocal_style = st.selectbox(f"🗣️ {v_type} 스타일 상세", VOCALS[v_type], key="v_style_sel")
+        main_inst = st.selectbox("🎹 메인 악기 선택", INSTRUMENTS, key="inst_sel")
+        st.divider()
+        strict_end = st.checkbox("가사 종료 시 즉시 곡 종료", value=True, key="strict_end_check")
+
+        if st.button("🚀 AI 가사 및 세션 구성 시작", type="primary", use_container_width=True):
+            # [수정] 곡에 맞는 [한글제목_영어제목] 생성 (직관적 제목 부여)
+            st.session_state.res_title = "은혜의항해_VoyageOfGrace"
+            
+            ending_tags = "\n\n[Outro]\n(Natural fade out to silence)\n[END]\n[Hard Stop]\n[Silence]"
+            st.session_state.res_lyrics = f"""[Verse 1]
+{subject}의 빛이 어두운 방안을 비추고
+지친 내 영혼에 새로운 숨결을 불어넣네
+세상의 소음 속에서도 들려오는 그 음성
+나의 발걸음을 인도하시는 따스한 손길
+
+[Chorus]
+오 영원한 그 사랑 {lyric_mood}한 선율 속에
+우리 모두 하나 되어 기쁨으로 노래해
+{song_atm}한 리듬이 온 땅을 가득 채울 때
+{subject}의 영광이 우리 삶에 피어나리
+
+[Verse 2]
+광야 같은 길을 걸어도 나는 두렵지 않네
+구름 기둥과 불 기둥으로 나를 지키시니
+때로는 거친 파도가 나를 덮쳐와도
+바다를 가르시는 주님의 능력을 믿네
+
+[Chorus]
+오 영원한 그 사랑 {lyric_mood}한 선율 속에
+우리 모두 하나 되어 기쁨으로 노래해
+{song_atm}한 리듬이 온 땅을 가득 채울 때
+{subject}의 영광이 우리 삶에 피어나리
+
+[Bridge]
+하늘의 문이 열리고 축복의 비가 내리네
+간절한 우리의 기도가 보좌 앞에 닿을 때
+치유와 회복의 역사가 지금 시작되리
+소망의 닻을 내리고 흔들리지 않으리
+
+[Verse 3]
+마지막 날에 주님 앞에 서는 그 순간까지
+맡겨진 소명의 길을 묵묵히 걸어가리
+눈물로 씨를 뿌리는 자 기쁨으로 거두리니
+약속의 땅 향해 힘차게 전진해 나가세
+
+[Chorus]
+오 영원한 그 사랑 {lyric_mood}한 선율 속에
+우리 모두 하나 되어 기쁨으로 노래해
+{song_atm}한 리듬이 온 땅을 가득 채울 때
+{subject}의 영광이 우리 삶에 피어나리""" + ending_tags
+
+            session_info = SESSION_MAP.get(main_inst, "Full Orchestration")
+            p_style = f"A professional high-fidelity {genre} track for the {target} market. Mood: {lyric_mood}, {song_atm}. Tempo: {tempo}. Long duration composition targeted for 3-8 minutes. "
+            p_vocal = f"Vocal Performance: This production features a {vocal_style} through a {v_type} lead performance. The recording requires meticulous vocal processing with high-end studio gear to achieve crystalline clarity and deep emotional resonance. Harmonies should be rich, professional, and stylistic of the {genre} tradition. "
+            p_inst = f"Instrumentation and Soundstage: The arrangement is anchored by {main_inst} providing the primary harmonic and melodic foundation. This is augmented by a carefully curated session including {session_info}. The stereo field must be wide, immersive, and balanced across all frequency spectrums. "
+            p_tech = "Engineering Specs: 24-bit studio quality, professional mastering with warm analog-style saturation on the low-end and silky-smooth air in the high-frequency range. Dynamic range should be carefully managed to allow the emotional bridge to soar before landing on a powerful, celebratory final chorus. "
+            p_end = f"Structural Constraint: { 'CRITICAL: NO looping and NO repetition of song sections once the lyrics conclude. The track MUST end naturally and definitively into absolute silence following the [END] tag.' if strict_end else 'Standard end.' } "
+            p_detail = f"Detailed Production Analysis: The arrangement for '{subject}' must prioritize a sophisticated and highly nuanced harmonic progression that resonates deeply with {target} listeners. The {main_inst} should lead with a rhythmic and lyrical foundation that integrates perfectly with the emotive {vocal_style}. The sonic environment must mirror a world-class studio recording, ensuring total absence of digital artifacts or monotonous loops. Each instrument in the {session_info} should be strategically placed within the 3D stereo field, providing a lush, immersive depth. The dynamic range should allow the emotional bridge to soar before landing on a celebratory final chorus. Care should be taken to respect {genre} foundations while injecting modern energy. The transition from the {lyric_mood} mood to the {song_atm} atmosphere must feel organic and earned. Final check: the song MUST terminate into absolute silence immediately after the concluding lyrics, ensuring a one-take, definitive performance that captures the essence of {subject} without artificial time extension. This track must maintain professional industry standards, ensuring the balance between the {main_inst} and the {v_type} vocals remains consistent throughout the mix. No additional instrumental filler should be added after the lyrics are completed. Meticulous care in the mastering stage is required to preserve the {song_atm} character while keeping the low-end punchy."
+            
+            full_p = (p_style + p_vocal + p_inst + p_tech + p_end + p_detail).strip()
+            st.session_state.res_prompt = full_p[:1000]
+
+    if st.session_state.get('res_title'):
+        st.subheader("🏷️ 곡 제목 (한글_영어제목)")
+        st.code(st.session_state.res_title, language="text")
+        st.divider()
+        st.subheader("📝 곡 가사 (즉시 수정 및 편집)")
+        
+        lyrics = st.session_state.res_lyrics
+        line_count = lyrics.count("\n") + 1
+        dynamic_height = min(1500, max(300, line_count * 25))
+
+        st.text_area("가사 본문", value=lyrics, height=dynamic_height, key="lyrics_final_view", help="여기서 가사를 자유롭게 수정하세요.")
+        if st.button("📋 가사 복사"):
+            st.code(st.session_state.res_lyrics, language="text")
+            
+        st.divider()
+        st.subheader(f"🛠️ AI 제작 프롬프트 (길이: {len(st.session_state.res_prompt)}자)")
+        st.text_area("프롬프트 확인 (700~1000자)", value=st.session_state.res_prompt, height=600, key="prompt_final_view")
+        if st.button("📋 프롬프트 복사"):
+            st.code(st.session_state.res_prompt, language="text")
+    else:
+        st.info("👈 왼쪽에서 설정을 마치고 생성 버튼을 눌러주세요.")
