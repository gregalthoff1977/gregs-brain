from pathlib import Path

from fastapi import APIRouter, Query

from config import settings

router = APIRouter(
    prefix="/api/brain",
    tags=["brain"]
)


def get_wiki_path():
    return Path(settings.WORKSPACE_PATH) / "wiki"


def summarize_text(text: str, query: str, max_chars: int = 500):
    lower_text = text.lower()
    lower_query = query.lower()

    index = lower_text.find(lower_query)

    if index == -1:
        return text[:max_chars].strip()

    start = max(0, index - 180)
    end = min(len(text), index + max_chars)

    return text[start:end].strip()


@router.get("/search")
async def search_brain(
    q: str = Query(...),
    limit: int = Query(10)
):
    wiki_path = get_wiki_path()

    if not wiki_path.exists():
        return {
            "query": q,
            "results": [],
            "error": f"Wiki path not found: {wiki_path}"
        }

    matches = []

    for file_path in wiki_path.rglob("*.md"):
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        haystack = text.lower()
        query = q.lower()

        if query not in haystack and query not in file_path.name.lower():
            continue

        title = file_path.stem.replace("-", " ").title()

        matches.append({
            "title": title,
            "summary": summarize_text(text, q),
            "source_path": str(file_path.relative_to(wiki_path)),
        })

        if len(matches) >= limit:
            break

    return {
        "query": q,
        "results": matches
    }