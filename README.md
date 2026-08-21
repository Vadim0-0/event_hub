# Event Hub

> [Русская версия](README-RU.md)

Event management platform: user registration, event creation with map locations, participant enrollment, direct messaging, AI assistant, and real-time notifications.

A learning pet project showcasing async Python, SQLAlchemy 2.0, background jobs, WebSockets, and a full Docker-based stack.

## Features

- **Authentication** — email verification via SMTP, registration and login through JWT (python-jose + bcrypt)
- **User profiles** — username updates, password change, email change with confirmation
- **Timezones** — IANA timezone per user (e.g. `Europe/Moscow`), validated at registration
- **Events** — CRUD, filtering, pagination, participant limits, event history, location with coordinates
- **Maps** — interactive map picker on the frontend (Geoapify + Leaflet) for event venues
- **Registrations** — join and leave events with validation
- **Messaging** — 1-on-1 chats: conversations, history, read status, unread counter, clear/delete
- **Realtime** — WebSocket updates for new messages and unread counts (Redis pub/sub)
- **AI assistant** — personal chat powered by Ollama with conversation memory; can create events directly in chat
- **Notifications** — background processing via ARQ worker and Redis (including new messages)
- **Caching** — Redis for frequently accessed data (events, conversations, unread counts)
- **Frontend** — Nuxt 4 SPA with Pinia and i18n (`/chats` page for user and AI chat)
- **Testing** — pytest + httpx for core API logic
- **Infrastructure** — Docker Compose (PostgreSQL, Redis, Nginx, Ollama)

### Timezones

- Each user stores an IANA timezone (`UTC` by default) in their profile.
- Timezones are validated with Python `zoneinfo` (e.g. `Asia/Tokyo`, `America/New_York`).
- All datetimes in the database are stored in UTC (`DateTime(timezone=True)`); the user's timezone is available for display on the client.

### Messaging & Realtime

- Private conversations between two registered users.
- Cursor-based message pagination, soft delete, clear history, delete conversation.
- Read/unread tracking with a global unread counter.
- New messages trigger in-app notifications, Redis cache invalidation, and WebSocket events (`message.new`, `unread.updated`).
- Clients connect via `WebSocket /realtime/ws?token=<JWT>`.

### AI Assistant

- Optional assistant for authenticated users, backed by [Ollama](https://ollama.com/).
- Chat history is persisted per user; context is sent to the model on each request.
- Can be disabled with `AI_ENABLED=false` when Ollama is not needed.
- Default model: `qwen2.5:3b` (configurable via `AI_MODEL`).

**Creating events via AI chat**

1. Open the AI widget on any events page (robot icon in the bottom-right corner).
2. Ask to create an event — e.g. *"Create an event"* or *"Создай событие"*.
3. The assistant collects missing fields in conversation: title, date/time (in the user's timezone), optional description, location, and max participants.
4. When enough data is collected, the API returns a `draft` with `ready_to_create: true` and a **Confirm** button appears in the chat.
5. After confirmation, the event is created via `POST /ai/events/create` and appears in **My Events**.

The assistant also answers UI questions (*"how to create an event"*, *"куда нажать"*) with step-by-step navigation hints, without starting the in-chat creation flow.

### Event Locations

- Events support a text `location` plus optional `latitude` / `longitude`.
- The frontend uses Geoapify for geocoding, autocomplete, and map tiles.
- Requires `NUXT_PUBLIC_GEOAPIFY_API_KEY` for map features in the web UI.

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3.14, FastAPI, Pydantic v2 |
| ORM & DB | SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic |
| Auth | JWT (python-jose), bcrypt |
| Cache & Jobs | Redis, ARQ |
| AI | Ollama, httpx |
| Realtime | WebSockets, Redis pub/sub |
| Maps | Geoapify, Leaflet (frontend) |
| Email (dev) | MailHog |
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

4. **Pull the AI model (first run only, if AI is enabled):**

   ```bash
   make ollama-pull
   ```

5. **Verify everything is running:**

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
| MailHog (dev) | http://localhost:8025 |
| Ollama (dev) | http://localhost:11434 |
| PostgreSQL | localhost:`POSTGRES_PORT` (default: 5436) |

### Useful Commands (Makefile)

```bash
make help          # list all commands
make down          # stop containers
make logs          # follow API logs
make migrate       # apply migrations
make migration msg="description"  # create a migration
make test-docker   # run pytest inside the container
make ollama-pull   # pull AI model into Ollama
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
| `AI_ENABLED` | Enable AI assistant | `true` |
| `AI_MODEL` | Ollama model name | `qwen2.5:3b` |
| `AI_TIMEOUT_SECONDS` | AI request timeout | `120` |
| `SMTP_HOST` | SMTP server (MailHog in dev) | `mailhog` |
| `SMTP_PORT` | SMTP port | `1025` |
| `SMTP_FROM_EMAIL` | Sender email address | `noreply@eventhub.local` |
| `PGADMIN_DEFAULT_EMAIL` | pgAdmin email (dev) | `admin@local.dev` |
| `PGADMIN_DEFAULT_PASSWORD` | pgAdmin password (dev) | `admin` |
| `NUXT_PUBLIC_API_BASE` | API base URL for the frontend | `http://localhost/api` |
| `NUXT_PUBLIC_GEOAPIFY_API_KEY` | Geoapify API key for maps | `your-key` |

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
| POST | `/events/` | Create an event (supports `location`, `latitude`, `longitude`) |
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
| GET | `/conversations/available-users` | Users available to start a chat with |
| POST | `/conversations/` | Start or get a conversation with another user |
| GET | `/conversations/unread-count` | Total unread messages |
| GET | `/conversations/{id}/messages` | Message history (cursor pagination) |
| POST | `/conversations/{id}/messages` | Send a message |
| POST | `/conversations/{id}/read` | Mark conversation as read |
| POST | `/conversations/{id}/clear` | Clear conversation history |
| DELETE | `/conversations/{id}` | Delete conversation |
| DELETE | `/conversations/{id}/messages/{message_id}` | Soft-delete own message |

### AI

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ai/health` | AI service status (`enabled`, `available`, `model`) |
| GET | `/ai/messages` | User's AI chat history |
| POST | `/ai/chat` | Send a message (may return `draft` + `ready_to_create`) |
| POST | `/ai/events/create` | Create an event from a confirmed draft |
| DELETE | `/ai/messages` | Clear AI chat history |

### Realtime

| Protocol | Path | Description |
|----------|------|-------------|
| WebSocket | `/realtime/ws?token=<JWT>` | Live updates: `message.new`, `unread.updated` |

### Other

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications/my` | User notifications |
| GET | `/health` | Health check |

## Project Structure

```
event_hub/
├── api/           # FastAPI backend, migrations, tests, ARQ worker, AI & realtime
├── web/           # Nuxt frontend (events, chats, map, AI widget)
├── nginx/         # Reverse proxy (API + Web + WebSocket upgrade)
├── docker/        # PostgreSQL init scripts
├── docker-compose.yml
├── docker-compose.dev.yml
└── Makefile
```
