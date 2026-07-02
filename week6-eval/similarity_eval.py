"""
유사도 기반 평가
정답이 텍스트일 때 - 의미가 같은지 임베딩으로 측정
"""
import os
import numpy as np
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI()
anthropic_client = Anthropic()


def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))



# ===== 테스트 케이스: 질문 + 기준 정답 =====
test_cases = [
    {
        "question": "LangGraph에서 State가 뭐야? 한 문장으로.",
        "reference": "State의 그래프의 모든 노드가 공유하며 읽고 업데이트하는 데이터 공간입니다. "
    },
    {
        "question": "RAG에서 청크를 나누는 이유는? 한 문장으로.",
        "reference": "긴 문서를 한 덩어리로 임베딩하면 의미가 평균화되어 흐릿해지므로, 검색 정밀도를 위해 의미 단위로 나눕니다. "
    },
    {
        "question": "Prompt Caching의 효과는? 한 문장으로.",
        "reference": "동일한 프롬프트 prefix를 재사용하면 두 번째 호출부터 비용이 약 90% 절감되고 응답 속도도 빨라집니다."
    },
    {
        "question": "MCP가 뭐야? 한 문장으로.",
        "reference": "MCP는 LLM이 외부 시스템의 도구와 데이터에 접근하는 방식을 표준화한 Anthropic의 프로토콜입니다."
    },
]


def get_llm_answer(question):
    """평가 대상 시스템 (여기선 단순 LLM 호출)"""
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text


def run_similarity_eval(threshold=0.75):
    """유사도 기반 평가 실행"""
    print("=" * 70)
    print(f"유사도 기반 평가 (통과 기준: {threshold})")
    print("=" * 70)

    results = []
    passed = 0

    for i, case in enumerate(test_cases, 1):
        question = case["question"]
        reference = case["reference"]

        # LLM 답변 받기
        answer = get_llm_answer(question)

        # 기준 정답과 유사도 계산
        ref_emb = get_embedding(reference)
        ans_emb = get_embedding(answer)
        similarity = cosine_similarity(ref_emb, ans_emb)

        is_pass = similarity >= threshold
        if is_pass:
            passed += 1

        status = "✅" if is_pass else "❌"      # 이 부분 복붙함
        print(f"\n{i}. {status} {question}")
        print(f"  기준: {reference[:60]}...")
        print(f"  답변: {answer[:60]}...")
        print(f"  유사도: {similarity:.4f}")

        results.append({
            "question": question,
            "similarity": float(similarity),
            "passed": is_pass
        })

    total = len(test_cases)
    print("\n" + "=" * 70)
    print(f"통과율: {passed}/{total} = {passed/total*100:.1f}%")
    print(f"평균 유사도: {sum(r['similarity'] for r in results)/total:.4f}")
    print("=" * 70)

    return results

if __name__ == "__main__":
    run_similarity_eval()
