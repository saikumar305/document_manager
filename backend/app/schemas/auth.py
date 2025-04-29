from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str = Field(..., alias="refreshToken")
