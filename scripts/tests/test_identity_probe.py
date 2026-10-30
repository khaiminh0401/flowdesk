"""Probe-tool tests only: never evidence that FlowDesk authentication exists."""
import importlib.util
import json
import http.cookiejar
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'security' / 'verify_identity_contract.py'
spec = importlib.util.spec_from_file_location('identity_probe', MODULE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def token_response(access='A' * 43):
    return {'tokenType': 'Bearer', 'expiresInSeconds': 600, 'accessToken': access,
            'user': {'id': '00000000-0000-0000-0000-000000000001',
                     'email': 'fixture@example.invalid', 'displayName': 'Fixture'}}


class Handler(BaseHTTPRequestHandler):
    calls = []
    requests = []
    responses = {}

    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.calls.append(self.path)
        self.requests.append((self.path, dict(self.headers)))
        if self.path in self.responses:
            response = self.responses[self.path]
            status, headers, body = response.pop(0) if isinstance(response, list) else response
            self.send_response(status)
            for name, value in headers:
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())
            return
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

    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', '0')))
        self.do_GET()


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
        Handler.requests.clear()
        Handler.responses.clear()
        self.client = probe.Client(self.base)

    def test_rejects_localhost_before_credentials_can_reach_a_resolved_destination(self):
        # A controlled resolver points the hostname at our sentinel server only.
        # Restoring hostname acceptance would deliver the bearer to this server.
        import socket
        addresses = socket.getaddrinfo('127.0.0.1', self.server.server_port, type=socket.SOCK_STREAM)
        with patch('socket.getaddrinfo', return_value=addresses):
            with self.assertRaises(probe.Blocked):
                client = probe.Client(f'http://localhost:{self.server.server_port}')
                client.request('GET', '/api/v1/allowed', access='A' * 43)
        self.assertEqual(Handler.calls, [])

    def test_accepts_only_explicit_ipv4_and_ipv6_loopback_literals(self):
        self.assertEqual(probe.local_base('http://127.0.0.1:4200/'), 'http://127.0.0.1:4200')
        self.assertEqual(probe.local_base('https://[::1]:4200/'), 'https://[::1]:4200')
        for base in ['http://localhost', 'http://LOCALHOST', 'http://127.1',
                     'http://2130706433', 'http://[::ffff:127.0.0.1]']:
            with self.subTest(base=base), self.assertRaises(probe.Blocked):
                probe.Client(base)

    def test_normalizes_scheme_before_selecting_the_https_cookie_profile(self):
        self.assertEqual(probe.local_base('HTTPS://[::1]:4200/'), 'https://[::1]:4200')

    def test_refresh_override_preserves_cookie_domain_path_secure_and_expiry_filters(self):
        for name, domain, path, secure, expires in [
            ('FD-CSRF', '127.0.0.1', '/', False, None),
            ('private', '127.0.0.1', '/private', False, None),
            ('foreign', 'example.invalid', '/', False, None),
            ('secure', '127.0.0.1', '/', True, None),
            ('expired', '127.0.0.1', '/', False, 1),
            ('FD-REFRESH', '127.0.0.1', '/', False, None),
        ]:
            self.client.cookies.set_cookie(http.cookiejar.Cookie(
                0, name, 'synthetic', None, False, domain, False, False,
                path, True, secure, expires, expires is None, None, None, {}))
        self.client.request('POST', '/api/v1/auth/refresh', refresh='R' * 43)
        sent = Handler.requests[-1][1]['Cookie']
        self.assertEqual(set(sent.split('; ')), {'FD-CSRF=synthetic', 'FD-REFRESH=' + 'R' * 43})
        self.assertEqual(next(cookie.value for cookie in self.client.cookies
                              if cookie.name == 'FD-REFRESH'), 'synthetic')

    def test_replay_rejects_malformed_replacement_access_before_observing_revocation(self):
        for access in ['', 'short', None]:
            with self.subTest(access=access):
                Handler.calls.clear()
                Handler.responses.update({
                    '/api/v1/auth/csrf': (200, [], {'headerName': 'X-CSRF-TOKEN', 'token': 'synthetic-csrf'}),
                    '/api/v1/auth/login': (200, [('Set-Cookie', 'FD-REFRESH=' + 'R' * 43 + '; Path=/')],
                                           token_response()),
                    '/api/v1/auth/refresh': (200, [('Set-Cookie', 'FD-REFRESH=' + 'S' * 43 + '; Path=/')],
                                             token_response(access)),
                })
                with patch.dict('os.environ', {'AUTH_PROBE_EMAIL': 'fixture@example.invalid',
                                               'AUTH_PROBE_PASSWORD': 'synthetic-password'}):
                    with self.assertRaises(probe.ProbeFailure):
                        probe.replay(probe.Client(self.base))
                self.assertEqual(Handler.calls.count('/api/v1/auth/refresh'), 1)

    def test_login_rejects_extra_response_fields_instead_of_certifying_a_token_leak(self):
        Handler.responses.update({
            '/api/v1/auth/csrf': (200, [], {'headerName': 'X-CSRF-TOKEN', 'token': 'synthetic-csrf'}),
            '/api/v1/auth/login': (200, [], {**token_response(), 'refreshToken': 'private-sentinel'}),
        })
        with patch.dict('os.environ', {'AUTH_PROBE_EMAIL': 'fixture@example.invalid',
                                       'AUTH_PROBE_PASSWORD': 'synthetic-password'}):
            with self.assertRaises(probe.ProbeFailure) as caught:
                self.client.login()
        self.assertNotIn('private-sentinel', str(caught.exception))

    def test_replay_proves_replacement_access_works_before_testing_revocation(self):
        Handler.responses.update({
            '/api/v1/auth/csrf': (200, [], {'headerName': 'X-CSRF-TOKEN', 'token': 'synthetic-csrf'}),
            '/api/v1/auth/login': (200, [('Set-Cookie', 'FD-REFRESH=' + 'R' * 43 + '; Path=/')],
                                   token_response()),
            '/api/v1/auth/refresh': [
                (200, [('Set-Cookie', 'FD-REFRESH=' + 'S' * 43 + '; Path=/')], token_response('B' * 43)),
                (401, [], {'code': 'SESSION_INVALID'}),
            ],
            '/api/v1/me': [(200, [], token_response()['user']), (401, [], {'code': 'SESSION_INVALID'})],
        })
        with patch.dict('os.environ', {'AUTH_PROBE_EMAIL': 'fixture@example.invalid',
                                       'AUTH_PROBE_PASSWORD': 'synthetic-password'}):
            probe.replay(self.client)
        requests = [(path, headers.get('Authorization')) for path, headers in Handler.requests
                    if path in ('/api/v1/me', '/api/v1/auth/refresh')]
        self.assertEqual(requests, [('/api/v1/auth/refresh', None),
                                    ('/api/v1/me', 'Bearer ' + 'B' * 43),
                                    ('/api/v1/auth/refresh', None),
                                    ('/api/v1/me', 'Bearer ' + 'B' * 43)])

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
