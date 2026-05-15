import re
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

router = APIRouter()

_ALLOWED_HOSTS = {"drive.google.com", "lh3.googleusercontent.com"}

_DRIVE_FILE_RE = re.compile(r"drive\.google\.com/file/d/([^/?#]+)")

# Reuse a single client across requests for connection-pool benefits
_client = httpx.AsyncClient(follow_redirects=True, timeout=15)


def _is_allowed(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        return any(host == h or host.endswith("." + h) for h in _ALLOWED_HOSTS)
    except Exception:
        return False


def _resolve_drive_url(url: str) -> str:
    """Convert any Google Drive sharing URL to a thumbnail fetch URL."""
    m = _DRIVE_FILE_RE.search(url)
    if m:
        return f"https://drive.google.com/thumbnail?id={m.group(1)}&sz=w1000"
    return url


@router.get("/proxy/image")
async def proxy_image(url: str = Query(...)):
    """Fetch a Google Drive image server-side and stream it to the client,
    bypassing browser CORS/ORB restrictions."""
    if not _is_allowed(url):
        raise HTTPException(status_code=400, detail="URL not allowed")

    fetch_url = _resolve_drive_url(url)

    try:
        # Stream the response so the first bytes reach the browser before the
        # full image is downloaded, eliminating the full-buffering latency.
        req = _client.build_request("GET", fetch_url)
        resp = await _client.send(req, stream=True)

        content_type = resp.headers.get("content-type", "")
        if resp.status_code != 200 or not content_type.startswith("image/"):
            await resp.aclose()
            raise HTTPException(status_code=502, detail="Remote did not return an image")

        # Cache-Control lets the browser cache the image so repeat loads are instant
        headers = {
            "Cache-Control": "public, max-age=3600",
            "Content-Type": content_type,
        }
        if "content-length" in resp.headers:
            headers["Content-Length"] = resp.headers["content-length"]

        return StreamingResponse(
            resp.aiter_bytes(),
            media_type=content_type,
            headers=headers,
            background=None,
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

