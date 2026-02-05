# CHANGELOG


## v0.1.0-dev.1 (2026-02-05)

### Bug Fixes

- Update test client initialization to use new auth API
  ([`1f41934`](https://github.com/NYU-Databrary/databrarypy/commit/1f4193457e45ca65bf26240a0eaac8ce7c612b7d))

- Update test command in CI workflow to run unit tests specifically
  ([`eb3685d`](https://github.com/NYU-Databrary/databrarypy/commit/eb3685dedfb4df139e28b239332037fabf4deaee))

- Update VolumeDetail model to use File type for thumbnail instead of dict
  ([`8c455e6`](https://github.com/NYU-Databrary/databrarypy/commit/8c455e6a571422f62de3052d31eb6b737ff5a92a))

- **_base**: Add `follow_redirects = True` parameter to httpx.get requests in _request_json.
  ([`588c814`](https://github.com/NYU-Databrary/databrarypy/commit/588c8143e8df81333dc3269e2f84b0a906d7b404))

### Chores

- Consolidate CI and release workflows into a single configuration, enhancing release conditions and
  permissions
  ([`5dd5f49`](https://github.com/NYU-Databrary/databrarypy/commit/5dd5f49d98196d3581724b971ad85cf723dc6ccb))

- Readd authors field to pyproject.toml
  ([`d3cbb23`](https://github.com/NYU-Databrary/databrarypy/commit/d3cbb23441854a8674372cebf702fd08e748ece5))

- Remove authors and license fields from pyproject.toml
  ([`0bc094f`](https://github.com/NYU-Databrary/databrarypy/commit/0bc094f9af5f5a5e8c324a18ad5f3d3e5026815a))

- Update changelog configuration and adjust prerelease tokens in pyproject.toml
  ([`ad1840e`](https://github.com/NYU-Databrary/databrarypy/commit/ad1840e56681705e7c0f9f40bbb8e0050df0d1f0))

- Update CI and release workflows to include temporary feature branch and adjust release conditions
  ([`a3adf48`](https://github.com/NYU-Databrary/databrarypy/commit/a3adf489f424795330ed4406337197e52e77334c))

- Update CI workflow branches to include staging and development
  ([`ea7c787`](https://github.com/NYU-Databrary/databrarypy/commit/ea7c787f35c85a081f8885107fa9f360fdbd6a63))

- Update poetry.lock and pyproject.toml for new dependencies and testing branches
  ([`d4dc41b`](https://github.com/NYU-Databrary/databrarypy/commit/d4dc41bd32c0987a6f36b6335a116831327a7a41))

- Update pyproject.toml for semantic release and add GitHub Actions workflow for automated releases
  ([`9e21210`](https://github.com/NYU-Databrary/databrarypy/commit/9e212101d243947dae3196b303077075bb3b869d))

- **format**: Run `make format`
  ([`f3c7bff`](https://github.com/NYU-Databrary/databrarypy/commit/f3c7bffe3e93f3ee5868f6d9dc8caad0d5db0f21))

### Continuous Integration

- Update GitHub Actions workflow to trigger on main branch instead of feature branch
  ([`b9e9627`](https://github.com/NYU-Databrary/databrarypy/commit/b9e962772ea831ec755023519a05937606e97318))

### Documentation

- Add documentation generation
  ([`bda4d0e`](https://github.com/NYU-Databrary/databrarypy/commit/bda4d0ef7493135406a58b0ea91a345435881c35))

- Clarify Makefile commands for testing and coverage
  ([`e0bdb02`](https://github.com/NYU-Databrary/databrarypy/commit/e0bdb02a35a2c84f06af8c8f1fdf3f2e7f853088))

- Enhance README with .env configuration instructions and update Volume model to allow optional
  fields
  ([`cc339ab`](https://github.com/NYU-Databrary/databrarypy/commit/cc339abdc8ec3bb593a36e30e3ca36cd704f62e7))

- Update README and add resources documentation for Databrary API client
  ([`20169a6`](https://github.com/NYU-Databrary/databrarypy/commit/20169a6c953522b84466089690fe27e1de4e8f8a))

- Update README and client code to clarify optional BASE_URL in environment configuration
  ([`cec7db8`](https://github.com/NYU-Databrary/databrarypy/commit/cec7db8d5e6a62461b700d2e6f7bbdab8dac36b8))

- Update README.md
  ([`e151db1`](https://github.com/NYU-Databrary/databrarypy/commit/e151db13e9bac0b4554a71931343656671a2959d))

### Features

- Add Categories, Funders, Tags, and Search resources with corresponding models and tests
  ([`ece4c25`](https://github.com/NYU-Databrary/databrarypy/commit/ece4c2565b365af89ed0ab8f6fd662d774d7a773))

- Add coverage command to Makefile and CI, enhance tests with fixtures and new test cases
  ([`dd36bf8`](https://github.com/NYU-Databrary/databrarypy/commit/dd36bf835c3aba71f6122a0d0cbebd752bd53dc9))

- Add Folders, Records, and Sessions resources with corresponding models and tests
  ([`5582ce8`](https://github.com/NYU-Databrary/databrarypy/commit/5582ce8dc09c0c8e88b9b74a31f3d2044fa54f49))

- Add institutions and users resources, along with related models for institution and user data
  ([`7e7fc09`](https://github.com/NYU-Databrary/databrarypy/commit/7e7fc094ee68966ff5f67626b2253cfd10de3a23))

- Add institutions and users resources, along with related models for institution and user data
  ([`b73948b`](https://github.com/NYU-Databrary/databrarypy/commit/b73948b1e851b18d82db4e9f819b35de10d677d9))

- Add iterator tests for folders, institutions, sessions, users, and volumes in integration tests
  ([`ce0ca57`](https://github.com/NYU-Databrary/databrarypy/commit/ce0ca57aeeecf7154fef10fc05babc96202637e4))

- Add permission and release level models, supported file types, and corresponding methods in
  SystemResource
  ([`71a56e3`](https://github.com/NYU-Databrary/databrarypy/commit/71a56e3acaa1534e9f494dda7f40d1377dce0a92))

- Add python-dotenv dependency and add context management to auth and client
  ([`69d733d`](https://github.com/NYU-Databrary/databrarypy/commit/69d733d1d1abafef3d36ec51ef6d0772a90aaa5d))

- Add Requests models, update UserPublic to include pending requests
  ([`51a8d98`](https://github.com/NYU-Databrary/databrarypy/commit/51a8d98835d1b17bf1550d259a18c1d78b8306e0))

- Add VolumesResource and related models for volume management
  ([`d5e52a9`](https://github.com/NYU-Databrary/databrarypy/commit/d5e52a974b1147cfe66252ee0bbfd75815e2ccdc))

- Added integration tests and adjusted models
  ([`d556af6`](https://github.com/NYU-Databrary/databrarypy/commit/d556af67eb0b853ef684a2259ba16708d19f22f6))

- Enhance Age and Session models with additional fields and improve test fixtures for records and
  users
  ([`327392a`](https://github.com/NYU-Databrary/databrarypy/commit/327392a58a743b3b29489be3be9b422313843520))

- Enhance client configuration with environment variable support and improve test fixtures
  ([`8485caf`](https://github.com/NYU-Databrary/databrarypy/commit/8485caf2a2e6b979ea685729829b8a01da5e2925))

- Implement file download capabilities in resources with corresponding models and tests
  ([`29e3cb0`](https://github.com/NYU-Databrary/databrarypy/commit/29e3cb0a35d711ac384af141a2fd18f153e33d79))

- Implement retry logic and error handling in API client with typed exceptions
  ([`0c8811e`](https://github.com/NYU-Databrary/databrarypy/commit/0c8811ecf53024c745785df6274f4e75eb5c8469))

- Initial project setup for Databrary Python client
  ([`a5357bb`](https://github.com/NYU-Databrary/databrarypy/commit/a5357bb9fe819c64039fbd581c975a1e5edca768))

- Introduce activity tracking models and methods for user and volume history
  ([`351a53f`](https://github.com/NYU-Databrary/databrarypy/commit/351a53f6394036ac944286ff5fcce8a7cf7b04d0))

- Introduce TASK_STATUS_PROCESSING constant and update tests to use it for task status assertions
  ([`86b810a`](https://github.com/NYU-Databrary/databrarypy/commit/86b810a1ab33a699c537e3945c019436d18aefab))

- Refactor authentication process in DatabraryClient to use credentials from initialization and
  update README and tests accordingly
  ([`526b20f`](https://github.com/NYU-Databrary/databrarypy/commit/526b20f8780cfe986272a51b13576b6d91e7e383))

- Refactor resources, implement normalization for API responses, and enhance pagination handling
  ([`1a44d3c`](https://github.com/NYU-Databrary/databrarypy/commit/1a44d3cc54eaeeedf0a2d12c829746404d865b34))

- Refactor resources, implement normalization for API responses, and enhance pagination handling
  ([`3e758eb`](https://github.com/NYU-Databrary/databrarypy/commit/3e758ebac26d631b67d703e587dafc86738f4571))

- **models**: Add age metadata fields
  ([`95b0279`](https://github.com/NYU-Databrary/databrarypy/commit/95b0279f0b6f0e59541c02a2f4f5a379477c34e1))

- **models**: Add totp_enrolled_at field to UserSlim
  ([`535398c`](https://github.com/NYU-Databrary/databrarypy/commit/535398c163ecde9e0434a351db86c3a1b7fa493f))

Add TOTP enrollment timestamp field matching Django DateTimeField.

### Refactoring

- Modify users resource to return a list of sponsorships directly and update related tests
  ([`bb4a991`](https://github.com/NYU-Databrary/databrarypy/commit/bb4a991fe79482742203d5b1e48ef46af7f0c1eb))

- Rename search hit classes to search result for clarity and update related resource methods
  ([`6e801df`](https://github.com/NYU-Databrary/databrarypy/commit/6e801df5047acabe804f3489a6b5f8015c91fe54))

- Rename VolumeCollaboratorView to VolumeCollaborator and update related resource methods
  ([`8796db5`](https://github.com/NYU-Databrary/databrarypy/commit/8796db51104c0f3a49e88243817a628b9ed56796))

- Simplify affiliates method in UsersResource to return a list and update related tests
  ([`074743b`](https://github.com/NYU-Databrary/databrarypy/commit/074743bea73a262218a91486da8e80af0592288d))

- Update authentication method in tests to use new login approach with credentials from
  initialization
  ([`c7e7f94`](https://github.com/NYU-Databrary/databrarypy/commit/c7e7f94003ee4cc280cf7b21bf2bd1a26667b33e))

- Update Databrary client to use SystemResource for system statistics and adjust README and tests
  accordingly
  ([`a16b4fd`](https://github.com/NYU-Databrary/databrarypy/commit/a16b4fddade81f4198fee7e54c64992b44cd68ac))

- Update method names in integration tests for institutions and pagination iterators
  ([`88b3de0`](https://github.com/NYU-Databrary/databrarypy/commit/88b3de0e2811a2debda7c723d8665ce7d597a49a))

- Update model configurations to enforce stricter validation by changing 'extra' from 'ignore' to
  'forbid' across multiple models
  ([`e3e048b`](https://github.com/NYU-Databrary/databrarypy/commit/e3e048b5938dd558dfdeaaf7bfc071f6d403da79))

- Update models to enforce required fields and improve type definitions across various entities
  ([`b247a80`](https://github.com/NYU-Databrary/databrarypy/commit/b247a808d52616d81bed056238d9f17adcad88b8))

- Update models to enforce required fields and improve type definitions across various entities
  ([`6985793`](https://github.com/NYU-Databrary/databrarypy/commit/6985793bc71c22584a5f74032b0c5948213af38e))

- Update type hints in models and rebuild to resolve forward references
  ([`504d155`](https://github.com/NYU-Databrary/databrarypy/commit/504d155fc493baf5f101fabf41a4ef5d19b67fee))

### Testing

- Enhance institution avatar tests to verify file existence after saving
  ([`ca8cd19`](https://github.com/NYU-Databrary/databrarypy/commit/ca8cd1900b8276143e9fd27f6700fd9e0db2b694))

- Enhance user affiliates tests with active and expired scenarios and add mock data
  ([`35ccea3`](https://github.com/NYU-Databrary/databrarypy/commit/35ccea3c2c6ebb31bbe75510fff4b05dfff999ed))

- Refactor folder and session tests to utilize mock data for consistency and reliability
  ([`65ca8f9`](https://github.com/NYU-Databrary/databrarypy/commit/65ca8f9385747fde010608daff1717fdc47e829c))

- Update institutions list test to use mock data for search parameter
  ([`591398f`](https://github.com/NYU-Databrary/databrarypy/commit/591398f91f2185dd8d80a21aa535e032eb75273c))

- Update session tests to use new mock session file data for improved accuracy
  ([`23481df`](https://github.com/NYU-Databrary/databrarypy/commit/23481dfa1fe70c58706f2a71a1b3f90f04f6a428))

- Update volume tests to use mock data and constants for improved reliability
  ([`87a1a92`](https://github.com/NYU-Databrary/databrarypy/commit/87a1a92e5e0d768966bd3249a704ceccea7e1d61))
