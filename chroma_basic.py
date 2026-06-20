import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ===== Chroma 클라이언트 생성 =====
# PersistentClient: 디스크에 저장 (재시작해도 유지)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 컬렉션 = SQL의 테이블 같은 개념
# get_or_create: 있으면 가져오고 없으면 만들기
collection = chroma_client.get_or_create_collection(
    name="my_first_collection",
    metadata={"description": "Chroma 학습용 첫 컬렉션"}
)

# ===== 임베딩 함수 =====
def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# ===== 데이터 삽입 =====
documents = [
    "Python은 인터프리터 언어로 가독성이 좋습니다.",
    "C는 시스템 프로그래밍과 임베디드에 쓰입니다.",
    "JavaScript는 웹 브라우저 표준 언어입니다.",
    "ARM Cortex-M은 저전력 임베디드용 MCU입니다.",
    "FreeRTOS는 임베디드용 실시간 운영체제입니다.",
]

# 각 문서에 고유 ID 필요
ids = [f"doc_{i}" for i in range(len(documents))]

# 임베딩 생성
print("임베딩 생성 중...")
embeddings = [get_embedding(doc) for doc in documents]

# Chroma에 저장
collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=[{"index": i, "type": "tech"} for i in range(len(documents))]
)

print(f"{len(documents)}개 문서 저장 완료\n")

# ===== 검색 =====
def search(query, top_k=3):
    query_emb = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )

    return results

# 테스트
queries = [
    "임베디드 개발 언어",
    "웹 개발",
    "실시간 운영체제",
]

for query in queries:
    print("=" * 60)
    print(f"질문: {query}")
    print("=" * 60)

    results = search(query, top_k=2)

    # results 구조 살펴보기
    for i, (doc, distance, metadata) in enumerate(zip(
        results['documents'][0],
        results['distances'][0],
        results['metadatas'][0]
    )):
        print(f"\n[{i+1}위] 거리: {distance:.4f}")
        print(f"  문서: {doc}")
        print(f"  메타데이터: {metadata}")
    print()

# ===== 컬렉션 정보 =====
print("=" * 60)
print(f"컬렉션 정보")
print("=" * 60)
print(f"총 문서 수: {collection.count()}")