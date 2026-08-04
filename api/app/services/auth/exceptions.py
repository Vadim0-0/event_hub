class EmailAlreadyRegisteredError(Exception):
  """Email is already taken"""
  pass


class UsernameAlreadyRegisteredError(Exception):
  pass


class UserNotFoundError(Exception):
  pass


class InvalidCredentialsError(Exception):
  """Wrong email or password"""
  pass


class EmailNotVerifiedError(Exception):
  pass


class InvalidVerificationCodeError(Exception):
  pass


class UserNotFoundForVerificationError(Exception):
  pass


class EmailAlreadyVerifiedError(Exception):
  pass