"""Run actual local component tests and write their measured results."""
from contextlib import closing
import datetime
import hashlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from signed_webhook import receive, signature

ROOT = Path(__file__).resolve().parent
# Never leave an older passing report after a failing run.
(ROOT/'delivery_report.txt').unlink(missing_ok=True)
stream = io.StringIO()
suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_signed_webhook.py')
result = unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
print(stream.getvalue())
if not result.wasSuccessful():
    print('Tests failed. No passing delivery report was generated.')
    sys.exit(1)
with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / 'events.sqlite3'
    secret = b'local-report-fixture'
    body = json.dumps({'event_id':'evt_report','idempotency_key':'payment_report'},sort_keys=True).encode()
    invalid = receive(db,secret,body,'0'*64)
    before_storage = not db.exists()
    valid = receive(db,secret,body,signature(secret,body))
    duplicate = receive(db,secret,body,signature(secret,body))
    with closing(sqlite3.connect(db)) as conn, conn:
        count = conn.execute('SELECT COUNT(*) FROM processed').fetchone()[0]
report = '\n'.join([
    'Executed delivery verification — local signed-event receiver component',
    'Run time (UTC): ' + datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'Scope: the included delivery/signed_webhook.py component was executed against local inputs. This is not a live store test and is not a PayPal webhook verification implementation.',
    f'Webhook signature verification before processing: an invalid signature returned HTTP {invalid[0]} ({invalid[1]}); no storage was created before rejection: {before_storage}. A valid HMAC-SHA256 signature returned HTTP {valid[0]} ({valid[1]}) and the event was stored.',
    f'Duplicate payment-event handling using an idempotency key: the same signed event and key were sent twice. The second call returned HTTP {duplicate[0]} ({duplicate[1]}). Stored event count after both calls: {count}.',
    f'Unit test execution: {result.testsRun} tests ran; failures={len(result.failures)}; errors={len(result.errors)}; skipped={len(result.skipped)}. Result: PASS.',
    'Source SHA-256: ' + hashlib.sha256((ROOT/'signed_webhook.py').read_bytes()).hexdigest(),
    'Test SHA-256: ' + hashlib.sha256((ROOT/'test_signed_webhook.py').read_bytes()).hexdigest(),
    'The report records local execution only. It does not independently establish deployment or external service behavior.',
    '', 'Raw test output:', stream.getvalue(),
])
(ROOT/'delivery_report.txt').write_text(report,encoding='utf-8')
print('Written: ' + str(ROOT/'delivery_report.txt'))
