import re

from . import prompts
from .import intent


def detect_reply_language(user_message: str, history: list[dict] | None = None) -> str:
  parts: list[str] = []
  if user_message.strip():
    parts.append(user_message)
  if history:
    parts.extend(item["content"] for item in history if item["role"] == "user")
  combined = " ".join(parts[-5:])
  return "Russian" if re.search(r"[а-яёА-ЯЁ]", combined) else "English"


def language_instruction(language: str) -> str:
  if language == "Russian":
    return (
      "Language rule (mandatory): Reply ONLY in Russian. "
      "All user-facing text must be in Russian, even if these instructions are in English."
    )
  return (
    "Language rule (mandatory): Reply ONLY in English. "
    "All user-facing text must be in English."
  )


def build_ollama_messages(
  history: list[dict],
  user_message: str,
  user_timezone: str = "UTC",
) -> list[dict]:
  language = detect_reply_language(user_message, history)
  system_content = (
    f"{prompts.build_system_prompt(user_timezone)}\n\n"
    f"{language_instruction(language)}"
  )
  messages = [{"role": "system", "content": system_content}]

  for item in history:
    messages.append({
      "role": item["role"],
      "content": item["content"],
    })

  messages.append({"role": "user", "content": user_message})
  return messages


def history_from_db_rows(rows) -> list[dict]:
  return [{"role": row.role, "content": row.content} for row in rows]


def build_event_draft_context(history: list[dict], user_message: str) -> str:
  lines = []
  for item in history[-10:]:
    role = "User" if item["role"] == "user" else "Assistant"
    lines.append(f"{role}: {item['content']}")
  lines.append(f"User: {user_message}")
  return "\n".join(lines)


def is_event_creation_context(user_message: str, history: list[dict]) -> bool:
  text = user_message.lower()

  if any(hint in text for hint in intent.HOW_TO_CREATE_HINTS):
    return False

  if any(hint in text for hint in intent.EVENT_CREATE_HINTS):
    return True

  for item in reversed(history[-6:]):
    if item["role"] != "assistant":
      continue
    content = item["content"].lower()
    if any(hint in content for hint in intent.EVENT_FOLLOWUP_HINTS):
      return True

  return False