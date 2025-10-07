import httpx

from databrarypy.client import DatabraryClient


def make_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/o/token/" and request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "access_token": "ACCESS1",
                    "refresh_token": "REFRESH1",
                    "expires_in": 3600,
                },
            )
        if request.url.path == "/oauth2/test/" and request.method == "GET":
            return httpx.Response(200, json={"authMethod": "OAuth2"})
        if request.url.path == "/statistics/summary/" and request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "institutions": 5,
                    "affiliates": 10,
                    "investigators": 20,
                    "hours_of_recordings": 42,
                },
            )
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_whoami_and_get_db_stats():
    transport = make_transport()
    client = DatabraryClient(
        base_url="https://api.example.org",
        client_id="cid",
        client_secret="secret",
        user_agent="ua-test",
        transport=transport,
    )

    client.auth.login_with_password("user@example.org", "pw")

    who = client.whoami()
    assert who["authMethod"] == "OAuth2"

    stats = client.library.get_db_stats()
    assert stats.institutions == 5
    assert stats.affiliates == 10
    assert stats.investigators == 20
    assert stats.hours_of_recordings == 42
