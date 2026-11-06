from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from signed_webhook import receive, signature

class SignedEventTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.database = Path(self.tmp.name) / 'events.sqlite3'
        self.secret = b'local-test-fixture-key-not-for-production'
        self.body = json.dumps({'event_id':'evt_100','idempotency_key':'payment_100'}, sort_keys=True).encode()
    def tearDown(self):
        self.tmp.cleanup()
    def send(self, body=None):
        body = self.body if body is None else body
        return receive(self.database, self.secret, body, signature(self.secret, body))
    def test_valid_signature_is_processed(self):
        self.assertEqual(self.send(), (200, 'processed'))
    def test_modified_signature_is_rejected_before_storage(self):
        self.assertEqual(receive(self.database, self.secret, self.body, '0'*64), (401,'invalid_signature'))
        self.assertFalse(self.database.exists())
    def test_tampered_body_is_rejected_before_storage(self):
        self.assertEqual(receive(self.database, self.secret, self.body+b' ',signature(self.secret,self.body)), (401,'invalid_signature'))
        self.assertFalse(self.database.exists())
    def test_duplicate_idempotency_key_stores_one_record(self):
        self.assertEqual(self.send(), (200, 'processed'))
        self.assertEqual(self.send(), (200, 'already_processed'))
        with closing(sqlite3.connect(self.database)) as conn, conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM processed').fetchone()[0],1)
    def test_reused_key_with_different_event_is_rejected(self):
        self.send()
        other = json.dumps({'event_id':'evt_101','idempotency_key':'payment_100'}).encode()
        self.assertEqual(self.send(other), (409, 'idempotency_conflict'))
    def test_invalid_json_is_rejected(self):
        self.assertEqual(self.send(b'{'), (400,'invalid_json'))
    def test_missing_identifiers_are_rejected(self):
        self.assertEqual(self.send(b'{}'), (400,'missing_identifiers'))
    def test_database_connections_close_on_all_database_paths(self):
        original_connect = sqlite3.connect
        opened = []
        class TrackedConnection(sqlite3.Connection):
            closed_explicitly = False
            def close(self):
                self.closed_explicitly = True
                return super().close()
        def tracked_connect(*args, **kwargs):
            conn = original_connect(*args, factory=TrackedConnection, **kwargs)
            opened.append(conn)
            return conn
        try:
            with patch('signed_webhook.sqlite3.connect', side_effect=tracked_connect):
                self.send()
                self.assertTrue(all(c.closed_explicitly for c in opened))
                self.send()
                self.assertTrue(all(c.closed_explicitly for c in opened))
                other = json.dumps({'event_id':'evt_101','idempotency_key':'payment_100'}).encode()
                self.send(other)
                self.assertTrue(all(c.closed_explicitly for c in opened))
                self.assertEqual(len(opened), 3)
        finally:
            for conn in opened:
                conn.close()
    def test_empty_secret_is_rejected(self):
        with self.assertRaises(ValueError):
            receive(self.database,b'',self.body,'')

if __name__=='__main__':unittest.main()
