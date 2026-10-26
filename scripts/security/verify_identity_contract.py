#!/usr/bin/env python3
"""Local proposed-contract probes. Not an auth implementation or security certification."""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request


class ProbeFailure(Exception):
    """Safe failure text: never include bodies, cookies or credentials."""


class Blocked(Exception):
    """Required local service/fixture is unavailable."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme not in ('http', 'https')
            or parsed.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parsed.username or parsed.password or parsed.path not in ('', '/')
            or parsed.query or parsed.fragment):
        raise Blocked('Use a loopback-only base URL without credentials, path or query')
    return value.rstrip('/')


def require_environment(*names: str) -> list[str]:
    values = [os.environ.get(name, '') for name in names]
    if not all(values):
        raise Blocked('Missing synthetic fixture variables: ' + ', '.join(names))
    return values


def expect_status(actual: int, expected: int) -> None:
    if actual != expected:
        raise ProbeFailure(f'Expected HTTP {expected}, received {actual}; response body withheld')


class Client:
    def __init__(self, base_url: str):
        self.base = local_base(base_url)
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies), NoRedirect())
        self.csrf = ''

    def request(self, method: str, path: str, *, body: dict | None = None,
                access: str | None = None, csrf: bool = True, origin: str | None = None,
                refresh: str | None = None) -> tuple[int, dict, bytes]:
        parsed = urllib.parse.urlsplit(path)
        if not path.startswith('/api/v1/') or parsed.scheme or parsed.netloc:
            raise Blocked('Probe paths must stay under same-origin /api/v1/')
        headers = {'Accept': 'application/json', 'Origin': origin or self.base}
        if method not in ('GET', 'HEAD') and csrf and self.csrf:
            headers['X-CSRF-TOKEN'] = self.csrf
        if access:
            if not re.fullmatch(r'[A-Za-z0-9_-]{43}', access):
                raise Blocked('Access fixture must be an opaque32-byte base64url token')
            headers['Authorization'] = 'Bearer ' + access
        if refresh is not None:
            if not re.fullmatch(r'[A-Za-z0-9_-]{43}', refresh):
                raise Blocked('Refresh fixture must be an opaque32-byte base64url token')
            cookie_name = '__Host-FD-REFRESH' if self.base.startswith('https:') else 'FD-REFRESH'
            cookies = {cookie.name: cookie.value for cookie in self.cookies}
            cookies[cookie_name] = refresh
            headers['Cookie'] = '; '.join(f'{name}={value}' for name, value in cookies.items())
        data = None if body is None else json.dumps(body).encode()
        if data is not None:
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            response = self.opener.open(request, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise Blocked('Local HTTP service unavailable; request details withheld') from error
        with response:
            content = response.read(65537)
            if len(content) > 65536:
                raise ProbeFailure('Response too large; body withheld')
            return response.code, dict(response.headers), content

    def checked(self, method: str, path: str, status: int, **kwargs) -> dict:
        actual, _, content = self.request(method, path, **kwargs)
        expect_status(actual, status)
        if not content:
            return {}
        try:
            value = json.loads(content)
        except (ValueError, UnicodeError) as error:
            raise ProbeFailure('Expected JSON response; body withheld') from error
        if not isinstance(value, dict):
            raise ProbeFailure('Expected JSON object; body withheld')
        return value

    def bootstrap(self) -> None:
        result = self.checked('GET', '/api/v1/auth/csrf', 200)
        if result.get('headerName') != 'X-CSRF-TOKEN' or not isinstance(result.get('token'), str) or not result['token']:
            raise ProbeFailure('Invalid CSRF bootstrap contract; body withheld')
        self.csrf = result['token']

    def login(self) -> str:
        email, password = require_environment('AUTH_PROBE_EMAIL', 'AUTH_PROBE_PASSWORD')
        self.bootstrap()
        result = self.checked('POST', '/api/v1/auth/login', 200, body={'email': email, 'password': password})
        if (result.get('tokenType') != 'Bearer' or result.get('expiresInSeconds') != 600
                or not isinstance(result.get('accessToken'), str)
                or not re.fullmatch(r'[A-Za-z0-9_-]{43}', result['accessToken'])):
            raise ProbeFailure('Invalid access response contract; body withheld')
        self.bootstrap()  # login rotated CSRF state
        return result['accessToken']

    def refresh_cookie(self) -> str:
        names = ('FD-REFRESH', '__Host-FD-REFRESH')
        matches = [cookie.value for cookie in self.cookies if cookie.name in names]
        if len(matches) != 1:
            raise ProbeFailure('Expected exactly one refresh cookie; values withheld')
        return matches[0]


def anonymous(client: Client) -> None:
    client.checked('GET', '/api/v1/me', 401)
    client.bootstrap()
    body = {'email': 'absent-fixture@example.invalid', 'password': secrets.token_urlsafe(24)}
    client.checked('POST', '/api/v1/auth/login', 403, body=body, csrf=False)
    client.checked('POST', '/api/v1/auth/login', 403, body=body, origin='https://attacker.invalid')
    result = client.checked('POST', '/api/v1/auth/login', 401, body=body)
    if result.get('code') != 'AUTHENTICATION_FAILED':
        raise ProbeFailure('Generic login failure code missing; body withheld')


def lifecycle(client: Client) -> None:
    access = client.login()
    client.checked('GET', '/api/v1/me', 200, access=access)
    client.checked('GET', '/api/v1/me', 401)  # refresh/CSRF cookies alone must not authenticate
    client.checked('POST', '/api/v1/auth/logout', 204, access=access)
    client.checked('GET', '/api/v1/me', 401, access=access)
    client.bootstrap()
    client.checked('POST', '/api/v1/auth/logout', 204)  # idempotent, still CSRF-protected


def replay(client: Client) -> None:
    client.login()
    old_refresh = client.refresh_cookie()
    replacement = client.checked('POST', '/api/v1/auth/refresh', 200)
    access = replacement.get('accessToken')
    if not isinstance(access, str) or client.refresh_cookie() == old_refresh:
        raise ProbeFailure('Refresh did not replace credentials; values withheld')
    result = client.checked('POST', '/api/v1/auth/refresh', 401, refresh=old_refresh)
    if result.get('code') != 'SESSION_INVALID':
        raise ProbeFailure('Generic refresh failure code missing; body withheld')
    client.checked('GET', '/api/v1/me', 401, access=access)  # durable family revocation


def expiry(client: Client) -> None:
    access, refresh = require_environment('AUTH_PROBE_EXPIRED_ACCESS', 'AUTH_PROBE_EXPIRED_REFRESH')
    client.checked('GET', '/api/v1/me', 401, access=access)
    client.bootstrap()
    result = client.checked('POST', '/api/v1/auth/refresh', 401, refresh=refresh)
    if result.get('code') != 'SESSION_INVALID':
        raise ProbeFailure('Generic expired-refresh failure missing; body withheld')


def workspace(client: Client) -> None:
    own, other = require_environment('AUTH_PROBE_OWN_RESOURCE', 'AUTH_PROBE_OTHER_RESOURCE')
    if own == other or not all(path.startswith('/api/v1/workspaces/') for path in (own, other)):
        raise Blocked('Provide two distinct scoped resource paths from FD-011 synthetic fixtures')
    access = client.login()
    client.checked('GET', own, 200, access=access)
    client.checked('GET', other, 404, access=access)


CASES = {'anonymous': anonymous, 'lifecycle': lifecycle, 'replay': replay, 'expiry': expiry, 'workspace': workspace}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:4200')
    parser.add_argument('--case', choices=CASES, default='anonymous')
    args = parser.parse_args()
    try:
        CASES[args.case](Client(args.base_url))
    except Blocked as error:
        print(f'BLOCKED: {error}')
        return 2
    except ProbeFailure as error:
        print(f'FAIL: {error}')
        return 1
    except Exception:
        print('FAIL: unexpected probe error; details withheld to protect credentials')
        return 1
    print(f'PASS: {args.case} HTTP contract probe only; not a full security assessment')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
