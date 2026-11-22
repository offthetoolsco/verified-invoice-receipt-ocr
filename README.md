# Math-Verified Invoice & Receipt OCR (Vision LLM + Decimal Checksums)

Standard Vision LLMs silently misread smudged digits (`$18.25` vs `$18.75`). **Verified Invoice & Receipt OCR** combines high-resolution Vision LLM extraction with a **deterministic Python `Decimal` arithmetic & checksum engine**—automatically triggering targeted self-healing retries whenever `qty * unit_price != line_total` or `subtotal + tax != total`.

## Key Capabilities
- **100% Math & Schema Audited:** Every extracted document returns `verification_passed` (`true`/`false`), `attempts`, and `audit_errors` so bad numbers never reach Xero, QuickBooks, NetSuite, or ERP databases.
- **Claude / Cursor / MCP Ready:** Connect directly via `https://mcp.apify.com/`—pass either public `documentUrls` or local `fileBase64` files directly from AI agent workflows.
- **Multi-Format & Multi-Page:** Supports PDF, JPG, JPEG, PNG, and WEBP up to 25MB.
- **Zero Data Retention:** Uploaded documents are permanently deleted from ephemeral disk immediately upon verification.
- **Works Out-of-the-Box or Custom:** Leave `jsonSchema` and `mathRules` blank for standard Invoices & Receipts (`vendor_name`, `tax_id`, `invoice_number`, `invoice_date`, `currency`, `items[]`, `subtotal`, `tax`, `total`), or supply your own custom JSON Schema.
