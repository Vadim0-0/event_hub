from . import prompts


def build_ollama_messages(history: list[dict], user_message: str) -> list[dict]:
  messages = [{"role": "system", "content": prompts.SYSTEM_PROMPT}]

  for item in history:
    messages.append({
      "role": item["role"],
      "content": item["content"],
    })

  messages.append({"role": "user", "content": user_message})
  return messages


def history_from_db_rows(rows) -> list[dict]:
  return [{"role": row.role, "content": row.content} for row in rows]