from __future__ import annotations

from databrarypy.client import DatabraryClient


def test_iterate_volumes_users_and_records(client: DatabraryClient):
    # Volumes iterator yields at least first page size
    first_page = client.volumes.page(page=1, page_size=5)
    first_ids = [v.id for v in first_page.results]
    seen = []
    for idx, v in enumerate(client.volumes.iter_list(page=1, page_size=5)):
        seen.append(v.id)
        if idx >= 9:  # limit traversal for runtime
            break
    assert set(first_ids).issubset(set(seen))

    # Users iterator basic smoke
    u_first = client.users.page(page=1, page_size=5)
    u_seen = []
    for idx, u in enumerate(client.users.iter_list(page=1, page_size=5)):
        u_seen.append(u.id)
        if idx >= 9:
            break
    assert len(u_seen) >= len(u_first.results)

    # Records iterator for first available volume
    if first_page.results:
        vid = first_page.results[0].id
        r_first = client.records.page(vid, page=1, page_size=2)
        r_seen = []
        for idx, r in enumerate(client.records.iter_list(vid, page=1, page_size=2)):
            r_seen.append(r.id)
            if idx >= 4:
                break
        assert len(r_seen) >= len(r_first.results)
