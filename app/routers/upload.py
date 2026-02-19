"""File upload router for custom data."""

import csv
import io
import json
import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SOURCE_FILES = {"crm": "customers.json", "support": "support_tickets.json", "analytics": "analytics.json"}


def parse_csv(content: str) -> list:
    """Parse CSV content into list of dicts."""
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)


@router.post("/{source}")
async def upload_data(source: str, file: UploadFile = File(...)):
    """
    Upload custom data as JSON or CSV.
    source: crm | support | analytics
    """
    if source not in SOURCE_FILES:
        raise HTTPException(status_code=400, detail="source must be crm, support, or analytics")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / SOURCE_FILES[source]

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    try:
        if file.filename and file.filename.lower().endswith(".csv"):
            data = parse_csv(text)
        else:
            data = json.loads(text)
            if not isinstance(data, list):
                data = [data]
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Uploaded %d records to %s", len(data), source)
    return {"status": "ok", "source": source, "records": len(data)}
