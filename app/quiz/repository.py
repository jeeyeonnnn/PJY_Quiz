import json
from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.sql import func, select, case, or_
from sqlalchemy.types import JSON

from app.config.database import database
from app.config.model import Quiz, Question, Selection, User, QuestionLog, QuizVersion, PreSave
from app.quiz.dto.request import QuestionInfoRequest


def save_new_quiz(
        name: str, select_count: int, pagination_count:int, is_random: bool, questions: List[QuestionInfoRequest]
):
    # 문제가 존재하지 않은 경우
    if len(questions) == 0:
        return -1

    # 출제할 문제 수가 총 문제 수보다 작은 경우
    if len(questions) < select_count:
        return -2


    with database.session_factory() as db:
        new_quiz = Quiz(
            name=name,
            q_count=len(questions),
            s_count=select_count,
            p_count=pagination_count,
            is_random=is_random
        )

        db.add(new_quiz)
        db.flush()

        for question_idx in range(len(questions)):
            q_name, selections = questions[question_idx].name, questions[question_idx].selections

            new_question = Question(
                quiz_id=new_quiz.id,
                name=q_name,
                sequence=question_idx+1
            )
            db.add(new_question)
            db.flush()

            # 보기가 2개 미만인 경우
            if len(selections) < 2:
                return -3

            is_exist_answer = False
            for selection_idx in range(len(selections)):
                s_name, is_correct = selections[selection_idx].name, selections[selection_idx].is_correct

                db.add(Selection(
                    question_id=new_question.id,
                    name=s_name,
                    sequence=selection_idx+1,
                    is_correct=is_correct
                ))

                is_exist_answer = True if is_correct else is_exist_answer

            # 정답이 존재하지 않은 경우
            if not is_exist_answer:
                return -4

        db.commit()
        return new_quiz.id


def get_all_quiz_by_auth_and_limit(limit, page, user_idx, is_admin):
    quiz_stmt = (
        select(
            Quiz.id.label("id"),
            Quiz.name.label("name"),
            Quiz.s_count.label("question_count"),
            func.count(Question.id.distinct()).label("total_question_count"),
            Quiz.p_count.label("pagination_count"),
            Quiz.is_random.label("is_random"),

            # 관리자인 경우 null / 퀴즈를 안 푼 경우 0 / 푼 경우 1 / 임시 저장 2
            case(
                (is_admin == 1, None),
                (
                    func.exists(
                        select(1).select_from(QuestionLog)
                        .join(Question, QuestionLog.question_id == Question.id)
                        .where(
                            QuestionLog.user_id == user_idx,
                            QuestionLog.question_id == Question.id
                        ).scalar_subquery()
                    ),
                    1  # QuestionLog에 존재 == 퀴즈를 푼 적이 있음
                ),
                else_=0  # 그 외 상태 0
            ).label("status")
        )
        .select_from(Question)
        .join(Quiz, Question.quiz_id == Quiz.id)
        .group_by(Quiz.id)
        .offset((page-1) * limit)
        .limit(limit)
    )

    with database.session_factory() as db:
        total_quiz_count = db.execute(
            select(func.count(Quiz.id))
        ).scalar()
        return total_quiz_count, db.execute(quiz_stmt).fetchall()


def get_quiz_info_by_id_and_user(quiz_id: int):
    questions_stmt = (
        select(
            Question.id.label("id"),
            Question.name.label("name")
        )
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.sequence)
    )

    with database.session_factory() as db:
        return db.execute(questions_stmt).fetchall()


def get_quiz_info_by_id(quiz_id, user_idx, is_admin):
    quiz_stmt = (
        select(
            Quiz.name,
            func.count(Question.id),
            Quiz.s_count,
            Quiz.p_count,
            Quiz.is_random,
            # 관리자인 경우 null / 퀴즈를 안 푼 경우 0 / 푼 경우 1 / 임시 저장 2
            case(
                (is_admin == True, None),
                (
                    func.exists(
                        select(1).select_from(QuestionLog)
                        .join(Question, QuestionLog.question_id == Question.id)
                        .where(
                            QuestionLog.user_id == user_idx,
                            QuestionLog.question_id == Question.id
                        ).scalar_subquery()
                    ),
                    1  # QuestionLog에 존재 == 퀴즈를 푼 적이 있음
                ),
                else_=0  # 그 외 상태 0
            ).label("status"),
            (
                select(
                    func.count(QuestionLog.id)
                ).select_from(QuestionLog)
                .join(Question, QuestionLog.question_id == Question.id)
                .where(
                    Question.quiz_id == quiz_id,
                    QuestionLog.user_id == user_idx,
                    QuestionLog.is_correct == True
                ).scalar_subquery()
            ).label("correct_question_count")
        ).select_from(Question)
        .join(Quiz, Question.quiz_id == Quiz.id)
        .where(Quiz.id == quiz_id)
        .group_by(Quiz.id)
    )

    with database.session_factory() as db:
        return db.execute(quiz_stmt).fetchone()


def get_selections_by_question_id_and_is_random(question_id, is_random):
    stmt = (
        select(
            Selection.id.label("id"),
            Selection.name.label("name"),
            Selection.is_correct.label("is_correct")
        )
        .where(Selection.question_id == question_id)
        .order_by(Selection.sequence)
    )

    with database.session_factory() as db:
        return db.execute(stmt).fetchall()


def get_quiz_is_random_and_question_ids_by_quiz_id(quiz_id: int):
    quiz_stmt = (
        select(Quiz.is_random, Quiz.s_count)
        .select_from(Quiz)
        .where(Quiz.id == quiz_id)
    )

    question_stmt = (
        select(Question.id)
        .select_from(Question)
        .where(Question.quiz_id == quiz_id)
    )

    with database.session_factory() as db:
        is_random, s_count = db.execute(quiz_stmt).fetchone()
        question_ids = db.execute(question_stmt).scalars().all()

    return is_random, s_count, question_ids


def get_selection_ids_by_question_id(question_id: int):
    stmt = (
        select(Selection.id)
        .where(Selection.question_id == question_id)
    )

    with database.session_factory() as db:
        return db.execute(stmt).scalars().all()


def add_quiz_version(quiz_id, version_num, question_info, selection_info):
    with database.session_factory() as db:
        db.add(QuizVersion(
            quiz_id=quiz_id,
            version=version_num,
            question_ids=json.dumps(question_info),
            selection_info=json.dumps(selection_info)
        ))
        db.commit()


def get_max_quiz_version_by_quiz_id(quiz_id):
    with database.session_factory() as db:
        return db.execute(
            select(func.max(QuizVersion.version))
            .where(QuizVersion.quiz_id == quiz_id)
        ).scalar()


def update_quiz_version_by_user(user_idx, quiz_id, version_num):
    stmt = (
        select(QuizVersion.id)
        .where(
            QuizVersion.quiz_id == quiz_id,
            QuizVersion.version == version_num
        )
    )

    with database.session_factory() as db:
        quiz_version_id = db.execute(stmt).scalar_one()

        db.add(PreSave(
            user_id=user_idx,
            quiz_id=quiz_id,
            quiz_version_id=quiz_version_id,
            answer=None
        ))
        db.commit()


def not_exist_pre_save_by_quiz_and_user_idx(quiz_id, user_idx):
    stmt = (
        select(func.count(PreSave.id))
        .where(
            PreSave.quiz_id == quiz_id,
            PreSave.user_id == user_idx
        )
    )

    with database.session_factory() as db:
        count = db.execute(stmt).scalar_one()

    return True if count == 0 else False


def get_quiz_version_by_quiz_id_and_user_id(quiz_id, user_idx):
    stmt = (
        select(
            QuizVersion.question_ids,
            QuizVersion.selection_info,
            PreSave.answer
        )
        .select_from(PreSave)
        .join(QuizVersion, PreSave.quiz_version_id == QuizVersion.id)
        .where(
            PreSave.quiz_id == quiz_id,
            PreSave.user_id == user_idx
        )
    )

    with database.session_factory() as db:
        return db.execute(stmt).fetchone()


def get_question_info_by_ids(question_ids):
    stmt = (
        select(
            Question.id,
            Question.name
        )
        .where(Question.id.in_(question_ids))
        .order_by(
            case(
                {
                    id_value: index for index, id_value in enumerate(question_ids)
                },
                value=Question.id,
                else_=len(question_ids)
            )
        )
    )

    with database.session_factory() as db:
        return db.execute(stmt).fetchall() if len(question_ids) != 0 else []


def get_final_answer_by_question_id_and_user_id(question_id, user_idx):
    stmt = (
        select(QuestionLog.user_answer)
        .where(
            QuestionLog.question_id == question_id,
            QuestionLog.user_id == user_idx
        )
    )

    with database.session_factory() as db:
        return db.execute(stmt).scalar_one_or_none()


def get_selection_info_by_ids(selection_ids):
    stmt = (
        select(
            Selection.id,
            Selection.name,
            Selection.is_correct
        )
        .where(Selection.id.in_(selection_ids))
        .order_by(
            case(
                {
                    id_value: index for index, id_value in enumerate(selection_ids)
                },
                value=Selection.id,
                else_=len(selection_ids)
            )
        )
    )

    with database.session_factory() as db:
        return db.execute(stmt).fetchall()


def get_question_ids_by_quiz_id(quiz_id):
    stmt = (
        select(Question.id)
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.sequence)
    )

    with database.session_factory() as db:
        return db.execute(stmt).scalars().all()


def is_exist_submit_log(quiz_id: int, user_idx: int):
    stmt = (
        select(func.count(QuestionLog.id))
        .select_from(QuestionLog)
        .join(Question, QuestionLog.question_id == Question.id)
        .where(
            QuestionLog.user_id == user_idx,
            Question.quiz_id == quiz_id
        )
    )

    with database.session_factory() as db:
        return True if db.execute(stmt).scalar() != 0 else False


def update_pre_save_data(quiz_id: int, user_idx: int, answer: str):
    stmt = (
        update(PreSave)
        .where(
            PreSave.quiz_id == quiz_id,
            PreSave.user_id == user_idx
        )
        .values(answer=answer)
    )

    with database.session_factory() as db:
        db.execute(stmt)
        db.commit()