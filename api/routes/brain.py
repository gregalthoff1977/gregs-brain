from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/api/brain",
    tags=["brain"]
)


@router.get("/search")
async def search_brain(
    q: str = Query(...)
):
    return {
        "query": q,
        "results": [
            {
                "title": "Placeholder",
                "summary": f"No search implemented yet for '{q}'"
            }
        ]
    }