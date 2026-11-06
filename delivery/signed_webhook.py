"""Local signed-event receiver component; NOT PayPal's webhook verifier."""
from contextlib import closing
import hashlib
import hmac
import json
import sqlite3
from pathlib import Path


def signature(secret: bytes, body: bytes) -> str:
    if not secret:
        raise ValueError('Signing secret must not be empty')
    return hmac.new(secret, body, hashlib.sha256).hexdigest()


def receive(database: Path, secret: bytes, body: bytes, supplied_signature: str):
    # Authenticate the untouched bytes BEFORE decoding or handling an event.
    if not hmac.compare_digest(signature(secret, body), supplied_signature):
        return 401, 'invalid_signature'
    try:
        event = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return 400, 'invalid_json'
    if not isinstance(event, dict):
        return 400, 'invalid_event'
    event_id, key = event.get('event_id'), event.get('idempotency_key')
    if not all(isinstance(x, str) and 0 < len(x) <= 200 for x in (event_id, key)):
        return 400, 'missing_identifiers'
    digest = hashlib.sha256(body).hexdigest()
    with closing(sqlite3.connect(database, timeout=10)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS processed (event_id TEXT PRIMARY KEY, idem_key TEXT UNIQUE NOT NULL, digest TEXT NOT NULL)')
        conn.execute('BEGIN IMMEDIATE')
        existing = conn.execute('SELECT digest FROM processed WHERE event_id=? OR idem_key=?', (event_id, key)).fetchall()
        if existing:
            return (200, 'already_processed') if all(r[0] == digest for r in existing) else (409, 'idempotency_conflict')
        conn.execute('INSERT INTO processed VALUES (?,?,?)', (event_id, key, digest))
    return 200, 'processed'
