"""
VerifiedOCR - Local Stdio MCP Server
Calls https://ocr-api.offthetoolsco.com.au with OCR_API_KEY.
"""
import asyncio
import base64
import json
import os
from pathlib import Path
from urllib.parse import urlparse
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "VerifiedOCR",
    instructions="Math-verified invoice and receipt OCR extraction engine with deterministic Decimal arithmetic checksums.",
)

DEFAULT_GATEWAY_URL = "https://ocr-api.offthetoolsco.com.au"
ALLOWED_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}

@mcp.tool()
async def extract_invoice(
    file_path: str = "",
    file_url: str = "",
    file_base64: str = "",
    file_name: str = "document.pdf",
    json_schema: str = "",
    math_rules: str = "",
) -> str:
    """Extract structured data from an invoice or receipt with deterministic Decimal arithmetic verification.

    Args:
        file_path: Local filesystem path to an invoice/receipt file (PDF, JPG, PNG, WEBP).
        file_url: Public URL to an invoice or receipt image/PDF.
        file_base64: Raw base64 string or data URI of the document.
        file_name: Optional file name (used when file_base64 or file_url is provided).
        json_schema: Optional custom JSON Schema string to enforce.
        math_rules: Optional custom arithmetic rules JSON array.
    """
    api_key = os.environ.get("OCR_API_KEY", "").strip()
    if not api_key:
        return json.dumps({
            "error": "OCR_API_KEY environment variable is not set. Please set OCR_API_KEY to your VerifiedOCR API key."
        })

    gateway_url = os.environ.get("OCR_GATEWAY_URL", DEFAULT_GATEWAY_URL).rstrip("/")
    file_bytes: bytes | None = None
    target_name = file_name

    if file_path:
        p = Path(file_path).expanduser().resolve()
        if not p.is_file():
            return json.dumps({"error": f"File not found: {file_path}"})
        target_name = p.name
        file_bytes = p.read_bytes()
    elif file_url:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as dl_client:
            res = await dl_client.get(file_url)
            if res.status_code != 200:
                return json.dumps({"error": f"Failed to download document from {file_url}: HTTP {res.status_code}"})
            file_bytes = res.content
            parsed_path = urlparse(file_url).path
            if Path(parsed_path).suffix.lower() in ALLOWED_EXTS:
                target_name = Path(parsed_path).name
    elif file_base64:
        raw = file_base64.strip()
        if "," in raw and raw.startswith("data:"):
            raw = raw.split(",", 1)[1]
        try:
            file_bytes = base64.b64decode(raw)
        except Exception as exc:
            return json.dumps({"error": f"Invalid base64 payload: {exc}"})
    else:
        return json.dumps({"error": "Provide at least one of: file_path, file_url, or file_base64."})

    ext = Path(target_name).suffix.lower()
    if ext not in ALLOWED_EXTS:
        target_name = f"{target_name}.pdf"

    form_data = {}
    if json_schema:
        form_data["json_schema"] = json_schema
    if math_rules:
        form_data["math_rules"] = math_rules

    async with httpx.AsyncClient(timeout=75.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{gateway_url}/v1/extract?wait=true",
            headers={"X-API-Key": api_key},
            data=form_data,
            files={"file": (target_name, file_bytes)},
        )

        if resp.status_code != 200:
            return json.dumps({
                "status": "failed",
                "status_code": resp.status_code,
                "error": resp.text,
            })

        result = resp.json()
        job_id = result.get("job_id")
        if result.get("status") == "processing" and job_id:
            for _ in range(35):
                await asyncio.sleep(2.0)
                poll = await client.get(
                    f"{gateway_url}/v1/jobs/{job_id}",
                    headers={"X-API-Key": api_key},
                )
                if poll.status_code == 200:
                    result = poll.json()
                    if result.get("status") in ("completed", "failed"):
                        break

        return json.dumps(result, indent=2)

def main() -> None:
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
