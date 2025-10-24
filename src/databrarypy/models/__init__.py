"""Data models for Databrary API responses."""

from .affiliate_requests import AffiliateAccessRequest
from .categories import Category, Metric
from .files import File
from .folders import Folder
from .formats import Format, GroupedFormats
from .funders import Funder
from .history import HistoryUser, UserActivityItem, VolumeActivityItem
from .institution_requests import InstitutionAccessRequest
from .institution_sponsorship import InstitutionSponsorship
from .institutions import Institution
from .levels import PermissionLevels, ReleaseLevels
from .paginated import Page
from .records import Record
from .sessions import Session
from .sponsorships import Sponsorship
from .stats import Stats
from .supported_types import SupportedFileType, SupportedFileTypes
from .tags import Tag
from .users import SuspendedBy, UserPublic, UserSelf, UserSlim
from .volume_shared import VolumeFundingRead, VolumeLink
from .volumes import (
    VolumeCollaborator,
    VolumeDetail,
    VolumeListItem,
    VolumePreview,
)
from .whoami import WhoAmI

# Rebuild models to resolve forward references
File.model_rebuild()
Folder.model_rebuild()
InstitutionSponsorship.model_rebuild()
UserSlim.model_rebuild()
UserPublic.model_rebuild()
UserSelf.model_rebuild()
VolumeListItem.model_rebuild()
VolumePreview.model_rebuild()

__all__ = [
    "AffiliateAccessRequest",
    "Category",
    "File",
    "Folder",
    "Format",
    "Funder",
    "GroupedFormats",
    "HistoryUser",
    "Institution",
    "InstitutionAccessRequest",
    "InstitutionSponsorship",
    "Metric",
    "Page",
    "PermissionLevels",
    "Record",
    "ReleaseLevels",
    "Session",
    "Sponsorship",
    "Stats",
    "SupportedFileType",
    "SupportedFileTypes",
    "SuspendedBy",
    "Tag",
    "UserActivityItem",
    "UserPublic",
    "UserSelf",
    "UserSlim",
    "VolumeActivityItem",
    "VolumeCollaborator",
    "VolumeDetail",
    "VolumeFundingRead",
    "VolumeLink",
    "VolumeListItem",
    "VolumePreview",
    "WhoAmI",
]
