"""Probe-tool tests only: never evidence that FlowDesk authentication exists."""
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'security' / 'verify_identity_contract.py'
spec = importlib.util.spec_from_file_location('identity_probe', MODULE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class Handler(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.calls.append(self.path)
        if self.path == '/api/v1/redirect':
            self.send_response(302)
            self.send_header('Location', '/api/v1/target')
            self.end_headers()
            return
        self.send_response(401 if self.path == '/api/v1/denied' else 200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        content = b'private-token-not-json' if self.path == '/api/v1/malformed' else json.dumps({'code': 'AUTHENTICATION_REQUIRED'}).encode()
        self.wfile.write(content)


class IdentityProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        Handler.calls.clear()
        self.client = probe.Client(self.base)

    def test_rejects_nonlocal_and_credential_bearing_base_urls(self):
        for base in ['https://example.com', 'http://user:password@localhost', 'http://localhost/api', 'http://localhost?secret=value']:
            with self.subTest(base=base), self.assertRaises(probe.Blocked):
                probe.Client(base)

    def test_rejects_cross_origin_and_non_api_paths_before_http(self):
        for path in ['//example.com/api/v1/me', 'https://example.com/api/v1/me', '/admin']:
            with self.subTest(path=path), self.assertRaises(probe.Blocked):
                self.client.request('GET', path)
        self.assertEqual(Handler.calls, [])

    def test_ignores_configured_proxies_even_when_loopback_bypass_is_disabled(self):
        with patch('urllib.request.getproxies', return_value={'http': self.base}), \
                patch('urllib.request.proxy_bypass', return_value=False):
            client = probe.Client(self.base)
            client.request('GET', '/api/v1/allowed', access='A' * 43)
        self.assertEqual(Handler.calls, ['/api/v1/allowed'])

    def test_follows_no_redirect_even_with_a_bearer(self):
        status, _, _ = self.client.request('GET', '/api/v1/redirect', access='A' * 43)
        self.assertEqual(status, 302)
        self.assertEqual(Handler.calls, ['/api/v1/redirect'])

    def test_treats_a_200_on_an_expected_denial_as_failure(self):
        with self.assertRaisesRegex(probe.ProbeFailure, 'Expected HTTP 401, received 200'):
            self.client.checked('GET', '/api/v1/allowed', 401)

    def test_reads_json_from_real_http_error_responses(self):
        value = self.client.checked('GET', '/api/v1/denied', 401)
        self.assertEqual(value, {'code': 'AUTHENTICATION_REQUIRED'})

    def test_withholds_non_json_response_secrets_from_failure_text(self):
        with self.assertRaises(probe.ProbeFailure) as caught:
            self.client.checked('GET', '/api/v1/malformed', 200)
        self.assertNotIn('private-token', str(caught.exception))
        self.assertIn('body withheld', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
