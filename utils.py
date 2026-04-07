from PIL import Image
import time

def generate_all_text(query):
    """지피티 등 유료 API를 연결할 수 있는 텍스트 생성 로직"""
    # 실제로는 여기서 OpenAI나 Gemini API를 호출합니다.
    time.sleep(1)
    title = f"[생성됨] {query[:15]}..."
    prompt = f"Peaceful atmosphere, {query}, highly detailed, 8k, cinematic light"
    lyrics = f"[{query}를 바탕으로 생성된 가사]\n\n주의 은혜가 내 영혼에...\n평안한 밤을 주시는 주님..."
    return title, prompt, lyrics

def prepare_background(width, height, prompt, count, filename, uploaded_file):
    """
    이미지 탭의 에러를 방지하는 핵심 함수입니다.
    사용자가 업로드했으면 업로드 이미지를, 아니면 생성/기본 이미지를 반환합니다.
    """
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img = img.resize((width, height))
        return img
    else:
        # 실제로는 여기서 DALL-E나 Midjourney API를 호출하여 생성합니다.
        # 에러 방지를 위해 일단 기본 고화질 다크 톤 이미지를 생성하여 반환합니다.
        img = Image.new('RGB', (width, height), color=(20, 20, 25))
        return img