from pydantic import BaseModel, EmailStr


class Recipient(BaseModel):
    name: str
    email: EmailStr
