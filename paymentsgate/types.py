from pydantic import BaseModel

from .tokens import AccessToken, RefreshToken

class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  expires_in: int
  