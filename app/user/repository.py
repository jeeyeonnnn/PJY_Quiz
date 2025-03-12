from app.config.database import database
from app.config.model import User


def user_sign_up(user_id, is_admin):
    with database.session_factory() as db:
        # 아이디 중복 체크
        if (
                db.query(User)
                .filter(User.user_id == user_id)
                .count() != 0
        ):
            return False

        db.add(User(
            user_id=user_id,
            is_admin=is_admin
        ))
        db.commit()
        return True


def get_user_by_user_id(user_id):
    with database.session_factory() as db:
        # 아이디 존재 여부 확인
        if (
                db.query(User)
                .filter(User.user_id == user_id)
                .count() != 1
        ):
            return False

        return db.query(User).filter(User.user_id == user_id).one()
