from app.user import repository

async def user_sign_up(user_id: str, is_admin: int):
    return await repository.user_sign_up(user_id, is_admin)


async def get_user_by_user_id(user_id: str):
    return await repository.get_user_by_user_id(user_id)