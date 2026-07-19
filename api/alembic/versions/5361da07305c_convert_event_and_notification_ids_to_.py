"""convert_event_and_notification_ids_to_uuid

Revision ID: 5361da07305c
Revises: 136a937e6b7b
Create Date: 2026-07-19 06:45:32.197840

"""
from typing import Sequence, Union

from alembic import op


revision: str = "5361da07305c"
down_revision: Union[str, Sequence[str], None] = "136a937e6b7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _int_to_uuid(column: str) -> str:
  return f"""
    ('00000000-0000-0000-0000-' || lpad({column}::text, 12, '0'))::uuid
  """


def upgrade() -> None:
  op.drop_constraint(
    "event_registrations_event_id_fkey",
    "event_registrations",
    type_="foreignkey",
  )
  op.drop_constraint(
    "notifications_event_id_fkey",
    "notifications",
    type_="foreignkey",
  )

  op.execute("ALTER TABLE events ALTER COLUMN id DROP DEFAULT")
  op.execute("DROP SEQUENCE IF EXISTS events_id_seq")
  op.execute(
    f"ALTER TABLE events ALTER COLUMN id TYPE UUID USING {_int_to_uuid('id')}"
  )

  op.execute(
    "ALTER TABLE event_registrations "
    f"ALTER COLUMN event_id TYPE UUID USING {_int_to_uuid('event_id')}"
  )

  op.execute("ALTER TABLE notifications ALTER COLUMN id DROP DEFAULT")
  op.execute("DROP SEQUENCE IF EXISTS notifications_id_seq")
  op.execute(
    f"ALTER TABLE notifications ALTER COLUMN id TYPE UUID USING {_int_to_uuid('id')}"
  )
  op.execute(
    """
    ALTER TABLE notifications
    ALTER COLUMN event_id TYPE UUID
    USING (
      CASE
        WHEN event_id IS NULL THEN NULL
        ELSE ('00000000-0000-0000-0000-' || lpad(event_id::text, 12, '0'))::uuid
      END
    )
    """
  )

  op.create_foreign_key(
    "event_registrations_event_id_fkey",
    "event_registrations",
    "events",
    ["event_id"],
    ["id"],
    ondelete="CASCADE",
  )
  op.create_foreign_key(
    "notifications_event_id_fkey",
    "notifications",
    "events",
    ["event_id"],
    ["id"],
    ondelete="SET NULL",
  )


def downgrade() -> None:
  raise NotImplementedError("Downgrade is not supported for UUID migration")
