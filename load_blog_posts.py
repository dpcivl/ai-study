import os
import glob
import re
from pathlib import Path
import frontmatter


def load_blog_posts(directory):
    """Astro Paper 블로그 글 로드 (frontmatter 분리)"""
    files = glob.glob(f"{directory}/**/*.md", recursive=True)
    
    posts = []
    for filepath in files:
        try:
            post = frontmatter.load(filepath)
            
            posts.append({
                "filepath": filepath,
                "filename": Path(filepath).name,
                # frontmatter 메타데이터
                "title": post.get("title", "제목 없음"),
                "description": post.get("description", ""),
                "tags": post.get("tags", []),
                "pubDatetime": str(post.get("pubDatetime", "")),
                "draft": post.get("draft", False),
                # 본문 (frontmatter 제외된 마크다운)
                "content": post.content
            })
        except Exception as e:
            print(f"파일 로드 실패: {filepath} - {e}")
    
    return posts


# 테스트
if __name__ == "__main__":
    # 본인 블로그 글 경로로 수정
    # BLOG_PATH = "C:/dev/blog/src/content/blog"
    
    posts = load_blog_posts("learning_notes")
    print(f"총 {len(posts)}편 로드\n")
    
    for post in posts[:3]:  # 앞 3편만 확인
        print("=" * 60)
        print(f"파일: {post['filename']}")
        print(f"제목: {post['title']}")
        print(f"설명: {post['description']}")
        print(f"태그: {post['tags']}")
        print(f"본문 길이: {len(post['content'])}자")
        print(f"본문 미리보기: {post['content'][:150]}...")
        print()