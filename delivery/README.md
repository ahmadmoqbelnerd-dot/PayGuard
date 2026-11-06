# Executed delivery component

This is an actual Python signed-event receiver function with repeatable unit tests. Its HMAC-SHA256 protocol is generic. It does **not** verify PayPal webhook certificates, call PayPal's verification endpoint, or receive public HTTP webhooks. It is not integrated into the workbench payment lifecycle. Do not present it as completed PayPal webhook support.

From the project directory, run:

```sh
python delivery/run_checks.py
```

On Windows use `py delivery/run_checks.py`. This runs nine tests and generates `delivery/delivery_report.txt` only if all tests pass. The report contains actual execution results and source/test hashes. It uses no paid services, credentials or network calls.

Tests cover valid and invalid signatures, tampered bytes, duplicate keys, conflicting keys, invalid JSON, missing identifiers, and empty signing keys. SQLite uniqueness and a transaction enforce repeat handling. There is no timestamp/nonce replay window or production key management.

Use the report as evidence **only for a milestone whose agreed scope is this local component**. It is not evidence that an unrelated store or a PayPal-specific integration was delivered. If the buyer intended a deployed store integration, retain the hold and gather the correct integration evidence instead. Do not remove these scope limits to obtain approval.

## Windows file-lock fix

SQLite connections now close explicitly after committing or rolling back, including early duplicate/conflict returns and report/test reads. A regression test checks connection closure on all three database-return paths. The report generator removes any previous report before running tests, so a failure cannot leave a stale passing report. Nine component tests and eleven workbench tests pass in the Linux development environment; native Windows execution still needs to be confirmed.
