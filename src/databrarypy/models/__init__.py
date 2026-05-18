"""Data models for Databrary API responses."""

from .affiliate_requests import AffiliateAccessRequest
from .categories import Category, Metric
from .files import File
from .folders import Folder, FolderDuplicateFileCheckItem
from .formats import Format, GroupedFormats
from .funders import Funder
from .history import HistoryUser, UserActivityItem, VolumeActivityItem
from .institution_requests import InstitutionAccessRequest
from .institution_sponsorship import InstitutionSponsorship
from .institutions import Institution
from .levels import PermissionLevels, ReleaseLevels
from .paginated import Page
from .records import AgeInput, BirthdayInput, DateMeasureValue, ParticipantInput, Record
from .sessions import Session, SessionDuplicateFileCheckItem
from .sponsorships import Sponsorship
from .statistics import InstitutionStatistics, UserStatistics
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
Session.model_rebuild()
InstitutionSponsorship.model_rebuild()
UserSlim.model_rebuild()
UserPublic.model_rebuild()
UserSelf.model_rebuild()
VolumeListItem.model_rebuild()
VolumePreview.model_rebuild()

__all__ = [
    "AffiliateAccessRequest",
    "AgeInput",
    "BirthdayInput",
    "Category",
    "File",
    "Folder",
    "FolderDuplicateFileCheckItem",
    "Format",
    "Funder",
    "GroupedFormats",
    "HistoryUser",
    "Institution",
    "InstitutionAccessRequest",
    "InstitutionSponsorship",
    "InstitutionStatistics",
    "Metric",
    "DateMeasureValue",
    "Page",
    "ParticipantInput",
    "PermissionLevels",
    "Record",
    "ReleaseLevels",
    "Session",
    "SessionDuplicateFileCheckItem",
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
    "UserStatistics",
    "VolumeActivityItem",
    "VolumeCollaborator",
    "VolumeDetail",
    "VolumeFundingRead",
    "VolumeLink",
    "VolumeListItem",
    "VolumePreview",
    "WhoAmI",
]
