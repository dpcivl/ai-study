import os
import glob
import re
from pathlib import Path

def load_markdown_files(directory):
    files = glob.glob(f"{directory}/**/*.md", recursive=True)
    documents = []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        documents.append({
            "filepath": filepath,
            "filename": Path(filepath).name,
            "content": content
        })
    return documents

def chunk_by_headers(content, filename):
    """## 헤더 단위로 청크 분할"""
    chunks = []

    # ## 헤더로 분할
    sections = re.split(r'\n## ', content)

    # 첫 번째 섹션은 # 제목과 그 다음 내용
    title_match = re.match(r'# (.+)', sections[0])
    title = title_match.group(1) if title_match else filename

    # 나머지 섹션들 처리
    for i, section in enumerate(sections[1:], 1):
        # 첫 줄이 헤더, 나머지가 내용
        lines = section.split('\n', 1)
        if len(lines) >= 2:
            header = lines[0].strip()
            content_text = lines[1].strip()
        else:
            header = lines[0].strip()
            content_text = ""

        # 너무 짧은 청크는 스킵
        if len(content_text) < 30:
            continue

        chunks.append({
            "title": title,
            "header": header,
            "content": content_text,
            # 검색용으로는 제목+헤더+내용 합치기 (맥락 풍부화)
            "search_text": f"[{title}] {header}\n{content_text}",
            "source_file": filename,
            "chunk_id": f"{filename}_{i}"
        })

    return chunks

def chunk_all_documents(documents):
    """모든 문서를 청크로 분할"""
    all_chunks = []
    for doc in documents:
        chunks = chunk_by_headers(doc['content'], doc['filename'])
        all_chunks.extend(chunks)
    return all_chunks

# 테스트
docs = load_markdown_files("learning_notes")
chunks = chunk_all_documents(docs)

print(f"문서 {len(docs)}개 -> 청크 {len(chunks)}개\n")

# 청크 확인
for chunk in chunks[:5]:
    print("=" * 60)
    print(f"파일: {chunk['source_file']}")
    print(f"제목: {chunk['title']}")
    print(f"헤더: {chunk['header']}")
    print(f"내용 길이: {len(chunk['content'])}자")
    print(f"내용 미리보기: {chunk['content'][:100]}...")
    print()