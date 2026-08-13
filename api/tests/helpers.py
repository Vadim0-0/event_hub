import pytest


VERIFY_URL = "/auth/verify-email"
REGISTER_URL = "/auth/register"


async def register_and_verify(client, user_data: dict) -> dict:
  reg = await client.post(REGISTER_URL, json=user_data)
  assert reg.status_code == 201
  verify = await client.post(
    VERIFY_URL,
    json={"email": user_data["email"], "code": "123456"},
  )
  assert verify.status_code == 200
  return verify.json()


@pytest.fixture
def user_data_factory():
  """ factory for generating unique user data """
  counter = 0

  def _counter_user_data(username_prefix="Test User", timezone="UTC"):
    nonlocal counter
    counter += 1
    return {
      "username": f"{username_prefix}{counter}",
      "email": f"test{counter}@example.com",
      "password": "password123",
      "timezone": timezone,
    }
  
  return _counter_user_data
