import os
import time
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# 긴 답변이 나올 만한 질문
question = "임베디드 시스템에서 RTOS 도입을 결정할 때 고려해야 할 요소들을 자세히 설명해줘. 각 요소별로 구체적인 예시와 함께."

# ===== 방법 A: 일반 호출 (스트리밍 X) =====
print("=" * 60)
print("방법 A: 일반 호출 (전체 응답 기다림)")
print("=" * 60)

start = time.time()
print(f"호출 시작: 0.00초")

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=2048,
    messages=[{"role": "user", "content": question}]
)

elapsed = time.time() - start
print(f"응답 받음: {elapsed:.2f}초 후")
print(f"응답 길이: {len(response.content[0].text)}자")
print()
print("응답 일부:")
print(response.content[0].text[:200] + "...")

# ===== 방법 B: 스트리밍 =====
print("\n" + "=" * 60)
print("방법 B: 스트리밍 (실시간 출력)")
print("=" * 60)

start = time.time()
first_token_time = None
print(f"호출 시작: 0.00초")
print("응답: ", end="", flush=True)

with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=2048,
    messages=[{"role": "user", "content": question}]
) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time() -start
            print(f"\n[첫 토큰 도착: {first_token_time:.2f}초]\n", end="")
        print(text, end="", flush=True)

elapsed = time.time() - start
print(f"\n\n전체 완료: {elapsed:.2f}초 후")
print(f"첫 토큰까지 시간 (TTFT): {first_token_time:.2f}초")