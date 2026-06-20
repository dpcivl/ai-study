import os
import glob
from pathlib import Path

def load_markdown_files(directory):
    """디렉토리에서 .md 파일 모두 로드"""
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

# 테스트
docs = load_markdown_files("learning_notes")
print(f"총 {len(docs)}개 파일 로드\n")

for doc in docs:
    print(f"파일: {doc['filename']}")
    print(f"길이: {len(doc['content'])}자")
    print(f"미리보기: {doc['content'][:100]}...")
    print()