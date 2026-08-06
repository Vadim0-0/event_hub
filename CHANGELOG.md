# Changelog

All notable changes to this project will be documented in this file.
## [Unreleased]

### Bug Fixes

- Avoid referencing event title when event is missing by @Vadim0-0

- Allow spaces in username validation by @Vadim0-0

- **ci**: Correct typo in test env file path by @Vadim0-0

- **ci**: Rename default to defaults in workflow by @Vadim0-0

- **ci**: Rename evn to env in workflow by @Vadim0-0

- **ci**: Set working-directory for lint job by @Vadim0-0

- **ci**: Move dependabot config to .github/dependabot.yml by @Vadim0-0

- **ci**: Use docker-compose ecosystem in Dependabot by @Vadim0-0

- **web**: Correct nginx proxy path for Nuxt dev server by @Vadim0-0

- **nginx**: Proxy API under /api and enable WebSocket upgrades by @Vadim0-0

- **api**: Use settings singleton in test conftest by @Vadim0-0

- **web**: Correct Dockerfile production stage indentation by @Vadim0-0

- **api**: Add greenlet dependency and remove settings cache clear from tests by @Vadim0-0

- **web**: Scope notification component styles by @Vadim0-0

- **web**: Attach JWT from cookie on each API request by @Vadim0-0

- **web**: Correct notification container width class by @Vadim0-0

- **api**: Fix event detail cache and invalidate lists on join/leave by @Vadim0-0

- **web**: Show authenticated username in main header by @Vadim0-0

- **api**: Invalidate joined and user event list caches by @Vadim0-0

- **web**: Update users nav route to events slot page by @Vadim0-0

- **web**: Always open event info from event cards by @Vadim0-0

- **api**: Pass CORS allow_headers as list by @Vadim0-0

- **api**: Return only verified users in users list by @Vadim0-0

- **web**: Correct primary button border color variable by @Vadim0-0

- **web**: Redirect authenticated users to all events page by @Vadim0-0


### Documentation

- Add project README in English and Russian by @Vadim0-0


### Features

- Add FastAPI app bootstrap and database setup by @Vadim0-0

- Add User, Event and Registration models by @Vadim0-0

- Add user registration and JWT auth by @Vadim0-0

- Add events CRUD endpoints by @Vadim0-0

- Add event registration logic by @Vadim0-0

- Add event list, detail and user events endpoints by @Vadim0-0

- Add event update endpoint by @Vadim0-0

- Add event delete endpoint by @Vadim0-0

- Add event leave endpoint by @Vadim0-0

- Add Redis caching for event endpoints by @Vadim0-0

- Add Redis caching for event endpoints by @Vadim0-0

- Add ARQ background worker for notifications by @Vadim0-0

- Add nginx reverse proxy for API by @Vadim0-0

- Persist sent notifications to database in worker tasks by @Vadim0-0

- Add GET /notifications/my endpoint with Redis cache by @Vadim0-0

- Add Notification SQLAlchemy model by @Vadim0-0

- **api**: Support canceling event registrations by @Vadim0-0

- **web**: Build landing page with Lenis smooth scroll by @Vadim0-0

- **web**: Add Inter font, reset styles, and Tailwind theme by @Vadim0-0

- **web**: Add Inter font by @Vadim0-0

- **web**: Extract page content to localized JSON structure by @Vadim0-0

- **web**: Add footer component and scroll-to-top button to default layout by @Vadim0-0

- **web**: Configure i18n module and update nuxt config by @Vadim0-0

- **api**: Add CORS middleware and registration conflict errors by @Vadim0-0

- **web**: Add useApi composable with JWT and error parsing by @Vadim0-0

- **web**: Add global toast notifications by @Vadim0-0

- **web**: Add auth pages with login and registration by @Vadim0-0

- **web**: Add global loader by @Vadim0-0

- **api**: Add GET /events/joined/me endpoint by @Vadim0-0

- **web**: Add auth middleware and session handling by @Vadim0-0

- **web**: Add main layout sidebar header by @Vadim0-0

- **web**: Add events store scaffold by @Vadim0-0

- **api**: Add GET /events/me/stats endpoint by @Vadim0-0

- **web**: Load and display user event stats in main header by @Vadim0-0

- **web**: Add collapsible main header with localized navigation by @Vadim0-0

- **web**: Add events slot page scaffold by @Vadim0-0

- **web**: Add UiButton and extend UiInput with inputClass by @Vadim0-0

- **web**: Build all events page layout with search and sorting by @Vadim0-0

- **api**: Migrate event and notification ids to UUID v7 by @Vadim0-0

- **api**: Enhance events list and detail responses by @Vadim0-0

- **web**: Add events list with search, sort, and pagination by @Vadim0-0

- **web**: Add event detail side panel by @Vadim0-0

- **web**: Add join and leave actions in event detail panel by @Vadim0-0

- **web**: Localize all events page and animate event cards by @Vadim0-0

- **api**: Add search, sort, and count to user events endpoint by @Vadim0-0

- **web**: Add my events list with search and pagination by @Vadim0-0

- **web**: Add number stepper controls to UiInput by @Vadim0-0

- **web**: Add resizable UiTextarea component by @Vadim0-0

- **web**: Add UiDate picker component by @Vadim0-0

- **web**: Add UiTime picker component by @Vadim0-0

- **web**: Add useHeightTransition composable by @Vadim0-0

- **web**: Add event setup store and form validation by @Vadim0-0

- **web**: Add event setup panel with create, edit, and delete by @Vadim0-0

- **web**: Wire event setup flow into layout and events pages by @Vadim0-0

- **web**: Add primary, delete, and cancel button styles by @Vadim0-0

- **api**: Add user events list and count endpoints by @Vadim0-0

- **api**: Add search, sort, and count to joined events by @Vadim0-0

- **web**: Add joined events page with search and pagination by @Vadim0-0

- **web**: Add user and participant types by @Vadim0-0

- **web**: Add composables for users, user events, and participants by @Vadim0-0

- **web**: Add expandable UserCard with user events list by @Vadim0-0

- **web**: Add event participants panel in EventInfo by @Vadim0-0

- **web**: Add users page with search and pagination by @Vadim0-0

- **api**: Add SMTP mail delivery and Mailhog for local dev by @Vadim0-0

- **api**: Add email verification flow on registration by @Vadim0-0

- **web**: Add UiVerification code input component by @Vadim0-0

- **web**: Add useResendCooldown composable by @Vadim0-0

- **web**: Add verifyEmail and resendVerificationCode to auth store by @Vadim0-0

- **web**: Add email verification step to auth flow by @Vadim0-0

- **web**: Add password visibility toggle to UiInput by @Vadim0-0

- **api**: Add user profile update and email change flow by @Vadim0-0

- **api**: Add remove participant endpoint and notification

- **web**: Add remove participant action in event info panel


### Miscellaneous

- Add Docker, Alembic and project scaffolding by @Vadim0-0

- Ignore .env.test files by @Vadim0-0

- Add Makefile for Docker and dev workflow by @Vadim0-0

- Remove redundant module header comments by @Vadim0-0

- Translate Makefile comments to English by @Vadim0-0

- Pin dependency versions and add ruff by @Vadim0-0

- Migrate API packaging to pyproject.toml by @Vadim0-0

- Track VS Code settings and ignore build artifacts by @Vadim0-0

- Restrict setuptools packages and ignore egg-info artifacts by @Vadim0-0

- Fix ruff lint warnings by @Vadim0-0

- Extend gitignore for Nuxt and Node artifacts by @Vadim0-0

- Add .env.example with app and service defaults by @Vadim0-0

- **api**: Extend JWT access token lifetime to 24 hours by @Vadim0-0

- **api**: Bump Python to 3.14 and update asyncpg by @Vadim0-0

- Set default postgres port to 5432 in env example by @Vadim0-0

- **api**: Ignore unused imports in test files by @Vadim0-0

- **api**: Allow localhost without port in CORS origins by @Vadim0-0

- **web**: Switch favicon to svg and fix icon API path by @Vadim0-0

- Add pyright config and VS Code python settings by @Vadim0-0

- **docker**: Pass SMTP and ARQ env vars to api and worker by @Vadim0-0

- **docker**: Mount api volume in dev worker and simplify env by @Vadim0-0

- **api**: Extend SMTP settings and reorganize config by @Vadim0-0

- Use dev compose for down, logs, and migrate commands by @Vadim0-0

- **docker**: Keep SMTP env on worker only by @Vadim0-0


### Refactoring

- **web**: Use composable-based content in index page by @Vadim0-0

- **web**: Reuse shared localized page types in index types by @Vadim0-0

- **web**: Simplify auth middleware to use route meta by @Vadim0-0

- **web**: Improve UiButton class prop typing by @Vadim0-0

- **web**: Animate UiDate popup with height transition by @Vadim0-0

- **web**: Animate UiTime popup with height transition by @Vadim0-0

- **web**: Use UiButton style types in EventInfo by @Vadim0-0

- **api**: Move user event routes to users router and add users list by @Vadim0-0

- **web**: Update API paths for user events endpoints by @Vadim0-0

- **web**: Improve useHeightTransition composable by @Vadim0-0

- **api**: Split services into domain packages by @Vadim0-0

- **api**: Restructure notifications with dispatch and handlers by @Vadim0-0


### Style

- **web**: Update reset styles and tailwind theme configuration by @Vadim0-0

- **web**: Integrate Nuxt UI and add auth theme tokens by @Vadim0-0

- **web**: Reset outline and border on base links by @Vadim0-0

- **web**: Adjust theme color and notification layering by @Vadim0-0

- **web**: Add secondary text color token by @Vadim0-0

- **web**: Refine form inputs, card ring, and theme color by @Vadim0-0

- **web**: Polish login form and header border radius by @Vadim0-0

- **web**: Fix primary button border colors by @Vadim0-0

- **web**: Widen notification container by @Vadim0-0

- **web**: Change howWork section background on landing page by @Vadim0-0

- **web**: Polish auth forms layout and headings by @Vadim0-0


### Tests

- Add API test suite with PostgreSQL setup by @Vadim0-0

- Add event update endpoint tests by @Vadim0-0

- Add event update delete tests by @Vadim0-0

- Add event leave endpoint tests by @Vadim0-0

- Add join event when already started test by @Vadim0-0

- Fix event join and delete test bugs by @Vadim0-0

- Mock ARQ enqueue in test fixtures by @Vadim0-0

- **api**: Expect 409 for duplicate email registration by @Vadim0-0

- **api**: Update user events URL from /my to /me by @Vadim0-0

- **api**: Add email verification auth tests and helpers by @Vadim0-0

- **api**: Add user profile and email change tests by @Vadim0-0


### Ci

- Add GitHub Actions workflow for pytest by @Vadim0-0

- Add GitHub Actions workflow for migration by @Vadim0-0

- Add docker-build job to GitHub Actions workflow by @Vadim0-0

- Switch workflow to pyproject and add ruff lint job by @Vadim0-0

- Disable ruff format check in workflow by @Vadim0-0

- Add Dependabot configuration by @Vadim0-0

- Ignore postgres major version updates in Dependabot by @Vadim0-0

- Bump Python version to 3.14 in workflow by @Vadim0-0


### Hore

- **docker**: Add web service to docker-compose by @Vadim0-0

<!-- generated by git-cliff -->
