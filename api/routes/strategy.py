from fastapi import APIRouter, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


def get_sheets_service():
    if not settings.GOOGLE_SHEETS_CLIENT_EMAIL:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_SHEETS_CLIENT_EMAIL")
    if not settings.GOOGLE_SHEETS_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_SHEETS_PRIVATE_KEY")
    if not settings.LINKEDIN_STRATEGY_SHEET_ID:
        raise HTTPException(status_code=500, detail="Missing LINKEDIN_STRATEGY_SHEET_ID")

    private_key = settings.GOOGLE_SHEETS_PRIVATE_KEY.replace("\\n", "\n")

    credentials = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": settings.GOOGLE_SHEETS_CLIENT_EMAIL,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    return build("sheets", "v4", credentials=credentials)


def read_range(service, range_name: str):
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.LINKEDIN_STRATEGY_SHEET_ID,
            range=range_name,
        )
        .execute()
    )
    return result.get("values", [])


def rows_to_dict(rows):
    if not rows or len(rows) < 2:
        return {}

    output = {}

    for row in rows[1:]:
        if not row:
            continue

        key = row[0]
        value = row[1] if len(row) > 1 else ""

        if key:
            output[key] = value

    return output


@router.get("/current")
async def get_current_strategy():
    service = get_sheets_service()

    return {
        "annual": rows_to_dict(read_range(service, "00 Annual Strategy!A:B")),
        "quarter": rows_to_dict(read_range(service, "01 Quarterly Strategy!A:B")),
        "month": rows_to_dict(read_range(service, "02 Monthly Arcs!A:B")),
        "week": rows_to_dict(read_range(service, "03 Weekly Calendar!A:B")),
        "mechanics": rows_to_dict(read_range(service, "07 Editorial Mechanics!B:D")),
    }