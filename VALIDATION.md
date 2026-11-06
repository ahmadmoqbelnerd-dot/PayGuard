# Validation record — 6 November 2026

## Evidence reviewed

The operator supplied screenshots of local inference, Windows test execution, PayPal buyer approval/authorization activity, and a completed capture. A final JSON export from the same milestone had state CAPTURED, capture_status COMPLETED, amount USD 25.00, review version 3 and model qwen2.5:7b. It contained three met checks.

Checks performed on the supplied export:

- Recomputed SHA-256 of the evidence text matched its evidence_hash.
- All three quoted excerpts occurred in the evidence text.
- An authorization reference and capture reference were present.
- Activity and final state were consistent with the exported COMPLETED result.

These are consistency checks of operator-supplied artifacts. The export is editable, its hash is not a digital signature, and it is not an independently authenticated PayPal statement. Transaction references and buyer approval links are omitted from this public document. The operator should verify the matching transaction directly in the Sandbox dashboard before recording the final demo.

## Tests

Eleven workbench tests passed in the development environment. Nine delivery-component tests passed there and on the Windows operator machine. The supplied Windows screenshot recorded 9 tests, OK, with a generated report. No tests were skipped in that reported run.

The signed-event component checks generic HMAC-SHA256 signatures before processing and stores at most one record for an identical event/idempotency key. Its tests do not use PayPal webhooks and do not prove a store deployment. The development report generator executes tests; the AI itself does not.

## Interpretation

The observed negative, illustrative, and local positive cases exercise useful paths, but do not establish accuracy across unseen contracts. The final positive explanation for signature verification cites the accepted valid signature; the full report additionally contains the rejection-before-processing test. Quote presence alone does not establish that every explanation fully supports its criterion. Human reviewers must examine the report, scope and underlying tests.

## Still to complete

- Direct dashboard cross-check of the completed Sandbox capture.
- A broader set of unseen, contradictory and adversarial review cases.
- Public source repository and public YouTube demo.
- Final Devpost submission and confirmation.

The application is a local prototype. Nothing in this record claims production readiness, regulated escrow, real-money collection, guaranteed model safety, or a competition win.

## Release 4.1 regression checks

After the observed Sandbox run, AG Grid and the fixed-suite execution button were integrated. The workbench suite now has sixteen passing tests. The additional tests cover edited/missing evidence, inconsistent stored evidence, failed re-reviews and execution-report loading. The previous Sandbox completion remains evidence for the earlier payment path; it is not a newly executed transaction on release 4.1. UI rendering of the upgraded grid has not been visually validated here.
