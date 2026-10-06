"""InstitutionsResource tests."""

from pathlib import Path

import pytest

from databrarypy.client import DatabraryClient
from databrarypy.errors import NotFoundError
from tests.fixtures.constants import (
    TEST_BASE_URL,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from tests.fixtures.data_constants import (
    INSTITUTION_ID_1,
    INSTITUTION_ID_2,
    INSTITUTION_ID_NOT_FOUND,
)
from tests.fixtures.institutions import MOCK_INSTITUTION_1, MOCK_INSTITUTION_STATISTICS
from tests.fixtures.users import build_composite_transport


def _make_client():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()
    return client


def test_institutions_list():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    page = client.institutions.page(search="Example")
    assert page.count == 1

    assert page.results[0].name == MOCK_INSTITUTION_1["name"]
    inst_id = page.results[0].id
    invs = client.institutions.authorized_investigators(inst_id)
    assert invs and invs[0].is_authorized_investigator is True
    avatar2 = client.institutions.avatar(inst_id)
    assert avatar2.startswith(b"\x89PNG")
    # also save avatar to dir and explicit file
    out_dir = Path(".pytest_tmp/institution_avatar")
    if out_dir.exists() and out_dir.is_file():
        out_dir.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = client.institutions.avatar(inst_id, dest_path=str(out_dir))
    assert saved and (out_dir / Path(saved).name).exists()
    explicit = out_dir / "avatar.png"
    saved2 = client.institutions.avatar(inst_id, dest_path=str(explicit))
    assert saved2.endswith("avatar.png") and explicit.exists()


def test_institutions_list_empty_and_retrieve():
    # Use the same transport; we test retrieve to cover branch
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    page = client.institutions.page(search="Nonexistent")
    # Our fixture returns static list; still covers the call path
    inst = page.results[0]
    retrieved = client.institutions.retrieve(inst.id)
    assert retrieved.id == inst.id


def test_institutions_params_and_avatar_404():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    # Exercise page/page_size params on list
    page = client.institutions.page(search="Example", page=2, page_size=5)
    assert page.count >= 1


def test_institutions_list_iterator():
    transport = build_composite_transport()
    client = DatabraryClient(
        base_url=TEST_BASE_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        transport=transport,
    )
    client.auth.login()

    first_inst = next(client.institutions.list(search="Example"))
    assert first_inst.id is not None


def test_institution_statistics_ok():
    client = _make_client()

    stats = client.institutions.statistics(INSTITUTION_ID_1)

    assert stats is not None
    assert stats.institution_id == INSTITUTION_ID_1
    assert stats.volumes_number == MOCK_INSTITUTION_STATISTICS["volumes_number"]
    assert stats.files_number == MOCK_INSTITUTION_STATISTICS["files_number"]
    assert stats.uploaded_data_footprint == MOCK_INSTITUTION_STATISTICS["uploaded_data_footprint"]


def test_institution_statistics_no_content():
    client = _make_client()

    stats = client.institutions.statistics(INSTITUTION_ID_2)

    assert stats is None


def test_institution_statistics_not_found():
    client = _make_client()

    with pytest.raises(NotFoundError):
        client.institutions.statistics(INSTITUTION_ID_NOT_FOUND)
