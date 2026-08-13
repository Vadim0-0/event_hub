# Event Hub

> [Русская версия](README-RU.md)

Event management platform: user registration, event creation, participant enrollment, direct messaging, and notifications.

A learning pet project showcasing async Python, SQLAlchemy 2.0, background jobs, and a full Docker-based stack.

## Features

- **Authentication** — email verification, registration and login via JWT (python-jose + bcrypt)
- **User profiles** — username updates, password change, email change with confirmation
- **Timezones** — IANA timezone per user (e.g. `Europe/Moscow`), validated at registration
- **Events** — CRUD, filtering, pagination, participant limits, event history
- **Registrations** — join and leave events with validation
- **Messaging** — 1-on-1 chats between users: conversations, message history, read status, unread counter
- **Notifications** — background processing via ARQ worker and Redis (including new messages)
- **Caching** — Redis for frequently accessed data (events, conversations, unread counts)
- **Frontend** — Nuxt 4 SPA with Pinia and i18n
- **Testing** — pytest + httpx for core API logic
- **Infrastructure** — Docker Compose (PostgreSQL, Redis, Nginx)

### Timezones

- Each user stores an IANA timezone (`UTC` by default) in their profile.
- Timezones are validated with Python `zoneinfo` (e.g. `Asia/Tokyo`, `America/New_York`).
- All datetimes in the database are stored in UTC (`DateTime(timezone=True)`); the user's timezone is available for display on the client.

### Messaging

- Private conversations between two registered users.
- Cursor-based message pagination, soft delete for the sender's own messages.
- Read/unread tracking with a global unread counter.
- New messages trigger in-app notifications and cache invalidation in Redis.

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3.14, FastAPI, Pydantic v2 |
| ORM & DB | SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic |
| Auth | JWT (python-jose), bcrypt |
| Cache & Jobs | Redis, ARQ |
| Frontend | Nuxt 4, Vue 3, Pinia, Tailwind CSS |
| Tests | pytest, pytest-asyncio, httpx |
| Infra | Docker, Docker Compose, Nginx |

## Quick Start

### Requirements

- Docker and Docker Compose

### Getting Started

1. **Clone the repository and enter the project directory:**

   ```bash
   git clone <your-repo-url>
   cd event_hub
   ```

2. **Configure environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start the services:**

   ```bash
   docker compose up -d --build
   # or
   make up
   ```

4. **Verify everything is running:**

   | Service | URL |
   |---------|-----|
   | Web (Nginx) | http://localhost |
   | API | http://localhost/api |
   | Swagger | http://localhost/api/docs |
   | Health check | http://localhost/health |

## Development

For local development with API hot reload and a dedicated frontend port:

```bash
make dev
# or
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Web | http://localhost:3000 |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | localhost:`POSTGRES_PORT` (default: 5436) |

### Useful Commands (Makefile)

```bash
make help          # list all commands
make down          # stop containers
make logs          # follow API logs
make migrate       # apply migrations
make migration msg="description"  # create a migration
make test-docker   # run pytest inside the container
make shell-api     # shell into the api container
make shell-db      # open psql in postgres
```

### Migrations

```bash
make migration msg="initial schema"
make migrate
```

The test database `event_hub_test` is created automatically on the first PostgreSQL startup (script: `docker/postgres/init-test-db.sql`).

To run pytest locally without Docker, configure `api/tests/.env.test` using `api/tests/.env.test.example` as a reference.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Password | `password` |
| `POSTGRES_DB` | Database name | `event_hub` |
| `POSTGRES_PORT` | PostgreSQL port on the host | `5436` |
| `SECRET_KEY` | JWT signing key | random string |
| `REDIS_PORT` | Redis port on the host | `6379` |
| `PGADMIN_DEFAULT_EMAIL` | pgAdmin email (dev) | `admin@local.dev` |
| `PGADMIN_DEFAULT_PASSWORD` | pgAdmin password (dev) | `admin` |
| `NUXT_PUBLIC_API_BASE` | API base URL for the frontend | `http://localhost/api` |

## API Overview

Full documentation is available in Swagger (`/docs`). Summary:

### Auth & Users

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register (sends verification code; accepts `timezone`) |
| POST | `/auth/verify-email` | Confirm email and receive JWT |
| POST | `/auth/resend-verification-code` | Resend verification code |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/auth/me` | Current user (includes `timezone`) |
| GET | `/users/` | List registered users |
| PATCH | `/users/me` | Update profile |
| GET | `/users/me/events` | Events created by the current user |
| GET | `/users/me/joined-events` | Events the current user joined |

### Events

| Method | Path | Description |
|--------|------|-------------|
| POST | `/events/` | Create an event |
| GET | `/events/` | List upcoming events (filters, pagination) |
| GET | `/events/history` | Past events |
| GET | `/events/{id}` | Event details |
| PATCH | `/events/{id}` | Update an event |
| DELETE | `/events/{id}` | Delete an event |
| POST | `/events/{id}/join` | Join an event |
| DELETE | `/events/{id}/leave` | Leave an event |
| GET | `/events/{id}/participants` | Event participants |

### Conversations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/conversations/` | List user's conversations |
| POST | `/conversations/` | Start or get a conversation with another user |
| GET | `/conversations/unread-count` | Total unread messages |
| GET | `/conversations/{id}/messages` | Message history (cursor pagination) |
| POST | `/conversations/{id}/messages` | Send a message |
| POST | `/conversations/{id}/read` | Mark conversation as read |
| DELETE | `/conversations/{id}/soft_delete_message` | Soft-delete own message |

### Other

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications/my` | User notifications |
| GET | `/health` | Health check |

## Project Structure

```
event_hub/
├── api/           # FastAPI backend, migrations, tests, ARQ worker
├── web/           # Nuxt frontend
├── nginx/         # Reverse proxy (API + Web)
├── docker/        # PostgreSQL init scripts
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```
