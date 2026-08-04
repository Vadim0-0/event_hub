class EventCreatorCannotJoinError(Exception):
  """The event creator cannot register"""
  pass


class EventAlreadyStartedError(Exception):
  """The event has already begun"""
  pass


class EventNotFoundError(Exception):
  """Event not found"""
  pass


class AlreadyRegisteredError(Exception):
  """The user is already registered"""
  pass


class EventFullError(Exception):
  """There are no vacancies"""
  pass


class NotRegisteredError(Exception):
  """User is not registered for this event"""
  pass