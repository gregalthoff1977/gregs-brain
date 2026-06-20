from fastapi import APIRouter

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.get("/current")
async def get_current_strategy():
    return {
        "annual": {
            "year": 2026,
            "objective": "Become recognized as a credible voice at the intersection of systems thinking, design leadership, and AI-enabled creative work."
        },
        "quarter": {
            "theme": "Design leadership becomes systems leadership"
        },
        "month": {
            "question": "How do systems help teams create better work?"
        },
        "week": {
            "goal": "Generate connector posts that build toward the monthly anchor."
        },
        "mechanics": {
            "connector_target_min": 6,
            "connector_target_max": 8,
            "anchor_target": 1,
            "anchor_position": "final_week",
            "current_post_role": "Connector",
            "connector_count_mtd": 0,
            "anchor_count_mtd": 0
        }
    }