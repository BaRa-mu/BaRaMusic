from PIL import Image
import time

def generate_all_text(theme):
    """
    주제를 받아 제목, 프롬프트, 가사를 한 번에 생성하는 함수
    (여기에 기존에 사용하시던 OpenAI나 Gemini API 코드를 연결하시면 됩니다)
    """
    time.sleep(1.5)  # API 통신 대기 시간 시뮬레이션
    
    title = f"[{theme}] 평안한 쉼을 위한 노래"
    prompt = f"A beautiful, peaceful illustration of {theme}, highly detailed, 8k resolution, comforting atmosphere, cinematic lighting."
    lyrics = """1절
지친 하루를 마치고
눈을 감고 기도해
주의 따스한 손길이
나를 감싸 안으시네

후렴
평안한 이 밤, 주님 품 안에서
모든 걱정 다 내려놓고
새로운 힘을 얻네, 은혜의 밤"""
    
    return title, prompt, lyrics

def prepare_background(width, height, prompt, count, filename, uploaded_file):
    """
    업로드된 이미지를 처리하거나 프롬프트로 이미지를 생성하는 함수
    """
    if uploaded_file is not None:
        # 사용자가 이미지를 업로드한 경우
        img = Image.open(uploaded_file)
        img = img.resize((width, height))
        return img
    else:
        # 사용자가 이미지를 업로드하지 않고 생성 버튼을 누른 경우
        # (여기에 기존에 사용하시던 이미지 생성 API 코드를 연결하시면 됩니다)
        time.sleep(1) # 이미지 생성 대기 시간 시뮬레이션
        # 일단 더미로 단색(안정적인 톤) 이미지를 반환하여 에러가 나지 않게 합니다.
        img = Image.new('RGB', (width, height), color=(44, 62, 80)) 
        return img