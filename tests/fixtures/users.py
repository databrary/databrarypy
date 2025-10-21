"""Users fixtures and mock handlers."""

import httpx

from .common import build_transport
from .data_constants import (
    MOCK_AVATAR_PNG,
    USER_ID_1,
    USER_ID_2,
    USER_ID_COAUTHOR,
    USER_ID_NOT_FOUND,
    USER_ID_OWNER,
)
from .factory import make_page
from .institutions import MOCK_INSTITUTION_1_DETAILED, MOCK_INSTITUTION_2, MOCK_INSTITUTION_3

MOCK_USER_1 = {
    "id": USER_ID_1,
    "first_name": "Alex",
    "last_name": "Doe",
    "email": "user1@example.org",
    "affiliation": MOCK_INSTITUTION_1_DETAILED,
    "is_authorized_investigator": True,
    "orcid": None,
    "url": None,
    "has_avatar": False,
}

# ---- Paged payloads ----
MOCK_USERS_PAGE = make_page(
    results=[MOCK_USER_1],
    total_pages=1,
    current_page=1,
    sort_by=None,
    sort_order="asc",
)


def _get_mock_user_6_volumes_page_empty():
    return make_page(results=[], count=0)


def _get_mock_user_7_volumes_page():
    from tests.fixtures.volume import _get_mock_volume_base

    # Create first volume with title "Vol1"
    volume_1 = _get_mock_volume_base().copy()
    volume_1.update({"title": "Vol1"})

    # Create a second volume mock
    volume_2 = _get_mock_volume_base().copy()
    volume_2.update({"id": 2, "title": "Vol2"})

    return make_page(results=[volume_1, volume_2], count=2)


MOCK_USER_6_AFFILIATES_PAGE_EMPTY = make_page(results=[], count=0)


MOCK_USER_SELF = {
    **MOCK_USER_1,
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


MOCK_USER_COAUTHOR = {
    "id": USER_ID_COAUTHOR,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jsmith@example.org",
    "affiliation": MOCK_INSTITUTION_2,
    "is_authorized_investigator": True,
    "orcid": None,
    "url": "https://example.org/jsmith",
    "has_avatar": True,
}


MOCK_USER_OWNER = {
    "id": USER_ID_OWNER,
    "first_name": "John",
    "last_name": "Johnson",
    "email": "jjohnson@example.org",
    "affiliation": MOCK_INSTITUTION_3,
    "is_authorized_investigator": True,
    "orcid": "0000-0000-0000-0001",
    "url": "https://example.org/jjohnson",
    "has_avatar": True,
}


MOCK_USER_6_AFFILIATE_ACTIVE = {
    "id": 201,
    "sponsor": MOCK_USER_1,
    "user": MOCK_USER_1,
    "institution": {"id": 12, "name": "Penn State"},
    "access_level": "read",
    "has_databrary_affiliate_access": True,
    "sponsor_institution_connection": 1000,
    "expiration_date": "2099-01-01",
    "created_at": None,
    "updated_at": None,
}

MOCK_USER_6_AFFILIATE_EXPIRED = {
    "id": 202,
    "sponsor": MOCK_USER_1,
    "user": MOCK_USER_1,
    "institution": {"id": 12, "name": "Penn State"},
    "access_level": "read",
    "has_databrary_affiliate_access": False,
    "sponsor_institution_connection": 1001,
    "expiration_date": "2000-01-01",
    "created_at": None,
    "updated_at": None,
}

MOCK_USER_6_INSTITUTION_SPONSORS = []


def handle_users_list(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USERS_PAGE)


def handle_user_retrieve(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_SELF)


def handle_user_sponsorships(request: httpx.Request) -> httpx.Response:
    from .sponsorships import _get_mock_sponsorship_1

    return httpx.Response(200, json=[_get_mock_sponsorship_1()])


def handle_user_volumes_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_user_6_volumes_page_empty())


def handle_user_volumes_7(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_get_mock_user_7_volumes_page())


def handle_user_affiliates_6(request: httpx.Request) -> httpx.Response:
    include_expired = request.url.params.get("include_expired") == "true"
    results = [MOCK_USER_6_AFFILIATE_ACTIVE]
    if include_expired:
        results.append(MOCK_USER_6_AFFILIATE_EXPIRED)
    page = make_page(results=results, count=len(results))
    return httpx.Response(200, json=page)


def handle_user_avatar_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=MOCK_AVATAR_PNG)


def handle_user_institution_sponsors_6(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MOCK_USER_6_INSTITUTION_SPONSORS)


def handle_user_avatar_999(request: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json={"detail": "No avatar"})


def build_users_transport():
    return build_transport(
        ("GET", "/users/", handle_users_list),
        ("GET", f"/users/{USER_ID_1}/", handle_user_retrieve),
        ("GET", f"/users/{USER_ID_1}/sponsorships/", handle_user_sponsorships),
        ("GET", f"/users/{USER_ID_1}/volumes/", handle_user_volumes_6),
        ("GET", f"/users/{USER_ID_1}/avatar/", handle_user_avatar_6),
        (
            "GET",
            f"/users/{USER_ID_1}/institution-sponsors/",
            handle_user_institution_sponsors_6,
        ),
        ("GET", f"/users/{USER_ID_2}/volumes/", handle_user_volumes_7),
        ("GET", f"/users/{USER_ID_1}/affiliates/", handle_user_affiliates_6),
        ("GET", f"/users/{USER_ID_NOT_FOUND}/avatar/", handle_user_avatar_999),
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
