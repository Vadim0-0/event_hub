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