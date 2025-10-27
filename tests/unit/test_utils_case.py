"""Tests for case conversion utilities."""

from databrarypy.utils.case import camel_to_snake, snake_keys


def test_camel_to_snake():
    assert camel_to_snake("firstName") == "first_name"
    assert camel_to_snake("HTTPResponseCode") == "http_response_code"


def test_snake_keys_recursive():
    data = {
        "firstName": "Alex",
        "hasAvatar": False,
        "nestedObj": {"lastName": "Doe"},
        "items": [{"isAuthorizedInvestigator": True}],
    }
    out = snake_keys(data)
    assert out["first_name"] == "Alex"
    assert out["has_avatar"] is False
    assert out["nested_obj"]["last_name"] == "Doe"
    assert out["items"][0]["is_authorized_investigator"] is True
