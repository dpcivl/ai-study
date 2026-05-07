import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

system = """당신은 코드 분석 도구입니다.
사용자가 코드를 주면 분석 결과를 **반드시 유효한 JSON 형식으로만** 응답하세요. 

응답 형식:
{
  "summary": "코드 한 줄 요약",
  "language": "프로그래밍 언어",
  "issues": [
    {"severity": "high|medium|low", "description": "문제 설명"}
    ],
  "suggestions": ["개선 제안 1", "개선 제안 2"],
  "scores": {
    "readability": 7,
    "efficiency": 8,
    "safety": 5
    }
    }
    
JSON 외 다른 텍스트는 절대 포함하지 마세요. 마크다운 코드블록(```)도 사용하지 마세요. """

code_to_analyze = """
char* get_user_name() {
  char buffer[20];
  scanf("%s", buffer);
  return buffer;
}
"""

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=system,
    messages=[
        {"role": "user", "content": f"이 코드 분석해줘:\n{code_to_analyze}"}
    ]
)

# 응답 시작이 { 가 아니면 첫 { 부터 마지막 } 까지만 추출
def extract_json(text):
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end != 0:
        return text[start:end]
    return text

# 응답 받기
raw_response = response.content[0].text
clean_json = extract_json(raw_response)

# JSON 파싱 시도
try:
    result = json.loads(clean_json)
    print("=" * 60)
    print("파싱 성공! 구조화된 데이터로 활용 가능")
    print("=" * 60)

    print(f"\n언어: {result['language']}")
    print(f"요약: {result['summary']}")

    print(f"\n발견된 문제 ({len(result['issues'])}개):")
    for issue in result['issues']:
        print(f" [{issue['severity'].upper()}] {issue['description']}")

    print(f"\n점수:")
    for category, score in result['scores'].items():
        print(f" {category}: {score}/10")

except json.JSONDecodeError as e:
    print(f"JSON 파싱 실패: {e}")
    print("LLM이 형식을 안 지킴 - 더 강한 프롬프트 필요")