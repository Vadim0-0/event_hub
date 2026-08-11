from uuid import UUID
from ..worker.enqueue import enqueue_job

class notify:
  class auth:
    @staticmethod
    async def verification_code(user_id: int, email: str, code: str):
      await enqueue_job("notify_verification_code", user_id, email, code)


    @staticmethod
    async def welcome(user_id: int, email: str, username: str):
      await enqueue_job("notify_welcome", user_id, email, username)


    @staticmethod
    async def login(user_id: int, email: str, username: str):
      await enqueue_job("notify_login", user_id, email, username)


  class profile:
    @staticmethod
    async def updated(user_id: int, email: str, username: str, changes: list[dict]):
      await enqueue_job("notify_profile_updated", user_id, email, username, changes)


    @staticmethod
    async def password_changed(user_id: int, email: str, username: str):
      await enqueue_job("notify_password_changed", user_id, email, username)


    @staticmethod
    async def email_changed(user_id: int, email: str, username: str, old_email: str):
      await enqueue_job("notify_email_changed", user_id, email, username, old_email)
    
    
    @staticmethod
    async def email_change_code(user_id: int, new_email: str, code: str):
      await enqueue_job("notify_email_change_code", user_id, new_email, code)


  class events:
    @staticmethod
    async def created(event_id: UUID, creator_email: str):
      await enqueue_job("notify_event_created", event_id, creator_email)


    @staticmethod
    async def updated(event_id: UUID, changes: list[dict]):
      await enqueue_job("notify_event_updated", event_id, changes)


    @staticmethod
    async def deleted(event_id: UUID, title: str, participant_emails: list[str]):
      await enqueue_job("notify_event_deleted", event_id, title, participant_emails)


  class registrations:
    @staticmethod
    async def joined(event_id: UUID, participant_email: str):
      await enqueue_job("notify_registration_confirmed", event_id, participant_email)
      await enqueue_job("notify_new_participant", event_id, participant_email)


    @staticmethod
    async def left(event_id: UUID, participant_email: str):
      await enqueue_job("notify_leave_confirmed", event_id, participant_email)
      await enqueue_job("notify_participant_left", event_id, participant_email)
    

    @staticmethod
    async def removed(event_id: UUID, participant_email: str):
      await enqueue_job("notify_participant_removed", event_id, participant_email)

  
  class messages:
    @staticmethod
    async def received(
      conversation_id: UUID,
      recipient_id: int,
      sender_username: str,
      body: str,
    ):
      await enqueue_job(
        "notify_new_message",
        conversation_id,
        recipient_id,
        sender_username,
        body,
      )