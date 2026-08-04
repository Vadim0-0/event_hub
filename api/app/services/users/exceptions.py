class UserNotFoundError(Exception):
  pass


class UsernameAlreadyTakenError(Exception):
  pass 


class InvalidCurrentPasswordError(Exception):
  pass


class EmailAlreadyTakenError(Exception):
  pass 


class SameEmailError(Exception):
  pass


class InvalidEmailChangeCodeError(Exception):
  pass


class EmailChangeNotRequestedError(Exception):
  pass


class SamePasswordError(Exception):
  pass