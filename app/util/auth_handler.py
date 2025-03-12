from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.database import database
from app.config.model import User
from app.config.setting import setting

# JWT 인증 방식을 설정 (Swagger에서 Authorize 버튼 활성화됨)
security = HTTPBearer()

class AuthHandler:
    @staticmethod
    def encode_token(user_idx):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=10),
            'iat': datetime.utcnow(),
            'sub': user_idx
        }
        token = jwt.encode(payload, setting.JWT_SECRET, algorithm=setting.JWT_ALGORITHM)
        return token

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, setting.JWT_SECRET, algorithms=setting.JWT_ALGORITHM)
            return self.get_user(payload['sub'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='시간이 만료되었습니다. 재로그인 해주세요!')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='비정상적인 접근입니다. 재로그인 해주세요!')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    @staticmethod
    async def get_user(user_idx):
        async with database.session_factory() as db:
            return await db.query(User).filter(User.id == user_idx).one()

auth = AuthHandler()
