import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# 강력한 출력 형식 강제
system = """당신은 코드 분석 전문가입니다. 

사용자가 코드를 보여주면 반드시 다음 형식으로만 답변하세요:

## 한 줄 요약
[코드가 무엇을 하는지 한 줄로]

## 잠재적 문제점
1. [문제 1]
2. [문제 2]
3. [문제 3]

## 개선 제안
- [제안 1]
- [제안 2]

## 평가 점수
가독성: [1-10점]
효율성: [1-10점]
안전성: [1-10점]

다른 형식이나 추가 설명은 절대 하지 마세요."""

# 분석할 코드
code_to_analyze = """
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
        return total / len(numbers)
        """

code_2 = """
char buffer[10];
strcpy(buffer, user_input);
"""

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=system,
    messages=[
        {"role": "user", "content": f"이 코드 분석해줘:\n```c\n{code_2}\n```"}
    ]
)

print(response.content[0].text)