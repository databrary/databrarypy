# Resource Reference

This library exposes resource classes on `DatabraryClient`.

- `client.system: SystemResource`
- `client.search: SearchResource`
- `client.users: UsersResource`
- `client.institutions: InstitutionsResource`
- `client.volumes: VolumesResource`
- `client.sessions: SessionsResource`
- `client.folders: FoldersResource`
- `client.records: RecordsResource`
- `client.funders: FundersResource`
- `client.tags: TagsResource`
- `client.categories: CategoriesResource`

## UsersResource

- `page(search=None, page=None, page_size=None, include_suspended=None, exclude_self=None, is_authorized_investigator=None, has_api_access=None) -> Page[UserSlim]`: List users (paginated)
- `list(search=None, page=None, page_size=None, include_suspended=None, exclude_self=None, is_authorized_investigator=None, has_api_access=None) -> Iterator[UserSlim]`: Iterate all users
- `retrieve(user_id: int, for_self: bool = False) -> UserPublic | UserSelf`: Get a user
- `sponsors(user_id: int) -> list[Sponsorship]`: Sponsorships where user is affiliate
- `affiliates(user_id: int, include_expired: bool | None = None) -> list[Sponsorship]`: Sponsorships where user is sponsor
- `volumes_page(user_id: int, page=None, page_size=None) -> Page[VolumeListItem]`
- `volumes_list(user_id: int, page=None, page_size=None) -> Iterator[VolumeListItem]`
- `avatar(user_id: int, dest_path: str | None = None) -> bytes | str`: Bytes or saved path
- `activity_page(user_id: int, page=None, page_size=None) -> Page[UserActivityItem]`
- `activity_list(user_id: int, page=None, page_size=None) -> Iterator[UserActivityItem]`

Example:
```python
for u in client.users.list(search="doe", page_size=200):
    print(u.id, u.full_name)
```

## VolumesResource

- `page(search=None, ordering=None, page=None, page_size=None) -> Page[VolumeListItem]`
- `list(search=None, ordering=None, page=None, page_size=None) -> Iterator[VolumeListItem]`
- `retrieve(volume_id: int) -> VolumeDetail`
- `tags(volume_id: int) -> list[str]`
- `links(volume_id: int) -> list[VolumeLink]`
- `fundings(volume_id: int) -> list[VolumeFundingRead]`
- `collaborators(volume_id: int) -> list[VolumeCollaborator]`
- `collaborator(volume_id: int, collaborator_id: int) -> VolumeCollaborator`
- `activity_page(volume_id: int, page=None, page_size=None) -> Page[VolumeActivityItem]`
- `activity_list(volume_id: int, page=None, page_size=None) -> Iterator[VolumeActivityItem]`
- `request_zip_download(volume_id: int) -> ProcessingTask`
- `request_csv_download(volume_id: int) -> ProcessingTask`

## SessionsResource

- `page(volume_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Page[Session]`
- `list(volume_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Iterator[Session]`
- `retrieve(volume_id: int, session_id: int) -> Session`
- Files under a session:
  - `files_page(volume_id: int, session_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Page[File]`
  - `files_list(volume_id: int, session_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Iterator[File]`
  - `get_file(volume_id: int, session_id: int, file_id: int) -> File`
  - `get_file_download_link(volume_id: int, session_id: int, file_id: int) -> FileDownloadLink`
  - `download_file(volume_id: int, session_id: int, file_id: int, dest_path: str | None = None) -> bytes | str`
- Asynchronous:
  - `request_zip_download(volume_id: int, session_id: int) -> ProcessingTask`
  - `request_csv_download(volume_id: int, session_id: int) -> ProcessingTask`

## FoldersResource

- `page(volume_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Page[Folder]`
- `list(volume_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Iterator[Folder]`
- `retrieve(volume_id: int, folder_id: int) -> Folder`
- Files under a folder:
  - `files_page(volume_id: int, folder_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Page[File]`
  - `files_list(volume_id: int, folder_id: int, search=None, date_from=None, date_to=None, release_level=None, page=None, page_size=None) -> Iterator[File]`
  - `get_file(volume_id: int, folder_id: int, file_id: int) -> File`
  - `get_file_download_link(volume_id: int, folder_id: int, file_id: int) -> FileDownloadLink`
  - `download_file(volume_id: int, folder_id: int, file_id: int, dest_path: str | None = None) -> bytes | str`
- Asynchronous:
  - `request_zip_download(volume_id: int, folder_id: int) -> ProcessingTask`

## RecordsResource

- `page(volume_id: int, category_id: int | None = None, page=None, page_size=None) -> Page[Record]`
- `list(volume_id: int, category_id: int | None = None, page=None, page_size=None) -> Iterator[Record]`
- `retrieve(volume_id: int, record_id: int) -> Record`

## SearchResource

- Users:
  - `users_page(q=None, filter=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Page[UserSearchResult]`
  - `users_list(q=None, filter=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Iterator[UserSearchResult]`
- Institutions:
  - `institutions_page(q=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Page[InstitutionSearchResult]`
  - `institutions_list(q=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Iterator[InstitutionSearchResult]`
- Volumes:
  - `volumes_page(q=None, files_release_levels=None, tag=None, sharing_level=None, format_categories=None, formats=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Page[VolumeSearchResult]`
  - `volumes_list(q=None, files_release_levels=None, tag=None, sharing_level=None, format_categories=None, formats=None, page=None, page_size=None, sort_by=None, sort_order=None) -> Iterator[VolumeSearchResult]`

## SystemResource

- `get_db_stats() -> Stats`
- `list_asset_formats() -> GroupedFormats`
- `get_supported_file_types() -> SupportedFileTypes`
- `get_permission_levels() -> PermissionLevels`
- `get_release_levels() -> ReleaseLevels`
- `is_healthy() -> bool`

## InstitutionsResource

- `page(search=None, page=None, page_size=None) -> Page[Institution]`
- `list(search=None, page=None, page_size=None) -> Iterator[Institution]`
- `retrieve(institution_id: int) -> Institution`
- `avatar(institution_id: int, dest_path: str | None = None) -> bytes | str`
- `authorized_investigators(institution_id: int, page=None, page_size=None) -> list[UserSlim]`

## FundersResource

- `list(include_all: bool | None = None, is_approved: bool | None = None) -> list[Funder]`
- `retrieve(funder_id: int) -> Funder`

## TagsResource

- `page(search=None, page=None, page_size=None, ordering=None) -> Page[Tag]`
- `list(search=None, page=None, page_size=None, ordering=None) -> Iterator[Tag]`
- `retrieve(tag_id: int) -> Tag`

## CategoriesResource

- `list() -> list[Category]`
- `retrieve(category_id: int) -> Category`
