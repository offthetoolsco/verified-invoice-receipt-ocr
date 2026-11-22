import asyncio
import base64
import os
from pathlib import Path
from urllib.parse import urlparse
import httpx
from apify import Actor

ALLOWED_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MIME_TO_EXT = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

async def submit_and_poll(
    client: httpx.AsyncClient,
    gateway_url: str,
    api_key: str,
    filename: str,
    file_bytes: bytes,
    source_label: str,
    json_schema: str | None,
    math_rules: str | None,
) -> None:
    form_data = {}
    if json_schema:
        form_data["json_schema"] = json_schema
    if math_rules:
        form_data["math_rules"] = math_rules

    resp = await client.post(
        f"{gateway_url}/v1/extract?wait=true",
        headers={"X-API-Key": api_key},
        data=form_data,
        files={"file": (filename, file_bytes)},
    )

    if resp.status_code != 200:
        Actor.log.error(f"Extraction error ({resp.status_code}) for {source_label}: {resp.text}")
        return

    result = resp.json()
    job_id = result.get("job_id")
    if result.get("status") == "processing" and job_id:
        for _ in range(35):
            await asyncio.sleep(2.0)
            poll = await client.get(f"{gateway_url}/v1/jobs/{job_id}", headers={"X-API-Key": api_key})
            if poll.status_code == 200:
                result = poll.json()
                if result.get("status") in ("completed", "failed"):
                    break

    if result.get("status") == "completed":
        await Actor.push_data({"source": source_label, **result})
        Actor.log.info(
            f"Verified {source_label}! passed={result.get('verification_passed')} "
            f"latency={result.get('latency_ms')}ms attempts={result.get('attempts')}"
        )
    else:
        Actor.log.warning(f"Extraction did not complete cleanly for {source_label}: {result}")

async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        urls = [u.strip() for u in (actor_input.get("documentUrls") or []) if u and u.strip()]
        b64_raw = (actor_input.get("fileBase64") or "").strip()
        b64_name = (actor_input.get("fileName") or "invoice.pdf").strip()
        json_schema = (actor_input.get("jsonSchema") or "").strip() or None
        math_rules = (actor_input.get("mathRules") or "").strip() or None

        if not urls and not b64_raw:
            await Actor.fail(status_message="Provide at least one URL in 'documentUrls' or a file in 'fileBase64'.")
            return

        gateway_url = os.environ.get("OCR_GATEWAY_URL", "https://ocr-api.offthetoolsco.com.au").rstrip("/")
        api_key = os.environ.get("OCR_API_KEY", "").strip()
        if not api_key:
            await Actor.fail(status_message="Actor backend key not configured.")
            return

        async with httpx.AsyncClient(timeout=75.0, follow_redirects=True) as client:
            if b64_raw:
                if "," in b64_raw and b64_raw.startswith("data:"):
                    b64_raw = b64_raw.split(",", 1)[1]
                file_bytes = base64.b64decode(b64_raw)
                ext = Path(b64_name).suffix.lower()
                if ext not in ALLOWED_EXTS:
                    b64_name = f"{b64_name}.pdf"
                Actor.log.info(f"Processing base64 upload ({b64_name}, {len(file_bytes)} bytes)...")
                await submit_and_poll(client, gateway_url, api_key, b64_name, file_bytes, b64_name, json_schema, math_rules)

            for idx, doc_url in enumerate(urls, start=1):
                Actor.log.info(f"[{idx}/{len(urls)}] Downloading document: {doc_url}")
                try:
                    dl = await client.get(doc_url)
                    dl.raise_for_status()
                except Exception as exc:
                    Actor.log.error(f"Failed to download {doc_url}: {exc}")
                    continue

                ext = Path(urlparse(doc_url).path).suffix.lower()
                if ext not in ALLOWED_EXTS:
                    ctype = dl.headers.get("content-type", "").split(";")[0].strip().lower()
                    ext = MIME_TO_EXT.get(ctype, ".jpg")

                await submit_and_poll(
                    client, gateway_url, api_key, f"document_{idx}{ext}", dl.content, doc_url, json_schema, math_rules
                )

if __name__ == "__main__":
    asyncio.run(main())
