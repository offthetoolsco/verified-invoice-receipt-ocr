# Invoice & Receipt OCR API — Math-Verified Bookkeeping OCR & MCP Server

Stop letting raw Vision LLMs silently hallucinate bookkeeping totals. **Verified Invoice & Receipt OCR** is a production-ready **Invoice & Receipt OCR API** and zero-install **MCP Server** engineered to **Extract Line Items to JSON** with deterministic mathematical certainty. Built for accountants, developers, and AI agents, it pairs multimodal Vision LLMs with a Python `Decimal` arithmetic verification engine that guarantees extracted numbers add up before hitting your general ledger.

---

## ⚡ Instant 1-Click Trial (Zero Setup)

Experience zero-friction verification in under 5 seconds:
1. Navigate to the **Input** tab on this Apify Store page.
2. The `documentUrls` input field is already prefilled with a live **Australian GST tax invoice**:
   `https://ocr-api.offthetoolsco.com.au/sample-invoice.jpg`
3. Click **Save & Run** (or **Start**).
4. Inspect the clean, mathematically audited JSON in the **Dataset** tab—complete with line items, tax breakdown, and verification proofs.

---

## 🧠 Why Math-Verified Bookkeeping OCR Beats Raw Vision LLMs

Raw Vision LLM prompts (GPT-4o, Claude 3.5 Sonnet, Gemini Flash) are impressive at recognizing messy handwriting and complex table layouts, but they have a fatal flaw for accounting and bookkeeping: **they hallucinate arithmetic**.

- **Digit Ambiguity & Smudges:** A fold in a receipt or a low-resolution scan easily turns `$18.25` into `$18.75`. A raw LLM outputs the wrong digit without blinking, leading to reconciliation discrepancies.
- **Float Inaccuracies:** LLMs predict tokens probabilistically. They cannot guarantee that `3 × $14.99` equals `$44.97` rather than `$44.99`.
- **Silent Ledger Corruption:** When unverified JSON is piped directly into Xero, QuickBooks, MYOB, or NetSuite, reconciliation errors compound and require costly manual accountant audits.

### How Our Deterministic Math Engine Works
1. **High-Resolution Vision Extraction:** The document is parsed into an initial structured JSON payload capturing vendor information, tax registration numbers, invoice dates, currencies, and individual line items.
2. **Deterministic `Decimal` Auditing:** Our backend runs exact Python `Decimal` arithmetic across all extracted values:
   - Line-Item Checksum: `qty * unit_price == line_total` (for every single item)
   - Totals Reconciliation: `subtotal + tax == total`
   - Tax Rate Integrity: Checks that calculated tax matches declared rates (e.g., 10% GST).
3. **Targeted Self-Healing Retries:** If any equation fails, the engine automatically triggers targeted re-prompting with arithmetic feedback (e.g., *"Line 2 failed checksum: qty 4 * unit 12.50 = 50.00, but line_total was read as 55.00. Re-examine line 2 bounding box."*).
4. **Audit Protection:** If digits remain irreconcilable after retries, the payload is flagged with `verification_passed: false` and includes a clear `audit_errors` array. Corrupt numbers are stopped before they corrupt your accounting system.

---

## 🤖 Zero-Install Streamable HTTP MCP Server

Connect this Actor directly to **Cursor**, **Claude Desktop**, **Antigravity**, **Windsurf**, or **Claude Code** via Apify's native Streamable HTTP MCP integration. Your AI agents can extract invoices and receipts on the fly using either remote URLs or raw base64 uploads.

### Streamable HTTP Endpoint
```text
https://mcp.apify.com/?tools=fetch-actor-details,offthetoolsco/verified-invoice-receipt-ocr
```

### 1-Click CLI Setup
```bash
# Add to Cursor
apify mcp install cursor --tools fetch-actor-details,offthetoolsco/verified-invoice-receipt-ocr

# Add to Claude Code
apify mcp install claude-code --tools fetch-actor-details,offthetoolsco/verified-invoice-receipt-ocr

# Add to VS Code
apify mcp install vscode --tools fetch-actor-details,offthetoolsco/verified-invoice-receipt-ocr
```

### Manual Configuration (`claude_desktop_config.json` / `cursor.json`)
```json
{
  "mcpServers": {
    "verified-ocr": {
      "url": "https://mcp.apify.com/?tools=fetch-actor-details,offthetoolsco/verified-invoice-receipt-ocr",
      "headers": {
        "Authorization": "Bearer YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

### Local Stdio MCP (via `uvx` / `pipx`)
Prefer a local stdio MCP server? Run directly with `uvx`:
```json
{
  "mcpServers": {
    "verified-ocr": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/offthetoolsco/verified-invoice-receipt-ocr", "verified-ocr"],
      "env": {
        "OCR_API_KEY": "YOUR_OCR_API_KEY"
      }
    }
  }
}
```
Or run from your terminal:
```bash
uvx --from git+https://github.com/offthetoolsco/verified-invoice-receipt-ocr verified-ocr
```

---

## 💰 Transparent Pay-Per-Event Pricing

No recurring subscription fees. No seat minimums. No monthly credit expirations.

- **$0.03 per verified document** (Pay-Per-Event via Apify platform).
- **$0.00005 Actor start fee** (nominal compute charge).
- **Zero Charge for Verification Retries:** Multi-pass self-healing arithmetic audits are included in the single document fee.
- Pay only for successful extractions written to your dataset.

---

## 📥 Input Parameters

| Parameter | Type | Required | Description |
|:---|:---|:---:|:---|
| `documentUrls` | `array` of `string` | Optional* | Direct URLs to invoices, receipts, or PDFs. Prefilled with sample invoice. |
| `fileBase64` | `string` | Optional* | Base64-encoded document or data URI (perfect for local files in AI Agent workflows). |
| `fileName` | `string` | Optional | File name when providing `fileBase64` (e.g. `tax-invoice.pdf`). Defaults to `invoice.pdf`. |
| `jsonSchema` | `string` | Optional | Custom JSON Schema string. Omit to use the standard invoice & line-items schema. |
| `mathRules` | `string` | Optional | Custom arithmetic verification rules array. Omit for standard `qty * unit == total` checks. |

*\* Provide either `documentUrls` or `fileBase64`.*

---

## 📤 Verified Output Schema

Every document processed yields a dataset entry containing full audit telemetry and extracted line items:

```json
{
  "source": "https://ocr-api.offthetoolsco.com.au/sample-invoice.jpg",
  "job_id": "job_8f2b3e41a9c0",
  "status": "completed",
  "verification_passed": true,
  "attempts": 1,
  "latency_ms": 1420,
  "data": {
    "vendor_name": "Apex Electrical Contracting Pty Ltd",
    "tax_id": "ABN 84 123 456 789",
    "invoice_number": "INV-2026-0842",
    "invoice_date": "2026-11-20",
    "due_date": "2026-12-04",
    "currency": "AUD",
    "items": [
      {
        "description": "Commercial Switchboard Upgrade & Safety Switch Installation",
        "quantity": 1.0,
        "unit_price": 850.00,
        "line_total": 850.00
      },
      {
        "description": "Heavy Duty 20A Circuit Breakers",
        "quantity": 4.0,
        "unit_price": 45.00,
        "line_total": 180.00
      },
      {
        "description": "Compliance Testing & Electrical Safety Certificate",
        "quantity": 1.0,
        "unit_price": 120.00,
        "line_total": 120.00
      }
    ],
    "subtotal": 1150.00,
    "tax": 115.00,
    "total": 1265.00
  },
  "audit_errors": []
}
```

### Self-Healing & Discrepancy Flagging
When math fails even after self-healing passes, the document status alerts your system:
```json
{
  "source": "receipt_photo.jpg",
  "verification_passed": false,
  "attempts": 2,
  "audit_errors": [
    "Line 2: 4 * 45.00 = 180.00 != extracted line_total 170.00",
    "Totals mismatch: subtotal (1150.00) + tax (115.00) = 1265.00 != extracted total (1255.00)"
  ]
}
```

---

## 🔒 Enterprise Privacy & Zero Data Retention

- **Ephemeral Processing:** Uploaded images and PDFs are loaded into memory or transient ephemeral storage solely for the duration of the extraction request.
- **Immediate Disk Purge:** All temporary files are permanently wiped immediately upon completion of the verification pass.
- **Zero Training:** Your confidential invoices, financial data, and vendor details are never used to train machine learning models.

---

## 🚀 Getting Started

1. Click **Try for free** or **Save & Run** above with the prefilled sample.
2. Integrate with Python, Node.js, cURL, or MCP using the Apify API client.
3. For support or custom math rules, contact [Off The Tools Co.](https://offthetoolsco.com.au).
