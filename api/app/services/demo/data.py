from __future__ import annotations

import re
import random

NAMES = [
  "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Martinez",
  "Frank Miller", "Grace Lee", "Henry Brown", "Ivy Chen", "Jack Taylor",
  "Kate Anderson", "Leo Garcia", "Mia Rodriguez", "Noah Kim", "Olivia White",
  "Paul Martin", "Quinn Foster", "Rachel Green", "Samuel Clark", "Tina Lopez",
]

EMAIL_DOMAINS = [
  "gmail.event-hub.dev",
  "outlook.event-hub.dev",
  "yahoo.event-hub.dev",
  "mail.event-hub.dev",
]

TIMEZONES = [
  "Europe/London", "Europe/Berlin", "Europe/Madrid", "Europe/Paris",
  "America/New_York", "America/Chicago", "America/Los_Angeles",
  "Asia/Tokyo", "Asia/Seoul", "Asia/Singapore", "Australia/Sydney",
]

LOCATIONS: list[tuple[str, float, float]] = [
  ("Hyde Park, London", 51.5074, -0.1278),
  ("Central Park, New York", 40.7812, -73.9665),
  ("Brandenburg Gate, Berlin", 52.5163, 13.3777),
  ("Retiro Park, Madrid", 40.4153, -3.6844),
  ("Shibuya Crossing, Tokyo", 35.6595, 139.7004),
  ("Eiffel Tower, Paris", 48.8584, 2.2945),
  ("Opera House, Sydney", -33.8568, 151.2153),
  ("Millennium Park, Chicago", 41.8826, -87.6226),
]

EVENT_TITLES = [
  "Morning Yoga Meetup", "Book Club Night", "Tech Talk & Coffee",
  "City Photo Walk", "Board Game Evening", "Running Group 5K",
  "Language Exchange", "Startup Pitch Night", "Cooking Workshop",
  "Hiking Adventure", "Live Music Jam", "Volunteer Cleanup Day",
  "Chess in the Park", "Design Sprint Meetup", "Wine Tasting Evening",
]

DESCRIPTIONS = [
  "Casual meetup for everyone — beginners welcome!",
  "Bring friends and meet new people in the city.",
  "Small group, friendly atmosphere, no experience needed.",
  "Let's explore, learn something new, and have fun together.",
  "Open to all skill levels. See you there!",
]


def _slug(text: str) -> str:
  text = text.lower().strip()
  text = re.sub(r"[^a-z0-9]+", ".", text)
  return text.strip(".")


def random_demo_domain() -> str:
  return random.choice(EMAIL_DOMAINS)


def random_email_from_name(full_name: str, domain: str) -> str:
  parts = full_name.lower().split()
  first = re.sub(r"[^a-z]", "", parts[0]) if parts else "user"
  last = re.sub(r"[^a-z]", "", parts[-1]) if len(parts) > 1 else "demo"
  patterns = [
    f"{first}.{last}",
    f"{first}{last}",
    f"{first}.{last}{random.randint(1, 99)}",
    f"{first[0]}.{last}",
    f"{first}_{last}{random.randint(90, 99)}",
  ]
  local = random.choice(patterns)
  return f"{local}@{domain}"


def random_demo_email(full_name: str) -> str:
  return random_email_from_name(full_name, random_demo_domain())


def is_demo_email(email: str) -> bool:
  if "@" not in email:
    return False
  domain = email.rsplit("@", 1)[1].lower()
  return domain in EMAIL_DOMAINS


def random_name() -> str:
  return random.choice(NAMES)


def random_timezone() -> str:
  return random.choice(TIMEZONES)


def random_location() -> tuple[str, float, float]:
  return random.choice(LOCATIONS)


def random_event_title() -> str:
  return random.choice(EVENT_TITLES)


def random_description() -> str:
  return random.choice(DESCRIPTIONS)