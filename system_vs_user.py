import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

persona = "임베디드 시스템 전문가, C/C++ 관점, 메모리/전력 항상 고려"
question = "함수 포인터의 장단점은?"

# 방법 A: system에 페르소나
print("=" * 60)
print("방법 A: system에 페르소나 정의")
print("=" * 60)

response_a = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    system=f"당신은 {persona}입니다.",
    messages=[{"role": "user", "content": question}]
)

print(response_a.content[0].text)

# 방법 B: user 메세지에 페르소나
print("\n" + "=" * 60)
print("방법 B: user 메세지에 페르소나 지시")
print("=" * 60)

response_b = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[
        {"role": "user", "content": f"당신은 {persona}입니다. 질문: {question}"}
    ]
)

print(response_b.content[0].text)

# 멀티턴에서 차이
print("\n" + "=" * 60)
print("멀티턴 테스트: 두 번째 턴에 다른 질문")
print("=" * 60)

# A 방식: system 유지하고 새 질문
messages_a = [
    {"role": "user", "content": question},
    {"role": "assistant", "content": response_a.content[0].text},
    {"role": "user", "content": "이번엔 메모리 할당 얘기해줘"}
]

response_a2 = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    system=f"당신은 {persona}입니다.",
    messages=messages_a
)

print("A 방식 (system 유지):")
print(response_a2.content[0].text[:300])

# B 방식: user 메시지에만 한 번 적고 두 번째 턴엔 안 적음
messages_b = [
    {"role": "user", "content": f"당신은 {persona}입니다. 질문: {question}"},
    {"role": "assistant", "content": response_b.content[0].text},
    {"role": "user", "content": "이번엔 메모리 할당 얘기해줘"}
]

response_b2 = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=messages_b
)

print("\nB 방식 (user에만 한 번):")
print(response_b2.content[0].text[:300])