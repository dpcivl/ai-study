import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

messages = []

print("Claude와 스트리밍 대화. 'quit' 입력 시 종료. \n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("대화를 종료합니다.")
        break

    messages.append({
        "role": "user", 
        "content": user_input
    })

    print("\nClaude: ", end="", flush=True)

    # 스트리밍 응답
    full_response = ""
    
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text   # 전체 응답 수집

    print("\n")   # 줄 바꿈

    # 누적된 전체 응답을 히스토리에 추가
    messages.append({
        "role": "assistant",
        "content": full_response
    })