from fastapi import APIRouter

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.get("/current")
async def get_current_strategy():
    return {
        "status": "ok",
        "message": "strategy endpoint works",
        "annual": {},
        "quarter": {},
        "month": {},
        "week": {},
        "mechanics": {
            "current_post_role": "Connector",
            "connector_count_mtd": 0,
            "anchor_count_mtd": 0
        }
    }