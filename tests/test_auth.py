import time

import httpx

from databrarypy.auth import OAuth2Client


def make_transport(assertions):
    def handler(request: httpx.Request) -> httpx.Response:
        for fn in assertions:
            fn(request)
        if request.url.path == "/o/token/" and request.method == "POST":
            data = request.content.decode()
            if "grant_type=password" in data:
                payload = {
                    "access_token": "ACCESS1",
                    "refresh_token": "REFRESH1",
                    "expires_in": 3600,
                }
                return httpx.Response(200, json=payload)
            if "grant_type=refresh_token" in data:
                payload = {
                    "access_token": "ACCESS2",
                    "refresh_token": "REFRESH2",
                    "expires_in": 3600,
                }
                return httpx.Response(200, json=payload)
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_oauth2_password_and_refresh_flow():
    assertions = [
        lambda req: req.headers.get("User-Agent") == "ua-test",
        lambda req: req.headers.get("Accept") == "application/json",
        lambda req: req.headers.get("Content-Type") == "application/x-www-form-urlencoded",
    ]
    transport = make_transport(assertions)

    oauth = OAuth2Client(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        user_agent="ua-test",
        transport=transport,
    )

    tok1 = oauth.login_with_password("user@example.org", "pw")
    assert tok1.access_token == "ACCESS1"
    assert tok1.refresh_token == "REFRESH1"
    assert tok1.expires_at > time.time()

    tok2 = oauth.refresh()
    assert tok2.access_token == "ACCESS2"
    assert tok2.refresh_token == "REFRESH2"
