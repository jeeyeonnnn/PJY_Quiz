from pydantic import BaseModel

class SignUp(BaseModel):
    user_id: str
    is_admin: bool

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "jeeyeon",
                "is_admin": False
            }
        }


class SignIn(BaseModel):
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "jeeyeon"
            }
        }