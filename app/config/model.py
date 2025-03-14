from sqlalchemy import BigInteger, ForeignKey, Integer, TEXT, BOOLEAN, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(TEXT, nullable=False, doc='라벨러 ID')
    is_admin: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, doc='관리자 여부')


class Quiz(Base):
    __tablename__ = "quiz"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, doc='퀴즈 이름')
    q_count: Mapped[int] = mapped_column(Integer, nullable=False, doc='해당 퀴즈의 총 문제 수')
    s_count: Mapped[int] = mapped_column(Integer, nullable=False, doc='문제 출제 수 (관리자가 설정)')
    p_count: Mapped[int] = mapped_column(Integer, nullable=False, doc='한 목록에 보여질 문제 수 (관리자가 설정)')
    is_random: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False, doc='랜덤 출제 여부')


class Question(Base):
    __tablename__ = "question"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("pro.quiz.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False, doc='문제 정보 = 문항')
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, doc='순서')

    quiz = relationship("Quiz", backref=backref("question"))


class Selection(Base):
    __tablename__ = "selection"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("pro.question.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False, doc='보기 정보')
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, doc='순서')
    is_correct: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False, doc='정답 여부')

    question = relationship("Question", backref=backref("selection"))


# 문제 풀이 로그 관련 테이블
class QuestionLog(Base):
    __tablename__ = "question_log"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("pro.user.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("pro.question.id"), nullable=False, index=True)
    user_answer: Mapped[str] = mapped_column(TEXT, nullable=False, doc='유저가 선택한 정답')
    is_correct: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False, doc='정답 여부')

    user = relationship("User", backref=backref("question_log"))
    question = relationship("Question", backref=backref("question_log"))


class QuizVersion(Base):
    __tablename__ = "quiz_version"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("pro.quiz.id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    question_ids: Mapped[str] = mapped_column(TEXT, nullable=False, doc='문제 순서')
    selection_info: Mapped[str] = mapped_column(TEXT, nullable=False, doc='문제 별 보기 순서')

    quiz = relationship("Quiz", backref=backref("quiz_version"))


class PreSave(Base):
    __tablename__ = "pre_save"
    __table_args__ = {'schema': 'pro'}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("pro.quiz.id"), nullable=False, index=True)
    quiz_version_id: Mapped[int] = mapped_column(ForeignKey("pro.quiz_version.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("pro.user.id"), nullable=False, index=True)
    answer: Mapped[str] = mapped_column(TEXT, nullable=False, doc='문제 순서')
