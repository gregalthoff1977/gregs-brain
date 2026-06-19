from fastapi import APIRouter

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"]
)

@router.get("/current")
async def get_current_strategy():
    return {
        "status": "ok"
    }