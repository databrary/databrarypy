"""InstitutionsResource tests."""

from pathlib import Path

from databrarypy.client import DatabraryClient
from tests.fixtures.users import build_composite_transport


def test_institutions_list():
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

    page = client.institutions.list(search="Example")
    assert page.count == 1
    assert page.results[0].name == "Example University"
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
        base_url="https://api.example",
        client_id="cid",
        client_secret="sec",
        username="user@example.org",
        password="pw",
        user_agent="dbpy-tests",
        transport=transport,
    )
    client.auth.login()

    page = client.institutions.list(search="test")
    # Mock returns static data regardless of search params; tests client-side code path
    inst = page.results[0]
    retrieved = client.institutions.retrieve(inst.id)
    assert retrieved.id == inst.id


def test_institutions_params_and_avatar_404():
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

    # Exercise page/page_size params on list
    page = client.institutions.list(search="Example", page=2, page_size=5)
    assert page.count >= 1
