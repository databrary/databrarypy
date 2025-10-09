"""Users fixtures and mock handlers."""

import httpx

from .common import build_transport
from .factory import make_page

# ---- Top-level objects ----
MOCK_AVATAR_PNG = b"\x89PNG\r\n\x1a\n"

MOCK_USER_PRIMARY = {
    "id": 6,
    "firstName": "Alex",
    "lastName": "Doe",
    "email": "user1@example.org",
    "affiliation": {"id": 12, "name": "Penn State", "url": "https://psu.edu"},
    "isAuthorizedInvestigator": True,
    "orcid": None,
    "url": None,
    "hasAvatar": False,
}

MOCK_VOLUME_VOL1 = {
    "id": 1,
    "updated_at": None,
    "created_at": None,
    "title": "Vol1",
    "description": None,
    "short_name": None,
    "sharing_level": "public",
    "coauthors": [],
}

MOCK_VOLUME_VOL2 = {
    "id": 2,
    "updated_at": None,
    "created_at": None,
    "title": "Vol2",
    "description": None,
    "short_name": None,
    "sharing_level": "public",
    "coauthors": [],
}

# ---- Paged payloads ----
MOCK_USERS_PAGE = make_page(
    results=[MOCK_USER_PRIMARY],
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)

MOCK_USER_6_VOLUMES_PAGE_EMPTY = make_page(results=[], count=0)
MOCK_USER_7_VOLUMES_PAGE = make_page(results=[MOCK_VOLUME_VOL1, MOCK_VOLUME_VOL2], count=2)
MOCK_USER_6_AFFILIATES_PAGE_EMPTY = make_page(results=[], count=0)


MOCK_USER_SELF = {
    **MOCK_USER_PRIMARY,
    "pending_institution_requests": [],
    "pending_affiliate_requests": [],
    "phone": None,
    "totp_enrolled_at": None,
    "finished_registration": True,
    "has_api_access": True,
    "current_affiliates": [],
    "current_sponsors": [],
    "is_suspended": False,
    "suspended_by": None,
}


MOCK_SPONSORSHIPS = [
    {
        "id": 101,
        "sponsor": MOCK_USER_PRIMARY,
        "user": MOCK_USER_PRIMARY,
        "institution": {"id": 12, "name": "Penn State"},
        "access_level": "read",
        "has_databrary_affiliate_access": False,
        "sponsor_institution_connection": 999,
        "expiration_date": None,
        "created_at": None,
        "updated_at": None,
    }
]

MOCK_USER_6_INSTITUTION_SPONSORS = []


def handle_users_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USERS_PAGE)


def handle_user_retrieve(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_SELF)


def handle_user_sponsorships(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_SPONSORSHIPS)


def handle_user_volumes_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_6_VOLUMES_PAGE_EMPTY)


def handle_user_volumes_7(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_7_VOLUMES_PAGE)


def handle_user_affiliates_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_6_AFFILIATES_PAGE_EMPTY)


def handle_user_avatar_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=MOCK_AVATAR_PNG)


def handle_user_institution_sponsors_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_6_INSTITUTION_SPONSORS)


def handle_user_avatar_999(request: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json={"detail": "No avatar"})


def build_users_transport():
    return build_transport(
        ("GET", "/users/", handle_users_list),
        ("GET", "/users/6/", handle_user_retrieve),
        ("GET", "/users/6/sponsorships/", handle_user_sponsorships),
        ("GET", "/users/6/volumes/", handle_user_volumes_6),
        ("GET", "/users/6/avatar/", handle_user_avatar_6),
        ("GET", "/users/6/institution-sponsors/", handle_user_institution_sponsors_6),
        ("GET", "/users/7/volumes/", handle_user_volumes_7),
        ("GET", "/users/6/affiliates/", handle_user_affiliates_6),
        ("GET", "/users/999/avatar/", handle_user_avatar_999),
    )


def build_composite_transport():
    """Composite transport with auth routes and users/institutions routes."""
    from .client import build_client_transport

    client_transport = build_client_transport()
    users_transport = build_users_transport()
    from .institutions import build_institutions_transport

    institutions_transport = build_institutions_transport()

    def router(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        # Route auth endpoints to client transport
        if key in {("POST", "/o/token/"), ("GET", "/oauth2/test/")}:
            return client_transport.handle_request(request)
        # Try users first and fallback to institutions on 404
        resp = users_transport.handle_request(request)
        if resp.status_code == 404:
            return institutions_transport.handle_request(request)
        return resp

    return httpx.MockTransport(router)
