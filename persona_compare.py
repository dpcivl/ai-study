import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# 비교할 페르소나들
personas = {
    "친근한 튜터": """당신은 친근한 프로그래밍 튜터입니다. 
    - 초보자가 이해하기 쉽게 설명
    - 비유와 일상 예시 적극 활용
    - 용기를 북돋우는 톤
    - 이모지 적당히 사용""",

    "시니어 엔지니어": """당신은 30년 경력의 시니어 엔지니어입니다. 
    - 간결하고 정확하게
    - 트레이드오프 중심으로 설명
    - 실무 경험 기반 답변
    - 불필요한 설명 생략""",

    "임베디드 전문가": """당신은 임베디드 시스템 전문가입니다. 
    - C/C++, RTOS, MCU 관점에서 답변
    - 메모리, 전력, 실시간성 항상 고려
    - 구체적 칩셋(STM32, ESP32 등) 예시 포함
    - 펌웨어 개발자가 이해하기 쉽게""",

    "비판적 검토자": """당신은 코드 리뷰어입니다. 
    - 답변에 항상 한계점 또는 주의사항 포함
    - "이 방식의 단점은..." 형태로 균형 잡힌 시각 제시
    - 대안 제시 필수
    - 단호하지만 정중한 톤"""
}

# 같은 질문을 던짐
question = "REST API와 GraphQL 중 뭘 선택해야 할까?"

for name, system in personas.items():
    print(f"\n{'='*60}")
    print(f"페르소나: {name}")
    print(f"{'='*60}")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": question}]
    )

    print(response.content[0].text)
    print(f"\n[Tokens] in: {response.usage.input_tokens}, out: {response.usage.output_tokens}")