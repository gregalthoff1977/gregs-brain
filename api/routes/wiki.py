from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

@router.get("/brain")
def brain():
    root = Path("/data/gregs-brain-workspace/wiki")

    return {
        "overview": "/wiki/overview.md",
        "insights": "/wiki/inbox-insights.md",
        "log": "/wiki/log.md",
        "files": sorted([
            str(p.relative_to(root))
            for p in root.glob("**/*.md")
        ])
    }