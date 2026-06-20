import os
import chromadb
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI()
anthropic_client = Anthropic()

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="blog_posts")

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search(query, top_k=5):
    query_emb = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )

    return [
        {
            "content": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "distance": results['distances'][0][i]
        }
        for i in range(len(results['ids'][0]))
    ]

def answer_with_rag(question, top_k=5):
    chunks = search(question, top_k=top_k)

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[출처 {i}] ' {chunk['metadata']['title']}' - {chunk['metadata']['header']}\n"
            f"{chunk['content']}\n"
        )
    context = "\n".join(context_parts)

    system_prompt = """당신은 사용자의 블로그 글 기반 질의응답 시스템입니다. 

규칙:
1. 제공된 컨텍스트만 활용해 답변
2. 컨텍스트에 답이 없으면 "블로그에서 찾을 수 없습니다" 응답
3. 답변 시 어떤 출처(글 제목)에서 왔는지 명시
4. 간결하고 정확하게
5. 일반 지식 사용 금지"""

    user_message = f"""다음 블로그 글 내용 기반으로 답해주세요. 

=== 컨텍스트 ===
{context}

=== 질문 ===
{question}"""
    
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return {
        "answer": response.content[0].text,
        "sources": chunks
    }

if __name__ == "__main__":
    # 본인 블로그 글 주제에 맞는 질문으로 변경
    questions = [
        "내가 RAG에 대해 어떻게 설명했지?",
        "Tool Use 학습할 때 헤맸던 부분이 뭐였어?",
        "임베디드에서 AI Agent로 전환하는 이유를 어떻게 정리했지?",
    ]

    for q in questions:
        print("=" * 70)
        print(f"질문: {q}")
        print("=" * 70)

        result = answer_with_rag(q, top_k=5)

        print(f"\n답변:\n{result['answer']}\n")

        print(f"참고한 출처:")
        for i, s in enumerate(result['sources'], 1):
            print(f"  [{i}] {s['metadata']['title']} - {s['metadata']['header']} "
                  f"(거리: {s['distance']:.3f})")
            
        print()