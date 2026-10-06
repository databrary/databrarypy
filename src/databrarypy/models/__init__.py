"""Data models for Databrary API responses."""

from .affiliate_requests import AffiliateAccessRequest
from .categories import Category, Metric
from .files import File
from .folders import Folder, FolderDuplicateFileCheckItem, FolderMutation
from .formats import Format, GroupedFormats
from .funders import Funder
from .history import HistoryUser, UserActivityItem, VolumeActivityItem
from .institution_requests import InstitutionAccessRequest
from .institution_sponsorship import InstitutionSponsorship
from .institutions import Institution
from .levels import PermissionLevels, ReleaseLevels
from .paginated import Page
from .records import AgeInput, BirthdayInput, DateMeasureValue, ParticipantInput, Record
from .sessions import Session, SessionDuplicateFileCheckItem, SessionMutation
from .sponsorships import Sponsorship
from .statistics import InstitutionStatistics, UserStatistics
from .stats import Stats
from .supported_types import SupportedFileType, SupportedFileTypes
from .tags import Tag
from .uploads import (
    TERMINAL_FAILURE_STATUSES,
    InitiateMultipartResponse,
    InitiateResponse,
    InitiateSingleResponse,
    Part,
    PartUrl,
    UploadResult,
    UploadStatus,
)
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
    "FolderMutation",
    "Format",
    "Funder",
    "GroupedFormats",
    "HistoryUser",
    "InitiateMultipartResponse",
    "InitiateResponse",
    "InitiateSingleResponse",
    "Institution",
    "InstitutionAccessRequest",
    "InstitutionSponsorship",
    "InstitutionStatistics",
    "Metric",
    "DateMeasureValue",
    "Page",
    "Part",
    "PartUrl",
    "ParticipantInput",
    "PermissionLevels",
    "Record",
    "ReleaseLevels",
    "Session",
    "SessionDuplicateFileCheckItem",
    "SessionMutation",
    "Sponsorship",
    "Stats",
    "SupportedFileType",
    "SupportedFileTypes",
    "SuspendedBy",
    "TERMINAL_FAILURE_STATUSES",
    "Tag",
    "UploadResult",
    "UploadStatus",
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
