import json
from typing import List

from sqlalchemy import update, desc
from sqlalchemy.sql import func, select, case

from app.config.database import database
from app.config.model import Quiz, Question, Selection, QuestionLog, QuizVersion, PreSave
from app.quiz.dto.request import QuestionInfoRequest, QuizSubmitRequest


async def save_new_quiz(
        name: str, select_count: int, pagination_count:int, is_random: bool, questions: List[QuestionInfoRequest]
) -> int:
    # 문제가 존재하지 않은 경우
    if len(questions) == 0:
        return -1

    # 출제할 문제 수가 총 문제 수보다 작은 경우
    if len(questions) < select_count:
        return -2


    async with database.session_factory() as db:
        new_quiz = Quiz(
            name=name,
            q_count=len(questions),
            s_count=select_count,
            p_count=pagination_count,
            is_random=is_random
        )

        db.add(new_quiz)
        await db.flush()

        for question_idx in range(len(questions)):
            q_name, selections = questions[question_idx].name, questions[question_idx].selections

            new_question = Question(
                quiz_id=new_quiz.id,
                name=q_name,
                sequence=question_idx+1
            )
            db.add(new_question)
            await db.flush()

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

        await db.commit()
        return new_quiz.id


async def get_all_quiz_by_auth_and_limit(limit: int, page: int, user_idx: int, is_admin: bool):
    quiz_sql = (
        select(
            Quiz.id.label("id"),
            Quiz.name.label("name"),
            Quiz.s_count.label("question_count"),
            func.count(Question.id.distinct()).label("total_question_count"),
            Quiz.p_count.label("pagination_count"),
            Quiz.is_random.label("is_random"),

            # 관리자인 경우 null / 퀴즈를 안 푼 경우 0 / 푼 경우 1 / 임시 저장 2
            case(
                (is_admin == True, None),
                (
                    func.exists(
                        select(1).select_from(QuestionLog)
                        .join(Question, QuestionLog.question_id == Question.id)
                        .where(
                            QuestionLog.user_id == user_idx,
                            Question.quiz_id == Quiz.id
                        ).scalar_subquery()
                    ),
                    1  # QuestionLog에 존재 == 퀴즈를 최종 제출한 이력이 있음
                ),
                (
                    func.exists(
                        select(1).select_from(PreSave)
                        .where(
                            PreSave.user_id == user_idx,
                            PreSave.quiz_id == Quiz.id
                        ).scalar_subquery()
                    ),
                    2  # PreSave 존재 == 중간 저장 혹은 해당 퀴즈의 상세 페이지에 접근한 적이 있음
                ),
                else_=0  # 그 외 상태 0
            ).label("status")
        )
        .select_from(Question)
        .join(Quiz, Question.quiz_id == Quiz.id)
        .group_by(Quiz.id)
        .order_by(desc(Quiz.id))
        .offset((page-1) * limit)
        .limit(limit)
    )

    async with database.session_factory() as db:
        result = await db.execute(
            select(func.count(Quiz.id))
        )
        quiz_result = await db.execute(quiz_sql)

        return result.scalar(), quiz_result.fetchall()


async def get_quiz_info_by_id(quiz_id: int):
    questions_stmt = (
        select(
            Question.id.label("id"),
            Question.name.label("name")
        )
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.sequence)
    )

    async with database.session_factory() as db:
        result = await db.execute(questions_stmt)
        return result.fetchall()


async def get_quiz_info_by_id_and_user(quiz_id: int, user_idx: int, is_admin: bool):
    quiz_stmt = (
        select(
            Quiz.name,
            func.count(Question.id),
            Quiz.s_count,
            Quiz.p_count,
            Quiz.is_random,
            # status : 관리자인 경우 null / 퀴즈를 안 푼 경우 0 / 푼 경우 1 / 임시 저장 2
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
            # correct_question_count : 유저 별 해당 퀴즈에서 맞힌 문제 수
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

    async with database.session_factory() as db:
        result = await db.execute(quiz_stmt)
        return result.fetchone()


async def get_selections_by_question_id_and_is_random(question_id: int):
    stmt = (
        select(
            Selection.id.label("id"),
            Selection.name.label("name"),
            Selection.is_correct.label("is_correct")
        )
        .where(Selection.question_id == question_id)
        .order_by(Selection.sequence)
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.fetchall()


async def get_quiz_is_random_and_question_ids_by_quiz_id(quiz_id: int):
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

    async with database.session_factory() as db:
        quiz_result = await db.execute(quiz_stmt)
        question_result = await db.execute(question_stmt)

        is_random, s_count = quiz_result.fetchone()
        question_ids = question_result.scalars().all()

    return is_random, s_count, question_ids


async def get_selection_ids_by_question_id(question_id: int):
    stmt = (
        select(Selection.id)
        .where(Selection.question_id == question_id)
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.scalars().all()


async def add_quiz_version(quiz_id: int, version_num: int, question_info: List, selection_info: dict):
    async with database.session_factory() as db:
        db.add(QuizVersion(
            quiz_id=quiz_id,
            version=version_num,
            question_ids=json.dumps(question_info),
            selection_info=json.dumps(selection_info)
        ))
        await db.commit()


async def get_max_quiz_version_by_quiz_id(quiz_id: int):
    async with database.session_factory() as db:
        result = await db.execute(
            select(func.max(QuizVersion.version))
            .where(QuizVersion.quiz_id == quiz_id)
        )
        return result.scalar()


async def update_quiz_version_by_user(user_idx: int, quiz_id: int, version_num: int):
    stmt = (
        select(QuizVersion.id)
        .where(
            QuizVersion.quiz_id == quiz_id,
            QuizVersion.version == version_num
        )
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        quiz_version_id = result.scalar_one()

        db.add(PreSave(
            user_id=user_idx,
            quiz_id=quiz_id,
            quiz_version_id=quiz_version_id,
            answer=None
        ))
        await db.commit()


async def not_exist_pre_save_by_quiz_and_user_idx(quiz_id: int, user_idx: int):
    stmt = (
        select(func.count(PreSave.id))
        .where(
            PreSave.quiz_id == quiz_id,
            PreSave.user_id == user_idx
        )
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        count = result.scalar_one()

    return True if count == 0 else False


async def get_quiz_version_by_quiz_id_and_user_id(quiz_id: int, user_idx: int):
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

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.fetchone()


async def get_question_info_by_ids(question_ids: List[int]):
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

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.fetchall() if len(question_ids) != 0 else []


async def get_selection_info_by_ids(selection_ids: List[int]):
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

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.fetchall()


async def is_exist_submit_log(quiz_id: int, user_idx: int):
    stmt = (
        select(func.count(QuestionLog.id))
        .select_from(QuestionLog)
        .join(Question, QuestionLog.question_id == Question.id)
        .where(
            QuestionLog.user_id == user_idx,
            Question.quiz_id == quiz_id
        )
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return True if result.scalar() != 0 else False


async def update_pre_save_data(quiz_id: int, user_idx: int, answer: str):
    stmt = (
        update(PreSave)
        .where(
            PreSave.quiz_id == quiz_id,
            PreSave.user_id == user_idx
        )
        .values(answer=answer)
    )

    async with database.session_factory() as db:
        await db.execute(stmt)
        await db.commit()


async def get_final_answer_by_user_id_and_quiz_id(user_idx: int, quiz_id: int):
    stmt = (
        select(
            QuestionLog.question_id,
            QuestionLog.user_answer
        )
        .select_from(QuestionLog)
        .join(Question, QuestionLog.question_id == Question.id)
        .where(
            QuestionLog.user_id == user_idx,
            Question.quiz_id == quiz_id
        )
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        answer_info = result.fetchall()
        return answer_info if len(answer_info) != 0 else None


async def quiz_select_count_by_id(quiz_id: int):
    stmt = (
        select(Quiz.s_count)
        .where(Quiz.id == quiz_id)
    )

    async with database.session_factory() as db:
        result = await db.execute(stmt)
        return result.scalar()


async def final_submit_user_answer(user_idx: int, requests: List[QuizSubmitRequest]):
    async with database.session_factory() as db:
        for request in requests:
            question_id, answer = request.question_id, sorted(request.selection_ids)

            result = await db.execute(
                select(Selection.id)
                .where(
                    Selection.question_id == question_id,
                    Selection.is_correct == True
                )
                .order_by(Selection.id)
            )
            real_answer = result.scalars().all()

            db.add(QuestionLog(
                user_id=user_idx,
                question_id=question_id,
                user_answer=json.dumps(answer),
                is_correct=True if answer == real_answer else False
            ))

        await db.commit()