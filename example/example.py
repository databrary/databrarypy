from contextlib import suppress
from pathlib import Path

from databrarypy.client import DatabraryClient


def _mask(val: str | None) -> str:
    if not val:
        return "<missing>"
    if len(val) <= 4:
        return "****"
    return val[:4] + "****"


def _prompt_int(msg: str, default: int | None = None) -> int | None:
    raw = input(f"{msg}: ").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return None


def _prompt_str(msg: str, default: str | None = None) -> str | None:
    raw = input(f"{msg}: ").strip()
    if not raw:
        return default
    return raw


def _show_menu() -> int | None:
    print()
    print("Records management demo:")
    print("  1. List categories for volume (with metrics)")
    print("  2. List records in volume")
    print("  3. Create a new record")
    print("  4. Update a record")
    print("  5. Set a measure on a record")
    print("  6. Delete a measure from a record")
    print("  7. Delete a record")
    print("  8. List sessions and files in volume")
    print("  9. Assign record to file")
    print(" 10. Unassign record from file")
    print("  0. Quit")
    choice = _prompt_int("Choice", default=None)
    return choice


def _do_list_categories(client: DatabraryClient, volume_id: int) -> None:
    try:
        vol = client.volumes.retrieve(volume_id)
        categories = vol.enabled_categories or []
        if not categories:
            print("  No enabled categories for this volume.")
            return
        for cat in categories:
            print(f"  Category id={cat.id} name={cat.name!r}")
            for m in cat.metrics or []:
                print(f"    metric id={m.id} name={m.name!r} type={m.type} required={m.required}")
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_list_records(client: DatabraryClient, volume_id: int) -> None:
    cat_id = _prompt_int("  Category ID (optional, leave empty for all)", default=None)
    try:
        records = list(client.records.list(volume_id, category_id=cat_id, page_size=20))
        for r in records[:50]:
            print(f"  Record id={r.id} category_id={r.category_id} measures={r.measures}")
        if len(records) > 50:
            print(f"  ... and {len(records) - 50} more")
        else:
            print(f"  Total: {len(records)} records")
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_create_record(client: DatabraryClient, volume_id: int) -> None:
    cat_id = _prompt_int("  Category ID")
    if cat_id is None:
        print("  Category ID required.")
        return
    name = _prompt_str("  Record name")
    if not name:
        print("  Name required.")
        return
    use_birthday = _prompt_str("  Add participant birthday? (y/n)", default="n")
    participant = None
    if use_birthday and use_birthday.lower() == "y":
        year = _prompt_int("  Birthday year")
        month = _prompt_int("  Birthday month")
        day = _prompt_int("  Birthday day")
        if year is not None and month is not None and day is not None:
            participant = {"birthday": {"year": year, "month": month, "day": day}}
    try:
        rec = client.records.create(
            volume_id,
            category_id=cat_id,
            name=name,
            participant=participant,
        )
        print("  Created:", rec.model_dump())
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_update_record(client: DatabraryClient, volume_id: int) -> None:
    record_id = _prompt_int("  Record ID")
    if record_id is None:
        print("  Record ID required.")
        return
    metric_id_str = _prompt_str("  Metric ID to update (e.g. 123)")
    value_str = _prompt_str("  Value (string/number)")
    if not metric_id_str or value_str is None:
        print("  Metric ID and value required.")
        return
    try:
        metric_id = int(metric_id_str)
    except ValueError:
        print("  Invalid metric ID.")
        return
    try:
        val: str | int | float = value_str
        try:
            val = int(value_str)
        except ValueError:
            with suppress(ValueError):
                val = float(value_str)
        rec = client.records.update(
            volume_id,
            record_id,
            measures={str(metric_id): val},
        )
        print("  Updated:", rec.model_dump())
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_set_measure(client: DatabraryClient, volume_id: int) -> None:
    record_id = _prompt_int("  Record ID")
    metric_id = _prompt_int("  Metric ID")
    if record_id is None or metric_id is None:
        print("  Record ID and metric ID required.")
        return
    value_str = _prompt_str("  Value (string/number, or 'date' for date)")
    if value_str is None:
        print("  Value required.")
        return
    try:
        val: str | int | float | dict = value_str
        if value_str.lower() == "date":
            year = _prompt_int("  Date year", default=2000)
            month = _prompt_int("  Date month", default=1)
            day = _prompt_int("  Date day", default=1)
            if year is not None and month is not None and day is not None:
                val = {
                    "year": year,
                    "month": month,
                    "day": day,
                }
        else:
            try:
                val = int(value_str)
            except ValueError:
                with suppress(ValueError):
                    val = float(value_str)
        data = client.records.set_measure(volume_id, record_id, metric_id, value=val)
        print("  Result:", data)
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_delete_measure(client: DatabraryClient, volume_id: int) -> None:
    record_id = _prompt_int("  Record ID")
    metric_id = _prompt_int("  Metric ID")
    if record_id is None or metric_id is None:
        print("  Record ID and metric ID required.")
        return
    try:
        client.records.delete_measure(volume_id, record_id, metric_id)
        print("  Measure deleted.")
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_delete_record(client: DatabraryClient, volume_id: int) -> None:
    record_id = _prompt_int("  Record ID")
    if record_id is None:
        print("  Record ID required.")
        return
    try:
        client.records.delete(volume_id, record_id)
        print("  Record deleted.")
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_list_sessions_files(client: DatabraryClient, volume_id: int) -> None:
    try:
        sessions = list(client.sessions.list(volume_id, page_size=20))
        for sess in sessions[:10]:
            print(f"  Session id={sess.id} name={sess.name!r}")
            files = client.sessions.files_list(volume_id, sess.id, page_size=10)
            for f in files:
                print(f"    File id={f.id} name={f.name!r}")
        if len(sessions) > 10:
            print(f"  ... and {len(sessions) - 10} more sessions")
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_assign_record(client: DatabraryClient, volume_id: int) -> None:
    session_id = _prompt_int("  Session ID")
    file_id = _prompt_int("  File ID")
    record_id = _prompt_int("  Record ID")
    if session_id is None or file_id is None or record_id is None:
        print("  Session ID, file ID, and record ID required.")
        return
    try:
        data = client.sessions.assign_record_to_file(volume_id, session_id, file_id, record_id)
        print("  Assigned:", data)
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def _do_unassign_record(client: DatabraryClient, volume_id: int) -> None:
    session_id = _prompt_int("  Session ID")
    file_id = _prompt_int("  File ID")
    record_id = _prompt_int("  Record ID")
    if session_id is None or file_id is None or record_id is None:
        print("  Session ID, file ID, and record ID required.")
        return
    try:
        data = client.sessions.unassign_record_from_file(volume_id, session_id, file_id, record_id)
        print("  Unassigned:", data)
    except Exception as exc:  # noqa: BLE001
        print("  Error:", exc)


def run_interactive(client: DatabraryClient) -> None:
    """Run the interactive records management menu loop."""
    volume_id = _prompt_int("Enter volume ID to work with")
    if volume_id is None:
        print("Volume ID required. Exiting.")
        return
    while True:
        choice = _show_menu()
        if choice is None or choice == 0:
            break
        elif choice == 1:
            _do_list_categories(client, volume_id)
        elif choice == 2:
            _do_list_records(client, volume_id)
        elif choice == 3:
            _do_create_record(client, volume_id)
        elif choice == 4:
            _do_update_record(client, volume_id)
        elif choice == 5:
            _do_set_measure(client, volume_id)
        elif choice == 6:
            _do_delete_measure(client, volume_id)
        elif choice == 7:
            _do_delete_record(client, volume_id)
        elif choice == 8:
            _do_list_sessions_files(client, volume_id)
        elif choice == 9:
            _do_assign_record(client, volume_id)
        elif choice == 10:
            _do_unassign_record(client, volume_id)
        else:
            print("  Unknown option.")


def main() -> None:
    """Entry point: load env, authenticate, run interactive demo."""
    env_path = Path(__file__).resolve().parent / ".env"

    client = DatabraryClient.from_env(env_file=env_path, login=False)

    print("ENV check:")
    print("  BASE_URL:", client.base_url or "<missing>")
    print("  USER_AGENT:", client.user_agent or "<missing>")
    print("  CLIENT_ID:", _mask(client.auth.client_id))
    print("  CLIENT_SECRET:", _mask(client.auth.client_secret))
    print("  USERNAME:", _mask(client.auth.username))

    with client:
        client.auth.login()
        who = client.whoami()
        print("whoami:", who.model_dump())

        try:
            stats = client.system.get_db_stats()
            print("stats:", stats.model_dump())
        except Exception as exc:  # noqa: BLE001
            print("stats fetch failed:", exc)

        run_interactive(client)


if __name__ == "__main__":
    main()
