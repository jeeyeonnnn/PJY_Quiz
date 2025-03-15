from sqlalchemy import select, func

from app.config.database import database
from app.config.model import User


async def user_sign_up(user_id, is_admin):
    user_stmt = (
        select(func.count(User.id))
        .where(User.user_id == user_id)
    )

    async with database.session_factory() as db:
        # 아이디 중복 체크
        result = await db.execute(user_stmt)
        if result.scalar() != 0:
            return False

        db.add(User(
            user_id=user_id,
            is_admin=is_admin
        ))
        await db.commit()
        return True


async def get_user_by_user_id(user_id):
    user_stmt = (
        select(User)
        .where(User.user_id == user_id)
    )

    async with database.session_factory() as db:
        # 아이디 존재 여부 확인
        result = await db.execute(user_stmt)  # 결과를 비동기적으로 기다림
        user = result.scalar_one_or_none()  # 비동기적으로 첫 번째 결과를 확인

        return False if user is None else user