from fastapi import APIRouter, status

from app.user.dto.request import SignUp, SignIn
from app.user import service
from app.util.auth_handler import auth
from app.util.response_handler import res

router = APIRouter(tags=['☑️ USER'])

@router.post(
    path="/sign-up",
    description='## ✔️️ [회원 가입] \n'
                '''
                ## Request Detail ##
                - user_id : 유저 ID
                - is_admin : 관리자 여부 (True = 관리자 / False = 일반 사용자)\n
                ''',
    responses={
        status.HTTP_201_CREATED: {
            "description": "회원 가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "success"
                    }
                }
            }
        },
        status.HTTP_409_CONFLICT: {
            "description": "중복된 아이디로 회원가입을 요청하는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "이미 사용 중인 아이디입니다."
                    }
                }
            }
        }
    }
)
async def signup(
        request: SignUp
):
    if await service.user_sign_up(request.user_id, request.is_admin):
        return res.post_success()
    return res.post_exception(status.HTTP_409_CONFLICT, '이미 사용 중인 아이디입니다.')


@router.post(
    path='/sign-in',
    description='## ✔️️ [로그인] \n'
                '''
                ## Request Detail ##
                - user_id : 유저 ID
                ''',
    responses={
        status.HTTP_201_CREATED: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "token": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAi..."
                    }
                }
            }
        },
        status.HTTP_409_CONFLICT: {
            "description": "해당 아이디가 존재하지 않는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "존재하지 않은 아이디입니다."
                    }
                }
            }
        }
    }
)
async def signin(
        request: SignIn
):
    user = await service.get_user_by_user_id(request.user_id)

    if not user:  # 유저 존재 X
        return res.post_exception(status.HTTP_409_CONFLICT, '존재하지 않은 아이디입니다.')

    return res.post_custom('token', f'Bearer {await auth.encode_token(user.id)}')