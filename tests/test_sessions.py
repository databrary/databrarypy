"""SessionsResource tests (list, retrieve, nested files)."""

from __future__ import annotations

from databrarypy.client import DatabraryClient
from tests.fixtures.data_constants import VOLUME_ID_PRIMARY
from tests.fixtures.sessions import (
    SESSION_FILE_ID_1,
    SESSION_ID_1,
    build_composite_transport,
)


def test_sessions_list_retrieve_and_files() -> None:
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    # list
    page = client.sessions.list(VOLUME_ID_PRIMARY, page=1, page_size=10)
    assert page.count == 1
    assert page.results and page.results[0].id == SESSION_ID_1

    # retrieve
    detail = client.sessions.retrieve(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert detail.id == SESSION_ID_1
    assert detail.release_level == "public"

    # files list
    files_page = client.sessions.files(VOLUME_ID_PRIMARY, SESSION_ID_1)
    assert files_page.count == 1
    f0 = files_page.results[0]
    assert f0.format and f0.format.mimetype.startswith("video/")

    # file detail
    fdetail = client.sessions.get_file(VOLUME_ID_PRIMARY, SESSION_ID_1, SESSION_FILE_ID_1)
    assert fdetail.id == SESSION_FILE_ID_1
    tf = fdetail.transcoded_file
    assert tf is None or (
        getattr(tf, "id", None) is not None or (isinstance(tf, dict) and "id" in tf)
    )
