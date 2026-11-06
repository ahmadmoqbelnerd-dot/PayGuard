import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import server

class PaymentGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = server.DB
        server.DB = Path(self.tmp.name) / 'test.sqlite3'
        self.case = server.act('new', {'criteria': 'Signature validated\nDuplicates blocked', 'amount': '25'})
    def tearDown(self):
        server.DB = self.old
        self.tmp.cleanup()
    def test_missing_evidence_downgrades_positive_claim(self):
        out = server.validate_audit({'checks':[{'requirement_id':'R1','status':'met','quote':'invented evidence'}, {'requirement_id':'R2','status':'missing'}]}, self.case['criteria'], 'No tests')
        self.assertEqual(out['checks'][0]['status'], 'uncertain')
        self.assertFalse(out['ready'])
    def test_capture_blocked_without_ai_or_authorization(self):
        with patch('server.paypal') as remote:
            with self.assertRaises(ValueError):
                server.act('capture', {'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
            remote.assert_not_called()
    def test_human_permission_is_required(self):
        self.case.update(evidence='reviewed text',evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(),authorization_id='test',review={'ready':True,'version':server.REVIEW_VERSION})
        server.save(self.case)
        with patch('server.paypal') as remote:
            with self.assertRaises(ValueError): server.act('capture', {'id':self.case['id']})
            remote.assert_not_called()
    def test_no_false_payment_success(self):
        self.case.update(evidence='reviewed text',evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(),authorization_id='test',review={'ready':True,'version':server.REVIEW_VERSION})
        server.save(self.case)
        with patch('server.paypal', side_effect=ValueError('declined')):
            with self.assertRaises(ValueError): server.act('capture', {'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
        self.assertNotEqual(server.load(self.case['id'])['state'],'CAPTURED')
    def test_capture_requires_completed_status_and_is_idempotent(self):
        self.case.update(evidence='reviewed text',evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(),authorization_id='test',review={'ready':True,'version':server.REVIEW_VERSION})
        server.save(self.case)
        with patch('server.paypal', return_value={'id':'CAP-1','status':'COMPLETED'}) as remote:
            server.act('capture', {'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
            server.act('capture', {'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
            self.assertEqual(remote.call_count,1)
        self.assertEqual(server.load(self.case['id'])['capture_id'],'CAP-1')
    def test_reordered_results_are_matched_by_id(self):
        out = server.validate_audit({'checks':[{'requirement_id':'R2','status':'missing','reason':'second'}, {'requirement_id':'R1','status':'met','quote':'signed','reason':'first'}]},self.case['criteria'],'signed')
        self.assertEqual(out['checks'][0]['reason'],'first')
        self.assertEqual(out['checks'][1]['reason'],'second')
    def test_duplicate_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            server.validate_audit({'checks':[{'requirement_id':'R1'}, {'requirement_id':'R1'}]},self.case['criteria'],'text')
    def test_old_review_cannot_unlock_capture(self):
        self.case.update(evidence='reviewed text',evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(),authorization_id='test',review={'ready':True})
        server.save(self.case)
        with patch('server.paypal') as remote:
            with self.assertRaises(ValueError):server.act('capture',{'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
            remote.assert_not_called()
    def test_each_requirement_is_requested_separately(self):
        results=[{'message':{'content':'{"requirement_id":"R1","status":"missing","quote":"not implemented","reason":"not implemented"}'}}, {'message':{'content':'{"requirement_id":"R2","status":"uncertain","quote":"","reason":"no evidence"}'}}]
        with patch('server.request_json',side_effect=results) as remote:
            out=server.audit(self.case['criteria'],'not implemented')
            self.assertEqual(remote.call_count,2)
            for i,call in enumerate(remote.call_args_list):
                payload=__import__('json').loads(call.args[1]['messages'][-1]['content'])
                self.assertEqual(payload['requirement_id'],f'R{i+1}')
                self.assertNotIn('requirements',payload)
                self.assertIn('negative evidence', call.args[1]['messages'][0]['content'])
                self.assertGreater(len(call.args[1]['messages']), 2)
        self.assertFalse(out['ready'])
    def test_invalid_amounts_and_empty_requirements(self):
        for amount in ['NaN','-2','0','25.123']:
            with self.assertRaises(ValueError):server.act('new',{'criteria':'test','amount':amount})
        with self.assertRaises(ValueError):server.act('new',{'criteria':'','amount':'25'})
    def test_missing_requirements_fail_closed(self):
        with self.assertRaises(ValueError):server.validate_audit({'checks':[]},self.case['criteria'],'text')


    def test_capture_blocked_if_evidence_edited_after_review(self):
        self.case.update(
            authorization_id='test',
            evidence='original text',
            evidence_hash=server.hashlib.sha256(b'original text').hexdigest(),
            review={'ready': True, 'version': server.REVIEW_VERSION}
        )
        server.save(self.case)
        with patch('server.paypal') as remote:
            with self.assertRaises(ValueError):
                server.act('capture', {
                    'id': self.case['id'],
                    'buyer_confirmed': True,
                    'evidence': 'tampered text after review'
                })
            remote.assert_not_called()

    def test_failed_rereview_clears_previous_ready_state(self):
        self.case.update(
            authorization_id='test',
            review={'ready': True, 'version': server.REVIEW_VERSION}
        )
        server.save(self.case)
        with patch('server.audit', side_effect=ValueError('Ollama timed out')):
            with self.assertRaises(ValueError):
                server.act('review', {'id': self.case['id'], 'evidence': 'new unverified text'})
        reloaded = server.load(self.case['id'])
        self.assertNotIn('review', reloaded)

    def test_capture_rejects_missing_evidence_even_with_approved_review(self):
        self.case.update(authorization_id='test', evidence='reviewed text', evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(), review={'ready':True,'version':server.REVIEW_VERSION})
        server.save(self.case)
        for value in (None, '', 12):
            with patch('server.paypal') as remote:
                with self.assertRaises(ValueError):
                    server.act('capture',{'id':self.case['id'],'buyer_confirmed':True,'evidence':value})
                remote.assert_not_called()
    def test_capture_rejects_inconsistent_saved_evidence(self):
        self.case.update(authorization_id='test', evidence='changed on disk', evidence_hash=server.hashlib.sha256(b'reviewed text').hexdigest(), review={'ready':True,'version':server.REVIEW_VERSION})
        server.save(self.case)
        with patch('server.paypal') as remote:
            with self.assertRaises(ValueError):
                server.act('capture',{'id':self.case['id'],'buyer_confirmed':True,'evidence':'reviewed text'})
            remote.assert_not_called()

    def test_run_delivery_checks_action_generates_verified_report(self):
        out = server.act('run_delivery_checks', {})
        self.assertIn('Executed delivery verification', out['report'])
        self.assertIn('Result: PASS.', out['report'])

if __name__=='__main__':unittest.main()

