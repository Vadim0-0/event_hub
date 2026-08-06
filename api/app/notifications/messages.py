from .types import ChangedField


# Auth
def verification_code_message(code: str) -> tuple[str, str]:
  return (
    "Event Hub — verification code",
    f"Your verification code: {code}\n\nIt expires in 15 minutes.",
  )

def welcome_message(username: str) -> tuple[str, str]:
  return (
    "Welcome to Event Hub",
    f"Hi, {username}! Your email is verified. Welcome aboard.",
  )


def login_message(username: str) -> tuple[str, str]:
  return (
    "New login to Event Hub",
    f"Hi, {username}. You successfully logged in.",
  )


# User
def email_change_code_message(code: str) -> tuple[str, str]:
  return (
    "Event Hub — confirm email change",
    f"Your confirmation code: {code}\n\nIf you did not request this, ignore this email.",
  )


def password_changed_message(username: str) -> tuple[str, str]:
  return (
    "Password changed",
    f"Hi, {username}. Your password was changed successfully.",
  )


def email_changed_message(username: str, old_email: str, new_email: str) -> tuple[str, str]:
  return (
    "Email changed",
    f"Hi, {username}. Your email was changed from {old_email} to {new_email}.",
  )


def profile_updated_message(username: str, changes: list[ChangedField]) -> tuple[str, str]:
  lines = "\n".join(
    f"- {c.label}: {c.old or '—'} → {c.new or '—'}"
    for c in changes
  )
  return ("Profile updated", f"Hi, {username}. Your profile was updated:\n\n{lines}")


# Events
def event_created_message(title: str, starts_at: str) -> tuple[str, str]:
  return (
    f"Event created: {title}",
    f"Your event '{title}' starts at {starts_at}.",
  )


def event_updated_message(title: str, changes: list[ChangedField] | None = None) -> tuple[str, str]:
  if changes:
    lines = "\n".join(f"- {c.label}: {c.old} → {c.new}" for c in changes)
    body = f"The event '{title}' was updated:\n\n{lines}\n\nCheck the app for details."
  else:
    body = f"The event '{title}' was updated. Check the app for details."
  return (f"Event updated: {title}", body)


def event_deleted_message(title: str) -> tuple[str, str]:
  return (f"Event deleted: {title}", f"The event '{title}' was cancelled.")


# Registrations
def registration_confirmed_message(title: str, starts_at: str) -> tuple[str, str]:
  return (
    f"Join Event: {title}",
    f"You are registered for '{title}' starting at {starts_at}.",
  )


def new_participant_message(event_title: str, participant_email: str) -> tuple[str, str]:
  return (
    f"A new member has joined: {participant_email}",
    f"Participant {participant_email} joined '{event_title}'.",
  )


def leave_confirmed_message(title: str) -> tuple[str, str]:
  return (f"Leave Event: {title}", 
          f"You left the event '{title}'.")

  
def participant_left_message(title: str, participant_email: str) -> tuple[str, str]:
  return (
    f"A member has left: {participant_email}",
    f"Participant {participant_email} left '{title}'.",
  )


def participant_removed_message(event_title: str) -> tuple[str, str]:
  return (
    f"Removed from event: {event_title}",
    f"You were removed from the event '{event_title}' by the organizer.",
  )


EVENT_FIELD_LABELS = {
  "title": "Title",
  "description": "Description",
  "starts_at": "Start time",
  "max_participants": "Max participants",
}

PROFILE_FIELD_LABELS = {
  "username": "Username",
  "email": "Email",
}