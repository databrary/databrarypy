"""Tests record/age Pydantic models (snake_case payloads, matching default client)."""

from __future__ import annotations

from databrarypy.models.records import Age, BirthdayInput, DateMeasureValue
from databrarypy.models.sessions import SessionDate


def test_age_accepts_snake_case_normalized() -> None:
    """Default client path: API camelCase has been normalized to snake_case."""
    a = Age.model_validate(
        {
            "years": 3,
            "months": 0,
            "days": 0,
            "total_days": 100,
            "formatted_value": "3.00 years",
            "is_estimated": True,
            "is_blurred": False,
        }
    )
    assert a.is_estimated is True
    assert a.total_days == 100
    assert a.formatted_value == "3.00 years"
    assert a.is_blurred is False


def test_birthday_input_is_estimated() -> None:
    b = BirthdayInput.model_validate({"year": 2020, "is_estimated": True})
    assert b.is_estimated is True


def test_date_measure_value_is_estimated() -> None:
    d = DateMeasureValue.model_validate({"year": 2020, "month": 5, "is_estimated": True})
    assert d.is_estimated is True


def test_session_date_is_estimated() -> None:
    d = SessionDate.model_validate({"year": 2020, "month": 6, "day": 15, "is_estimated": True})
    assert d.is_estimated is True
