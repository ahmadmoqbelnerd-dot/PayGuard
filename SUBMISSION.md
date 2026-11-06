# PayGuard

## Tagline

Delivery evidence, a human decision, and a PayPal payment—in one milestone workflow.

## Inspiration

A freelance handoff often ends with a message saying the work is done. The buyer still has to compare a long report with the agreement and decide whether to collect or approve the next payment. PayGuard makes that comparison visible before a milestone is captured.

## What it does

An operator creates a milestone with a fixed acceptance checklist. A local AI model evaluates submitted evidence against each requirement, gives a reason, and quotes its source. Requirements are marked met, missing, or uncertain. Missing or uncertain results block the capture path.

PayPal is part of the actual workflow: the app creates a Sandbox order, sends the buyer to PayPal approval, authorizes the payment, and captures it only after the review gate and explicit operator confirmation. The app records a successful capture only when PayPal returns COMPLETED.

## How we built it

The application uses a Python standard-library server, SQLite and a browser interface. AG Grid Community presents a sortable, filterable evidence table with CSV export. A button executes the included fixed local test suite and loads its report, avoiding manual copying. Qwen2.5 7B runs locally through Ollama's structured-output API. Each requirement gets a separate model request and a stable ID. The backend rejects mismatched results and downgrades positive results without a verbatim source quote.

PayPal OAuth, Orders v2 and Payments v2 calls run on the server. Credentials stay outside source code in process environment variables. Stable request IDs are used for payment operations.

## What we demonstrated

We tested three evidence conditions: explicit non-delivery, an explicitly illustrative report, and results from an executed local signed-event component. The observed outcomes were missing, uncertain, and met respectively. Nine component tests and sixteen workbench safeguard tests passed in the development environment; the nine component tests also passed on the Windows demonstration machine.

An operator-provided export and screenshots show a USD 25 Sandbox milestone completing buyer approval, authorization and capture with status COMPLETED. This demonstrates the working payment path without moving real money.

## Challenges

Early reviews confused negative evidence with absent evidence, and assigned explanations to the wrong requirements. Separate requests and stable IDs corrected the association problem. A clearer classification rubric and labelled examples on different tasks improved the demonstrated negative and illustrative cases. This is a small functional check, not a general accuracy score.

Windows also exposed SQLite connections left open after transactions. Explicit closure and a regression test fixed the observed file-lock failure.

## Scope and next steps

The included delivery component is a generic local HMAC-signed event receiver, not a live store integration or a PayPal webhook verifier. Its test report is evidence only for that component. The application reviews supplied reports and relies on human judgment; it cannot independently prove delivery.

Next steps are independent CI evidence collection, verified PayPal webhooks, authenticated buyer and seller roles, and a larger adversarial review benchmark. These are planned capabilities, not completed features.

## Built with

Python, SQLite, HTML, CSS, JavaScript, AG Grid Community, Ollama, Qwen2.5 7B, PayPal Orders API v2, PayPal Payments API v2.

## AI disclosure

AI coding assistance was used during development. At runtime, Qwen2.5 7B assesses evidence locally through Ollama. No paid AI API is required. AI outputs are advisory, and operator confirmation is required before Sandbox capture.
