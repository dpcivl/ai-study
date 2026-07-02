"""
회귀 테스트: description 개선 Before/After 비교
같은 테스트셋으로 두 버전 측정 -> 개선 여부 숫자로 확인
"""
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


# ===== 버전 A: 대충 쓴 description =====
tools_v1 = [
    {
        "name": "calculator",
        "description": "계산",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "날씨",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    },
    {
        "name": "search_web",
        "description": "검색",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
]

# ===== 버전 B: 명확한 description =====
tools_v2 = [
    {
        "name": "calculator",
        "description": "수학 계산 전용. 사칙연산, 큰 수 곱셈, 나눗셈, 제곱 등 순수 숫자 연산에만 사용. 버전 번호, 가격, 통계 같은 '조회'는 검색을 사용할 것. ",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "계산식 (예: 847 * 2391)"}},
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "특정 도시의 현재 날씨, 기온, 강수 정보를 조회. '춥다', '덥다', '비 오냐' 같은 날씨 관련 질문에 사용.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "도시 이름 (예: 부산)"}},
            "required": ["city"]
        }
    },
    {
        "name": "search_web",
        "description": "웹에서 최신 정보 검색. 뉴스, 가격, 버전 정보, 일반 지식 등 계산이나 날씨가 아닌 모든 정보 정보에 사용.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "검색어"}},
            "required": ["query"]
        }
    }
]


# ===== 테스트셋 (난이도 계층화 적용) =====
test_cases = [
    # Easy: 명확한 케이스
    {"question": "847 곱하기 2391은?", "expected": "calculator", "level": "easy"},
    {"question": "부산 날씨 어때?", "expected": "get_weather", "level": "easy"},
    {"question": "오늘 주요 뉴스 알려줘", "expected": "search_web", "level": "easy"},
    {"question": "1234 더하기 5678은?", "expected": "calculator", "level": "easy"},
     
    # Medium: 판단 필요
    {"question": "파이썬 최신 버전이 뭐야?", "expected": "search_web", "level": "medium"},  # 숫자 나오지만 검색
    {"question": "서울 지금 추워?", "expected": "get_weather", "level": "medium"},  # 간접 표현
    {"question": "비트코인 지금 얼마야?", "expected": "search_web", "level": "medium"},     # 가격=숫자지만 검색
    {"question": "15의 제곱은?", "expected": "calculator", "level": "medium"},

    # Hard: 헷갈리는 케이스
    {"question": "달러 환율에 1500 곱하면?", "expected": "search_web", "level": "hard"},    # 환율 먼저 필요
    {"question": "내일 도쿄 갈 건데 우산 챙길까?", "expected": "get_weather", "level": "hard"}, # 우회적
]


def get_selected_tool(question, tools):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        tools=tools,
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": question}]
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.name
    return None


def run_eval(tools, version_name):
    """한 버전 평가"""
    print(f"\n{'=' * 70}")
    print(f"평가: {version_name}")
    print("=" * 70)

    results = []
    for case in test_cases:
        selected = get_selected_tool(case["question"], tools)
        is_correct = (selected == case["expected"])
        results.append({
            "question": case["question"],
            "level": case["level"],
            "expected": case["expected"],
            "selected": selected,
            "correct": is_correct
        })
        status = "✅" if is_correct else "❌"
        print(f"{status} [{case['level']:<6}] {case['question'][:35]:<38} -> {selected}")

    return results


def summarize(results, version_name):
    """난이도별 통계"""
    total = len(results)
    correct = sum(1 for r in results if r["correct"])

    print(f"\n[{version_name}] 전체: {correct}/{total} = {correct/total*100:.1f}%")

    for level in ["easy", "medium", "hard"]:
        level_results = [r for r in results if r["level"] == level]
        level_correct = sum(1 for r in level_results if r["correct"])
        if level_results:
            print(f"  {level:<6}: {level_correct}/{len(level_results)} = {level_correct/len(level_results)*100:1f}%")

    return correct / total * 100


if __name__ == "__main__":
    # 버전 A 평가
    results_v1 = run_eval(tools_v1, "V1 (대충 쓴 description)")

    # 버전 B 평가
    results_v2 = run_eval(tools_v2, "V2 (명확한 description)")

    # 비교
    print("\n" + "=" * 70)
    print("Before / After 비교")
    print("=" * 70)
    acc_v1 = summarize(results_v1, "V1")
    acc_v2 = summarize(results_v2, "V2")

    print(f"\n개선폭: {acc_v2 - acc_v1:+.1f}%p")

    # 저장
    with open("regression_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "v1_accuracy": acc_v1,
            "v2_accuracy": acc_v2,
            "improvement": acc_v2 - acc_v1,
            "v1_results": results_v1,
            "v2_results": results_v2
        }, f, ensure_ascii=False, indent=2)
    print("\n결과 저장: regression_results.json")