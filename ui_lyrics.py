--- ui_lyrics.py
+++ ui_lyrics.py
@@ -95,4 +95,12 @@
         if st.button("📋 프롬프트 복사"):
             st.code(st.session_state.res_prompt, language="text")
+
+        st.divider()
+        st.subheader("🏁 다음 단계로 이동")
+        col_next1, col_next2 = st.columns(2)
+        with col_next1:
+            if st.button("🎨 2. 이미지 생성으로 이동", use_container_width=True):
+                st.session_state.active_tab = 1
+                st.rerun()
+        with col_next2:
+            if st.button("🎬 3. 영상 렌더링으로 이동", use_container_width=True):
+                st.session_state.active_tab = 2
+                st.rerun()
     else:
