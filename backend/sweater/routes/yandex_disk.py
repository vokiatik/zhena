"""
Yandex Disk routes.

POST /yandex-disk/tree
    Body:  { "url": "https://disk.yandex.ru/client/disk/…", "token": "OAuth_token" }
    Returns the recursive folder tree up to the first image level.

POST /yandex-disk/import
    Body:  { "process_id": "uuid", "token": "…", "selected_paths": ["disk:/…"] }
    Imports images from the selected folders into advertisement rows.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import httpx

from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles
from sweater.services.picture.yandex_disk_service import (
    parse_disk_path,
    fetch_folder_tree,
)
from sweater.services.picture.yandex_disk_import_service import import_selected_folders

router = APIRouter(prefix="/yandex-disk", tags=["yandex-disk"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class TreeRequest(BaseModel):
    url: str
    token: str


class ImportRequest(BaseModel):
    process_id: Optional[str] = None
    token: str
    selected_paths: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/tree")
async def get_folder_tree(
    body: TreeRequest,
    user: dict = Depends(require_roles("admin", "analyst", "marketing_specialist")),
):
    """
    Return the folder tree from *body.url* up to the first image level.
    """
    disk_path = parse_disk_path(body.url.strip())
    try:
        tree = await fetch_folder_tree(body.token.strip(), disk_path)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid Yandex OAuth token.")
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Folder not found on Yandex Disk.")
        raise HTTPException(
            status_code=502,
            detail=f"Yandex Disk API error: {exc.response.status_code}",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch folder tree: {exc}")

    return tree


@router.post("/import")
async def import_from_yandex_disk(
    body: ImportRequest,
    user: dict = Depends(require_roles("admin", "analyst")),
    db: Session = Depends(get_reference_db),
):
    """
    Import images from the selected Yandex Disk folder paths.
    """
    if not body.selected_paths:
        raise HTTPException(status_code=400, detail="No folders selected.")

    try:
        result = await import_selected_folders(
            db=db,
            token=body.token.strip(),
            selected_paths=body.selected_paths,
            process_id=body.process_id,
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid Yandex OAuth token.")
        raise HTTPException(
            status_code=502,
            detail=f"Yandex Disk API error: {exc.response.status_code}",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Import failed: {exc}")

    return {"ok": True, **result}
