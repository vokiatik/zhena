import re
import httpx


def list_cloud_pictures(folder_url: str) -> list[str]:
    """
    List picture URLs from a cloud folder URL.
    Supports JSON array responses and HTML directory listings with image links.
    """
    try:
        response = httpx.get(folder_url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")

        if "json" in content_type:
            data = response.json()
            if isinstance(data, list):
                return [str(url) for url in data]
            return []

        # Try regex-based HTML parsing for image file links
        img_pattern = r'href=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|bmp))["\']'
        hrefs = re.findall(img_pattern, response.text, re.IGNORECASE)
        links = []
        base = folder_url.rstrip("/")
        for href in hrefs:
            if href.startswith("http"):
                links.append(href)
            else:
                links.append(f"{base}/{href.lstrip('/')}")
        return links
    except Exception:
        return []
