"""Seed demo users and events for local development.

Usage (from repo root):
  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api python scripts/seed_demo_data.py

Or from api/ with env pointing at local Postgres/Redis:
  python scripts/seed_demo_data.py
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.database import AsyncSessionLocal  # noqa: E402
from app.models.ai_message import AiMessage  # noqa: F401, E402
from app.models.conversation import Conversation  # noqa: F401, E402
from app.models.conversation_read import ConversationRead  # noqa: F401, E402
from app.models.conversation_user_state import ConversationUserState  # noqa: F401, E402
from app.models.event import Event  # noqa: F401, E402
from app.models.message import Message  # noqa: F401, E402
from app.models.message_user_hide import MessageUserHide  # noqa: F401, E402
from app.models.notification import Notification  # noqa: F401, E402
from app.models.registration import EventRegistration  # noqa: F401, E402
from app.models.user import User  # noqa: F401, E402
from app.redis_client import close_redis, init_redis  # noqa: E402
from app.schemas.event import EventCreate  # noqa: E402
from app.schemas.user import UserRegister  # noqa: E402
from app.services.auth import services as auth_service  # noqa: E402
from app.services.auth.helpers import get_user_by_email  # noqa: E402
from app.services.events import services as events_service  # noqa: E402

PASSWORD = "password123"

DEMO_USERS = [
  {
    "username": "Alice Johnson",
    "email": "alice.demo@example.com",
    "timezone": "Europe/London",
    "events": [
      ("Morning Yoga Meetup", "Weekly yoga session in the park.", "Hyde Park, London", 51.5074, -0.1278, 20),
      ("Product Design Workshop", "Hands-on UX workshop for beginners.", "Shoreditch Hub", 51.5255, -0.0784, 15),
      ("Book Club: Sci-Fi Night", "Discussing classic and modern sci-fi.", "Central Library", 51.5155, -0.0922, 12),
      ("Thames Riverside Walk", "Easy 8 km walk along the river.", "Westminster Bridge", 51.5007, -0.1246, 25),
      ("Watercolour Painting Class", "Beginner-friendly outdoor sketching.", "Regent's Park", 51.5313, -0.1569, 10),
      ("Jazz in Camden", "Live jazz and networking evening.", "Camden Market Hall", 51.5416, -0.1466, 40),
    ],
  },
  {
    "username": "Bob Smith",
    "email": "bob.demo@example.com",
    "timezone": "America/New_York",
    "events": [
      ("Startup Pitch Night", "Five-minute pitches from local founders.", "Brooklyn Loft", 40.6782, -73.9442, 50),
      ("Python Study Group", "Async Python patterns and best practices.", "WeWork Manhattan", 40.7580, -73.9855, 10),
      ("Central Park Run", "Easy 5k group run.", "Central Park", 40.7812, -73.9665, 30),
      ("Photo Walk Downtown", "Street photography walk.", "Wall Street", 40.7075, -74.0113, 8),
      ("Chess in Bryant Park", "Casual chess games for all levels.", "Bryant Park", 40.7536, -73.9832, 16),
      ("Open Mic Comedy Night", "Stand-up and improv performances.", "East Village Bar", 40.7265, -73.9815, 35),
      ("Volunteer Food Drive", "Help pack meals for local shelters.", "Queens Community Center", 40.7282, -73.7949, 20),
    ],
  },
  {
    "username": "Carol Davis",
    "email": "carol.demo@example.com",
    "timezone": "Europe/Berlin",
    "events": [
      ("Berlin Tech Meetup", "Talks about event-driven architecture.", "Factory Berlin", 52.5320, 13.3849, 40),
      ("Coffee & Code", "Casual coworking morning.", "Mitte Café", 52.5200, 13.4050, 6),
      ("Hiking Trip Grunewald", "Half-day hike in the forest.", "Grunewald Forest", 52.4833, 13.2500, 15),
      ("Street Art Tour Kreuzberg", "Guided walk through murals and graffiti.", "Kottbusser Tor", 52.4990, 13.4180, 18),
      ("Sourdough Baking Workshop", "Learn to bake your first loaf.", "Prenzlauer Berg Kitchen", 52.5400, 13.4100, 8),
      ("Cycling Along Spree", "Relaxed group ride by the river.", "Treptower Park", 52.4880, 13.4690, 22),
    ],
  },
  {
    "username": "David Wilson",
    "email": "david.demo@example.com",
    "timezone": "Asia/Tokyo",
    "events": [
      ("Tokyo Ramen Tour", "Explore three ramen shops in Shinjuku.", "Shinjuku Station", 35.6896, 139.7006, 8),
      ("Language Exchange", "English/Japanese conversation practice.", "Shibuya Community Center", 35.6595, 139.7004, 20),
      ("Board Game Night", "Strategy and party games.", "Nakano Game Bar", 35.7074, 139.6638, 10),
      ("Morning Meditation", "Guided meditation session.", "Yoyogi Park", 35.6717, 139.6949, 25),
      ("Origami for Beginners", "Simple figures and paper crafts.", "Asakusa Culture Hall", 35.7148, 139.7967, 12),
      ("Akihabara Retro Gaming", "Visit classic arcades together.", "Akihabara", 35.7023, 139.7745, 14),
      ("Sumida River Night Walk", "Evening stroll with city views.", "Sumida Park", 35.7101, 139.8016, 30),
    ],
  },
  {
    "username": "Eva Martinez",
    "email": "eva.demo@example.com",
    "timezone": "Europe/Madrid",
    "events": [
      ("Flamenco Beginners Class", "Introduction to flamenco basics.", "La Latina Studio", 40.4110, -3.7120, 12),
      ("Tapas Tasting Evening", "Local tapas and wine pairing.", "Mercado San Miguel", 40.4154, -3.7074, 16),
      ("Retiro Park Picnic", "Bring snacks and meet new people.", "El Retiro Park", 40.4153, -3.6844, 30),
      ("Prado Museum Visit", "Guided tour of selected masterpieces.", "Museo del Prado", 40.4138, -3.6921, 15),
      ("Sunset at Temple of Debod", "Photography and relaxed hangout.", "Temple of Debod", 40.4240, -3.7179, 20),
      ("Spanish Conversation Club", "Practice Spanish with natives.", "Malasaña Café", 40.4260, -3.7030, 10),
    ],
  },
]


async def ensure_user(db, redis, spec: dict) -> User:
  existing = await get_user_by_email(db, spec["email"])

  if existing is not None and existing.is_email_verified:
    print(f"  user exists: {spec['email']}")
    return existing

  register_data = UserRegister(
    username=spec["username"],
    email=spec["email"],
    password=PASSWORD,
    timezone=spec["timezone"],
  )

  user, code = await auth_service.register_user(register_data, db, redis)
  user, _token = await auth_service.verify_email(spec["email"], code, db, redis)
  print(f"  user created: {spec['email']}")
  return user


async def ensure_events(db, user: User, events: list[tuple]) -> int:
  created = 0
  now = datetime.now(timezone.utc)

  for index, (title, description, location, lat, lng, max_participants) in enumerate(events, start=1):
    result = await db.execute(
      select(Event.id).where(
        Event.creator_id == user.id,
        Event.title == title,
      ),
    )
    if result.scalar_one_or_none() is not None:
      continue

    starts_at = now + timedelta(days=7 * index + user.id, hours=10 + index)

    await events_service.create_event(
      EventCreate(
        title=title,
        description=description,
        starts_at=starts_at,
        location=location,
        latitude=lat,
        longitude=lng,
        max_participants=max_participants,
      ),
      db,
      user.id,
    )
    created += 1
    print(f"    + event: {title}")

  return created


async def main() -> None:
  redis = await init_redis()
  total_users = 0
  total_events = 0

  try:
    async with AsyncSessionLocal() as db:
      print("Seeding demo users and events...\n")

      for spec in DEMO_USERS:
        print(spec["username"])
        user = await ensure_user(db, redis, spec)
        total_users += 1
        total_events += await ensure_events(db, user, spec["events"])
        print()

      print("Done.")
      print(f"Users processed: {total_users}")
      print(f"Events created: {total_events}")
      print(f"\nAll demo accounts use password: {PASSWORD}")
  finally:
    await close_redis()


if __name__ == "__main__":
  asyncio.run(main())
