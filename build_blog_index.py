import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from chunk_blog_posts import load_blog_posts, chunk_all_posts

load_dotenv()
openai_client = OpenAI()

chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 블로그용 새 컬렉션
collection = chroma_client.get_or_create_collection(
    name="blog_posts",
    metadata={"description": "본인 블로그 글 RAG"}
)

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def build_index():
    BLOG_PATH = "learning_notes"

    print("=" * 60)
    print("블로그 인덱스 빌드")
    print("=" * 60)

    # 1. 로드
    posts = load_blog_posts(BLOG_PATH)
    print(f"\n1. 글 로드: {len(posts)}편")

    # draft 글은 제외 (선택)
    posts = [p for p in posts if not p.get('draft', False)]
    print(f"  draft 제외: {len(posts)}편")

    # 2. 청크 분할
    chunks = chunk_all_posts(posts, max_chunk_size=400)
    print(f"2. 청크 분할: {len(chunks)}개")

    # 3. 임베딩
    print(f"3. 임베딩 생성 중...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk['search_text'])
        embeddings.append(emb)
        if (i + 1) % 10 == 0:
            print(f"    {i+1}/{len(chunks)}")

    # 4. Chroma 저장
    collection.upsert(
        ids=[c['chunk_id'] for c in chunks],
        embeddings=embeddings,
        documents=[c['content'] for c in chunks],
        metadatas=[{
            "title": c['title'],
            "header": c['header'],
            "source_file": c['source_file']
        } for c in chunks]
    )
    print(f"4. Chroma 저장 완료\n")

    print(f"총 청크 (DB): {collection.count()}")

if __name__ == "__main__":
    build_index()