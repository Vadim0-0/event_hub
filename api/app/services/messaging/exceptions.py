class ConversationNotFoundError(Exception):
  pass


class ConversationAccessDeniedError(Exception):
  pass


class CannotMessageSelfError(Exception):
  pass


class RecipientNotFoundError(Exception):
  pass


class MessageNotFoundError(Exception):
  pass


class EmptyMessageBodyError(Exception):
  pass


class IntegrityError(Exception):
  pass


class ConversationCreationError(Exception):
  pass


class MessageDeleteForEveryoneDeniedError(Exception):
  pass