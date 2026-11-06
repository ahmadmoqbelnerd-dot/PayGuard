# PayGuard

**Review delivery evidence before collecting a freelance milestone payment.**
Built by Ahmad Moqbel for the PayPal AI Hackathon.

PayGuard connects a fixed acceptance checklist, a local AI evidence review, and PayPal's authorize/capture flow. The reviewer returns a status, reason, and source quote for each requirement. Missing or uncertain requirements block capture. A human operator must confirm review and permission before a sandbox payment can be collected.

## Quick start

Requirements: Python 3.10+, [Ollama](https://ollama.com/download), and a computer able to run Qwen2.5 7B. Model downloads require internet and disk space; local inference uses your hardware. No paid AI API account is required. The demonstrated setup used Windows, 12 GB RAM and an RTX 2060 with 6 GB VRAM. Close memory-heavy applications first. This is a tested configuration, not a performance guarantee.

Download the model once:

```sh
ollama pull qwen2.5:7b
```

From this repository directory, start the server. On Windows PowerShell:

```powershell
$env:OLLAMA_MODEL = 'qwen2.5:7b'
py server.py
```

On macOS/Linux:

```sh
OLLAMA_MODEL=qwen2.5:7b python3 server.py
```

Open **http://127.0.0.1:8080**. Keep Ollama and the server running. Opening `index.html` directly does not connect the backend. No npm or pip dependencies are needed for the application. Ollama and model weights are separate prerequisites. The model can take several minutes to review a milestone.

## Configure PayPal Sandbox

Use a free developer application at https://developer.paypal.com/dashboard/. Stay in **Sandbox** mode. Use separate sandbox merchant and buyer accounts. Never paste credentials into a submission, source file, or recording.

Stop the server with Ctrl+C. In the same PowerShell session, enter credentials through these prompts:

```powershell
$env:PAYPAL_CLIENT_ID = Read-Host 'Sandbox Client ID'
$secret = Read-Host 'Sandbox Client Secret' -AsSecureString
$env:PAYPAL_CLIENT_SECRET = [System.Net.NetworkCredential]::new('', $secret).Password
$env:OLLAMA_MODEL = 'qwen2.5:7b'
py server.py
```

On other platforms, provide `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and `OLLAMA_MODEL` through your process environment. Refresh the page after restarting. The connections card reports configuration presence, not a live connectivity check.

## Try the complete flow

1. Create a milestone with an amount and one requirement per line. Requirements are fixed on creation.
2. Load the incomplete example and run the review. Explicit non-delivery should be marked missing. The detailed example is declared illustrative and should remain uncertain.
3. For a positive test, click **Run & load verified local checks** to execute the included component tests and load their report, or run the report generator from a terminal. Read its scope first: it is not a deployed store or PayPal webhook verifier.
4. Create a PayPal order and open buyer approval. Sign in as a sandbox buyer and approve.
5. Return and select the **same milestone** from the list. Click Confirm with PayPal to obtain authorization.
6. When the review is ready, review its reasons and sources, attest to permission, then click Capture once. Only `COMPLETED` is treated as captured. Save the capture id and check the transaction in your sandbox dashboard.
7. Download the review record. It contains the evidence, model verdicts and payment references. Keep account-specific exports private unless you choose to share them.

Authorization is a temporary hold, not regulated escrow or a payment guarantee. PayPal recommends capture within the initial three-day honor period. Expiration, reauthorization and refunds are not implemented.

## Tests and delivery evidence

Workbench safeguards:

```sh
python -m unittest -v
```

Sixteen tests cover capture gates, human confirmation, failed remote calls, repeat capture handling, requirement IDs, citation occurrence and stale reviews. Payment and model calls are mocked in these tests.

Local delivery component:

```sh
python delivery/run_checks.py
```

On Windows use `py` in place of `python` where needed. Nine tests check the generic signed-event component, including signature validation, duplicate handling and explicit SQLite closure. A passing run writes `delivery/delivery_report.txt` with measured results and source hashes. A failing run removes any previous report. See `delivery/README.md` for limitations.

## Observed validation

On 6 November 2026, operator-provided screenshots and an exported review record showed:

- Qwen2.5 7B running locally through Ollama.
- The explicit negative example classified missing; the declared illustrative example classified uncertain.
- A report from nine passing local-component tests classified met for the three supplied requirements.
- A USD 25 PayPal Sandbox order approved, authorized and captured with status COMPLETED.
- The exported evidence hash matched the supplied text, and each displayed quote occurred in that text.

This is a small functional demonstration, not a statistical accuracy benchmark. The payment outcome was observed through the application's exported PayPal response and screenshots; an independent query of PayPal's dashboard has not been performed by the reviewer. No real money was collected. The test component does not prove a live store integration. Public account identifiers and credentials are intentionally excluded from this repository.

## Architecture and limits

- Python standard-library loopback HTTP server, SQLite persistence, and a single-operator UI.
- Ollama structured output, one request per requirement, stable IDs, and verbatim-quote checks. Unknown or duplicated IDs are rejected. Citation matching checks occurrence, not factual truth or semantic relevance.
- PayPal Sandbox OAuth, Orders v2 create/authorize, and Payments v2 capture run server-side. Stable PayPal request ids support retry handling. This is not a claim of complete recovery from all payment failures.
- Secrets stay in the server process. Mutations require a per-run local request token. The application has no multi-user accounts or independent buyer-consent records; the operator attests to permission.
- The AI reviews reports; it does not execute submitted code, independently collect evidence, or guarantee quality. Evidence can be misleading, including malicious instructions. Human judgment remains necessary.
- The delivery component uses generic HMAC signatures. It is not a PayPal webhook verifier and is not wired into payment status.
- No verified PayPal webhooks, automatic pending-payment reconciliation, deployment verification, production authentication, or immutable audit ledger is implemented. Records and exports are editable.

Do not expose this development server publicly. Do not use this prototype to collect real payments. For an ambiguous capture, inspect the sandbox dashboard before retrying. Never create another milestone simply to bypass a pending payment.

## Submission materials

- `SUBMISSION.md`: project description and tool disclosure.
- `DEMO_SCRIPT.md`: timed recording outline and narration.
- `SUBMISSION_CHECKLIST_AR.md`: remaining publication steps.
- `VALIDATION.md`: evidence provenance and limits.

Developed with AI coding assistance. Runtime reviews use Qwen through Ollama. MIT covers this repository's code; model weights, Ollama and PayPal have separate licenses and terms.

References: https://github.com/ollama/ollama/blob/main/docs/api.md and https://developer.paypal.com/checkout/delay-capture/.

## Release 4.1

Integrated AG Grid Community 31.3.2 with sorting, filtering and CSV export; scripts and styles load from jsDelivr, so the grid needs internet access. The original text review remains available if the grid library is unavailable. CSV fields that could be interpreted as formulas are prefixed for safer spreadsheet opening.

A UI button executes only the fixed, included delivery/run_checks.py file; it does not execute uploaded or user-supplied code. The report covers that local component only.

Capture now requires a nonempty evidence string, a stored evidence record, and matching hashes of submitted and stored evidence. A failed re-review clears any prior ready verdict. Sixteen workbench tests pass, including these safeguards and the local-check action. These are local automated checks; release 4.1 has not repeated the prior full Sandbox transaction or received visual browser validation. Milestone labels include state and an ID suffix to distinguish identical titles.
