"""Databrary Python client library.

A Python client library for interacting with the Databrary API.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("databrarypy")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"
from .client import DatabraryClient
from .resources import (
    CategoriesResource,
    FoldersResource,
    FundersResource,
    InstitutionsResource,
    RecordsResource,
    SearchResource,
    SessionsResource,
    SystemResource,
    TagsResource,
    UploadsResource,
    UsersResource,
    VolumesResource,
)

__all__ = [
    "DatabraryClient",
    "CategoriesResource",
    "FoldersResource",
    "FundersResource",
    "InstitutionsResource",
    "RecordsResource",
    "SearchResource",
    "SessionsResource",
    "SystemResource",
    "TagsResource",
    "UploadsResource",
    "UsersResource",
    "VolumesResource",
]
