from app.user import repository

def user_sign_up(user_id: str, is_admin: int):
    return repository.user_sign_up(user_id, is_admin)


def get_user_by_user_id(user_id: str):
    return repository.get_user_by_user_id(user_id)