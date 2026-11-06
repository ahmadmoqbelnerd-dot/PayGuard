# Recording guide — target 2:40

Use the working Windows setup and Qwen2.5 7B. Keep developer credentials and account passwords off camera. Screen recording is still required; this file is not a generated video.

## Before recording

Generate a fresh delivery report with `py delivery/run_checks.py`. Keep its scope paragraph. Warm the model with a harmless request. Confirm the completed USD 25 capture directly in the PayPal Sandbox dashboard and prepare the matching transaction view. Create any fresh demonstration payment only in Sandbox. Use a milestone title such as **Local signed-event receiver handoff** to state the actual scope.

You may use clearly labelled time compression for model waiting and login transitions. Do not substitute a prerecorded verdict for a live request, or imply that a generic HMAC test verifies PayPal webhooks. If using the already-completed transaction, call it a previously recorded Sandbox run. Captured milestones cannot be re-reviewed; use an uncaptured milestone for negative/uncertain cases.

## 0:00–0:20 · Problem and scope

Show the milestone checklist.

“Before collecting a freelance milestone, I want a clear answer to one question: what in the delivery report supports the agreed work? PayGuard puts the checklist, the evidence review, and PayPal's payment state in one place. Today the deliverable is a local signed-event receiver.”

## 0:20–0:50 · Non-delivery

Load the incomplete example, run the model, and show missing results and their quotes.

“This report explicitly says the signature check is absent and tests were not run. The reviewer marks the requirements missing, and the capture gate stays closed. This is a local model response, not a preset keyword score.”

## 0:50–1:10 · Illustrative evidence

Load the illustrative report and show uncertain results.

“A polished report is not enough when it declares itself illustrative. PayGuard leaves it uncertain instead of treating it as an actual delivery.”

## 1:10–1:45 · Executed evidence

Show the nine passing tests, paste the generated report, run review, and inspect the three checks.

“Here are tests we actually executed. An invalid signature is rejected before storage. A repeated idempotency key leaves one event record. The model cites the supplied results for its review. These tests cover our local component, not a deployed store or PayPal's own webhook protocol. I still review the evidence and its scope.”

## 1:45–2:25 · PayPal flow

Show Sandbox order creation, buyer approval, authorization, explicit confirmation, and completed capture. For an existing transaction, show its stored activity and receipt, not another capture click.

“PayPal creates and authorizes the Sandbox order. The review alone does not collect it: an operator must confirm permission. The app reports success only after PayPal returns COMPLETED. Here is the capture reference and the matching Sandbox transaction.”

## 2:25–2:40 · Close

“PayGuard makes the handoff easier to inspect before payment. Local AI explains the report, a person makes the decision, and PayPal provides the payment confirmation. The next step is independently collected CI evidence and authenticated buyer and seller roles.”

## Recording checklist

- Keep the final video strictly below three minutes.
- Show actual functionality, not just slides or this script.
- Keep any cuts, time compression and previous-run footage clear.
- Do not use unlicensed music, borrowed promotional clips, or invented testimonials.
- Upload a public YouTube video and verify it plays while signed out.
