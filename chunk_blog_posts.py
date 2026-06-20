import os
import glob
import re
from pathlib import Path
import frontmatter

def load_blog_posts(directory):
    files = glob.glob(f"{directory}/**/*.md", recursive=True)
    posts = []
    for filepath in files:
        try:
            post = frontmatter.load(filepath)
            posts.append({
                "filepath": filepath,
                "filename": Path(filepath).name,
                "title": post.get("title", "제목 없음"),
                "description": post.get("description", ""),
                "tags": post.get("tags", []),
                "content": post.content
            })
        except Exception as e:
            print(f"로드 실패: {filepath} - {e}")
    return posts

def split_into_chunks(text, max_chunk_size=800, overlap=100):
    """긴 텍스트를 최대 크기로 분할 (overlap 포함)"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size

        # 문장 중간에서 끊지 않도록 마침표/줄바꿈에서 끊기
        if end < len(text):
            # 가까운 줄바꿈 찾기
            last_newline = text.rfind('\n', start, end)
            last_period = text.rfind('. ', start, end)

            cut_point = max(last_newline, last_period)
            if cut_point > start + max_chunk_size // 2: # 너무 가까이 X
                end = cut_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks

def chunk_blog_post(post, max_chunk_size=800):
    """블로그 글 1편을 청크들로 분할"""
    chunks = []
    content = post['content']
    title = post['title']

    # ## 헤더로 분할
    sections = re.split(r'\n## ', content)

    # 첫 섹션 (## 전의 도입부)
    intro = sections[0].strip()
    # # 제목 라인 제거 (있을 경우)
    intro = re.sub(r'^# .|\n|', '', intro)

    # 도입부가 있으면 청크로 추가
    if len(intro) >= 50:
        intro_chunks = split_into_chunks(intro, max_chunk_size=max_chunk_size)
        for i, c in enumerate(intro_chunks):
            chunks.append({
                "title": title,
                "header": "도입",
                "content": c,
                "search_text": f"[{title}] 도입\n{c}",
                "source_file": post['filename'],
                "chunk_id": f"{post['filename']}_intro_{i}"
            })

    # 각 ## 섹션 처리
    for sec_idx, section in enumerate(sections[1:], 1):
        lines = section.split('\n', 1)
        if len(lines) < 2:
            continue

        header = lines[0].strip()
        section_content = lines[1].strip()

        if len(section_content) < 30:
            continue

        # 섹션이 너무 크면 작게 분할
        section_chunks = split_into_chunks(section_content, max_chunk_size=max_chunk_size)

        for i, c in enumerate(section_chunks):
            # 한 섹션 안에 여러 청크면 인덱스 표시
            chunk_label = f"{header}" if len(section_chunks) == 1 else f"{header} ({i+1}/{len(section_chunks)})"

            chunks.append({
                "title": title,
                "header": chunk_label,
                "content": c,
                "search_text": f"[{title}] {chunk_label}\n{c}",
                "source_file": post['filename'],
                "chunk_id": f"{post['filename']}_sec{sec_idx}_{i}"
            })
    return chunks
    

def chunk_all_posts(posts, max_chunk_size=800):
    all_chunks = []
    for post in posts:
        chunks = chunk_blog_post(post, max_chunk_size=max_chunk_size)
        all_chunks.extend(chunks)
    return all_chunks

if __name__ == "__main__":
    BLOG_PATH = "learning_notes"

    posts = load_blog_posts(BLOG_PATH)
    chunks = chunk_all_posts(posts, max_chunk_size=800)

    print(f"글 {len(posts)}편 -> 청크 {len(chunks)}개")
    print(f"청크 평균 크기: {sum(len(c['content']) for c in chunks) / len(chunks):.0f}자\n")

    # 청크 크기 분포
    sizes = [len(c['content']) for c in chunks]
    print(f"청크 크기 분포:")
    print(f"  최소: {min(sizes)}자")
    print(f"  최대: {max(sizes)}자")
    print(f"  평균: {sum(sizes)/len(sizes):.0f}자")
    print()

    # 청크 예시
    print("=" * 60)
    print("청크 예시 (앞 3개)")
    print("=" * 60)
    for chunk in chunks[:3]:
        print(f"\n출처: {chunk['source_file']}")
        print(f"제목: {chunk['title']}")
        print(f"헤더: {chunk['header']}")
        print(f"내용 ({len(chunk['content'])}자): {chunk['content'][:200]}...")
        print()