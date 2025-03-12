from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.util.preloaded import orm

from app.config.setting import setting


class Database:
    def __init__(self):
        self.engine = create_engine(setting.get_db_url)
        self.session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )

    @contextmanager
    def session(self):
        session: Session = self.session_factory()
        try:
            yield session
        except Exception as e:
            print('Session rollback because of exception: %s', e)
            session.rollback()
        finally:
            session.close()


database = Database()