"""
Yandex Disk API helper.

Fetches a folder tree from a Yandex Disk path up to the depth where
images first appear.  At that depth, sibling sub-directories are still
listed (but not recursed into) because the user needs to see and select
them explicitly.

Yandex Disk REST API reference:
  GET https://cloud-api.yandex.net/v1/disk/resources
       ?path=disk:/Folder/Sub&fields=…&limit=1000
  Authorization: OAuth <token>
"""

import asyncio
import urllib.parse
from typing import Optional

import httpx

YDISK_API = "https://cloud-api.yandex.net/v1/disk/resources"
IMAGE_MEDIA_TYPES = {"image"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


# ---------------------------------------------------------------------------
# URL → disk path
# ---------------------------------------------------------------------------

def parse_disk_path(url: str) -> str:
    """
    Convert a Yandex Disk client/browser URL to a disk path suitable for
    the REST API.

    Supported formats
    -----------------
    * Private client URL:
      https://disk.yandex.ru/client/disk/Folder/Sub%20folder
      → disk:/Folder/Sub folder

    * Public link (share):
      https://disk.yandex.ru/d/XXXXXXX   (returned as-is for public API use)

    Returns the string starting with ``disk:/`` for private paths,
    or the original URL for public links so the caller can decide.
    """
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)  # decode %XX sequences

    # Private client URL: /client/disk/<path>
    if path.startswith("/client/disk/"):
        disk_path = path[len("/client/disk/"):]
        return "disk:/" + disk_path.lstrip("/")

    # Already looks like a disk path (e.g., user typed "disk:/Folder")
    if path.startswith("disk:/"):
        return path

    # Fall back: treat the whole thing as-is
    return url


# ---------------------------------------------------------------------------
# Low-level listing
# ---------------------------------------------------------------------------

# Minimal fields for tree walk – no download URL needed here, keeps payloads small
_TREE_FIELDS = (
    "_embedded.items.name,"
    "_embedded.items.type,"
    "_embedded.items.path,"
    "_embedded.items.media_type"
)

async def _list_folder_async(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    path: str,
) -> list[dict]:
    params = {"path": path, "limit": 1000, "fields": _TREE_FIELDS}
    async with sem:
        resp = await client.get(YDISK_API, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("_embedded", {}).get("items", [])


def _is_image(item: dict) -> bool:
    if item.get("type") != "file":
        return False
    if item.get("media_type") in IMAGE_MEDIA_TYPES:
        return True
    name: str = item.get("name", "").lower()
    return any(name.endswith(ext) for ext in IMAGE_EXTENSIONS)


# ---------------------------------------------------------------------------
# Recursive async tree builder
# ---------------------------------------------------------------------------

# Max simultaneous HTTP requests in flight; stays well under Yandex rate limits
_CONCURRENCY = 24


async def _fetch_node_async(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    path: str,
) -> dict:
    """
    Fetch one node and recurse into all children simultaneously.

    asyncio.gather fires ALL sibling requests at the same time without
    blocking any coroutine, so the total wall-clock time is:
        depth_of_tree × one_RTT   (plus semaphore queuing when > _CONCURRENCY)
    instead of the thread-pool approach where blocked waiters eat worker slots.
    """
    items = await _list_folder_async(client, sem, path)

    dirs   = [i for i in items if i.get("type") == "dir"]
    images = [i for i in items if _is_image(i)]
    node_name = path.rstrip("/").split("/")[-1]

    if images:
        # Leaf level – sibling folders hidden (they sit next to images)
        return {
            "name": node_name,
            "path": path,
            "folders": [],
            "files": [
                {"name": f["name"], "path": f["path"], "url": ""}
                for f in images
            ],
        }

    if not dirs:
        return {"name": node_name, "path": path, "folders": [], "files": []}

    # Fire ALL children simultaneously – no thread blocking, no starvation
    children = await asyncio.gather(
        *[_fetch_node_async(client, sem, d["path"]) for d in dirs]
    )
    # gather preserves submission order, so no re-sort needed
    return {"name": node_name, "path": path, "folders": list(children), "files": []}


async def fetch_folder_tree(token: str, path: str) -> dict:
    """Walk the folder tree. Call with ``await`` from async context."""
    headers = {"Authorization": f"OAuth {token}"}
    sem = asyncio.Semaphore(_CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        return await _fetch_node_async(client, sem, path)


# ---------------------------------------------------------------------------
# Collect leaf folders (those with files)
# ---------------------------------------------------------------------------

def collect_leaf_folders(tree: dict) -> list[dict]:
    """Return all nodes that have at least one file (leaf level)."""
    results = []

    def _walk(node: dict) -> None:
        if node["files"]:
            results.append(node)
        for child in node["folders"]:
            _walk(child)

    _walk(tree)
    return results


# Fields for import – includes the file download URL
_IMPORT_FIELDS = (
    "_embedded.items.name,"
    "_embedded.items.type,"
    "_embedded.items.path,"
    "_embedded.items.media_type,"
    "_embedded.items.file"
)


async def _get_files_async(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    path: str,
) -> list[dict]:
    params = {"path": path, "limit": 1000, "fields": _IMPORT_FIELDS}
    async with sem:
        resp = await client.get(YDISK_API, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("_embedded", {}).get("items", [])
    return [
        {"name": i["name"], "path": i["path"], "url": i.get("file", "")}
        for i in items
        if _is_image(i)
    ]


async def fetch_all_files(token: str, paths: list[str]) -> list:
    """
    Fetch file listings for all *paths* simultaneously.
    Returns a list in the same order as *paths*; each entry is either
    a ``list[dict]`` of image files or an ``Exception`` if that folder failed.
    """
    headers = {"Authorization": f"OAuth {token}"}
    sem = asyncio.Semaphore(_CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        return list(
            await asyncio.gather(
                *[_get_files_async(client, sem, p) for p in paths],
                return_exceptions=True,
            )
        )
