"""
채점자 비교: 같은 답변 쌍을 두 모델로 채점
"""
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI()
bge_model = SentenceTransformer("BAAI/bge-m3")


def openai_embed(text):
    r = openai_client.embeddings.create(input=text, model="text-embedding-3-small")
    return np.array(r.data[0].embedding)


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# 사람이 보기에 명확한 케이스들
pairs = [
    # (기준, 답변, 사람 판단)
    ("State는 노드들이 공유하는 데이터 공간입니다",
     "그래프의 모든 노드가 읽고 쓰는 중앙 데이터 구조예요",
     "같은 의미 -> 통과여야 함"),
    ("State는 노드들이 공유하는 데이터 공간입니다",
     "State는 현재 실행 중인 노드의 위치를 나타냅니다",
     "틀린 답 -> 탈락이어야 함"),
    ("청크를 나누는 이유는 의미 평균화를 막기 위해서입니다",
     "긴 문서를 통째로 임베딩하면 의미가 흐려져서 나눕니다",
     "같은 의미 -> 통과여야 함"),
]

print(f"{'사람 판단':<25} {'OpenAI':<10} {'BGE-M3':<10}")
print("-" * 50)

for ref, ans, human in pairs:
    # OpenAI 채점
    sim_openai = cosine(openai_embed(ref), openai_embed(ans))
    # BGE-M3 채점
    embs = bge_model.encode([ref, ans])
    sim_bge = cosine(embs[0], embs[1])

    print(f"{human:<25} {sim_openai:.4f}    {sim_bge:.4f}")