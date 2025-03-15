from typing import Optional, List

from fastapi import APIRouter, Depends, BackgroundTasks
from starlette import status

from app.quiz.dto.request import QuizInfo, QuizSubmitRequest
from app.quiz.dto.response import Quizzes, QuizDetail
from app.util.auth_handler import auth
from app.util.response_handler import res
from app.quiz import service

router = APIRouter(tags=['QUIZ'], prefix='/quiz')

@router.post(
    path='',
    description='## ✔️️ [퀴즈 생성하기] \n'
                '''
                ## Request Detail ##
                
                - name : 퀴즈 이름
                - select_count : 설정한 문제 갯수 (출제 문제 수)
                - pagination_count : 목록에 보여질 문제의 수 (페이지 네이션에서 활용)
                - is_random : 출제 시 문제 + 보기 랜덤 출제 여부
                
                * Question
                - name : 문항, 문제 내용
                
                * Selection
                - name : 보기 내용
                - is_correct : 보기 정답 여부 (True 정답 / False 오답)
                ''',
    responses={
        status.HTTP_201_CREATED: {
            "description": "퀴즈 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "success"
                    }
                }
            }
        },
        444: {
            "description": "퀴즈에 문제가 하나도 존재하지 않은 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "해당 퀴즈에 문제가 존재하지 않습니다."
                    }
                }
            }
        },
        445: {
            "description": "설정한 출제 문제 수가 총 문제 수보다 작은 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "설정한 출제 문제 수가 총 문제 수보다 작습니다."
                    }
                }
            }
        },
        446: {
            "description": "특정 문제에 보기가 2개 미만인 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "보기가 2개 미만인 문제가 존재합니다."
                    }
                }
            }
        },
        447: {
            "description": "정답이 없는 문제가 존재하는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "정답이 없는 문제가 존재합니다."
                    }
                }
            }
        }
    }
)
async def add_quiz(
        request: QuizInfo,
        task: BackgroundTasks,
        user=Depends(auth.auth_wrapper),
):
    if not user.is_admin:
        return res.post_exception(status.HTTP_401_UNAUTHORIZED, "권한이 존재하지 않습니다.")

    result =  await service.save_new_quiz(
        request.name, request.select_count, request.pagination_count, request.is_random, request.questions
    )

    # 문제가 존재하지 않은 경우
    if result == -1:
        return res.post_exception(444, "해당 퀴즈에 문제가 존재하지 않습니다.")

    # 설정한 출제 문제 수가 총 문제 수보다 작은 경우
    elif result == -2:
        return res.post_exception(445, "설정한 출제 문제 수가 총 문제 수보다 작습니다.")

    # 특정 문제에 보기가 2개 미만인 경우
    elif result == -3:
        return res.post_exception(446, "보기가 2개 미만인 문제가 존재합니다.")

    # 정답이 없는 문제가 존재하는 경우
    elif result == -4:
        return res.post_exception(447, "정답이 없는 문제가 존재합니다.")

    # 백그라운드 task 추가하기
    task.add_task(service.quiz_version_update, result)
    return res.post_success()


@router.get(
    path='zes',
    description='## ✔️️ [퀴즈 목록 조회] \n'
                '''
                ## Request Detail ##
                page : 현재 페이지 (default = 1)
                limit : 목록에 보여질 퀴즈의 수 (default = 5)
                
                
                ## Response Detail ##
                
                * Page
                - total_page : 총 페이지 수
                - total_count : 총 컨텐츠 수 (=총 퀴즈 수)
                - current_page : 현제 페이지 (request param page와 동일한 값)
                
                * Quizzes
                - id : 퀴즈 PK
                - name : 퀴즈 이름
                - is_random : 출제 시 문제 + 보기 랜덤 출제 여부
                - total_question_count : 해당 퀴즈의 속해있는 총 문제 수
                - question_count : 설정한 문제 갯수 (= 출제 문제 수)
                - pagination_count : 한 목록에서 보여질 문제의 수 (페이지네이션)
                - status
                    - Null : 관리자 권한인 경우
                    - 0 : 사용자 권한 + 해당 퀴즈를 푼 적 없음
                    - 1 : 사용자 권한 + 해당 퀴즈의 문제를 모두 풀고 제출한 이력이 있음
                    - 2 : 사용자 권한 + 해당 퀴즈의 특정 문제를 풀고 제출하진 않음 (중간 저장 단계)
                
                ''',
    response_model=Quizzes
)
async def get_all_quiz(
        limit: Optional[int] = 2,
        page: Optional[int] = 1,
        user=Depends(auth.auth_wrapper)
):
    page, quizzes = await service.get_all_quiz_by_auth(limit, page, user)
    return Quizzes(page=page, quizzes=quizzes)


@router.get(
    path='/{quiz_id}',
    description='## ✔️️ [퀴즈 상세 조회] \n'
                '''
                ## Request Detail ##
                - quiz_id : 퀴즈 PK
                - page : 현재 페이지 (default = 1)
                
                

                ## Response Detail ##
                - quiz_name : 퀴즈 이름
                - total_question_count : 해당 퀴즈의 총 보유 문제 수
                - question_count : 출제 문제 수
                - pagination_count : 한 목록 당 보여질 문제 수
                - is_random : 랜덤 출제 여부
                - correct_question_count : 해당 퀴즈에서 맞힌 문제 수
                    (관리자인 경우 무조건 0, 사용자인 경우 최종 제출 전까지는 무조건 0)
                
                
                * Page
                - total_page : 총 페이지 수
                - total_count : 총 컨텐츠 수 (=총 퀴즈 수)
                - current_page : 현제 페이지 (request param page와 동일한 값)
                
                
                * UserAnswers (관리자 Null)
                - question_id : 문제 PK
                - selection_ids : 해당 문제에 사용자가 선택한 답 (= selection의 PK 값)
                
                
                * Question 
                - id : 문제 PK
                - name : 문항, 문제 내용
                
                
                * Selection
                - id : 보기 PK
                - name : 보기 내용
                - is_correct : 보기 정답 여부 (True 정답 / False 오답)
                ''',
    response_model=QuizDetail
)
async def get_quiz_detail(
        quiz_id: int,
        page: Optional[int] = 1,
        user=Depends(auth.auth_wrapper)
):
    (
        quiz_name, total_question_count, question_count, pagination_count,
        is_random, status, correct_question_count, page, user_answers, questions
    ) = await service.get_quiz_detail(quiz_id, user, page)

    return QuizDetail(
        id=quiz_id,
        name=quiz_name,
        total_question_count=total_question_count,
        question_count=question_count,
        pagination_count=pagination_count,
        is_random=is_random,
        correct_question_count=correct_question_count,
        page=page,
        user_answers=user_answers,
        questions=questions
    )

@router.post(
    path='/{quiz_id}/pre-save',
    description='## ✔️️ [퀴즈 임시 저장] \n'
                '''
                ## Request Detail ##
                - question_id : 문제 PK
                - selection_ids : 사용자가 정답이라고 택한 보기의 PK List
                ''',
    responses={
        status.HTTP_201_CREATED: {
            "description": "퀴즈 임시 저장 성공",
            "content": {
                "application/json": {
                    "example": {
                        "message": "success"
                    }
                }
            }
        },
        401: {
            "description": "관리자 권한인 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "사용자 권한이 존재하지 않습니다."
                    }
                }
            }
        },
        409: {
            "description": "사용자가 해당 퀴즈를 최종 제출한 이력이 존재하는 경우",
            "content": {
                "application/json": {
                    "example": {
                        "message": "해당 퀴즈의 최종 제출 이력이 있어 임시저장이 불가능합니다."
                    }
                }
            }
        }
    }
)
async def quiz_pre_save(
        quiz_id: int,
        request: List[QuizSubmitRequest],
        user=Depends(auth.auth_wrapper)
):
    if user.is_admin:
        return res.post_exception(status.HTTP_401_UNAUTHORIZED, "사용자 권한이 존재하지 않습니다.")

    result = await service.update_pre_save_data(quiz_id, user.id, request)

    # 사용자가 해당 퀴즈를 최종 제출한 이력이 존재하는 경우
    if result == -1:
        return res.post_exception(status.HTTP_409_CONFLICT, "해당 퀴즈의 최종 제출 이력이 있어 임시저장이 불가능합니다.")
    return res.post_success()


@router.post(
    path='/{quiz_id}/submit',
    description='## ✔️️ [퀴즈 답안 최종 제출] \n'
                '''
                ## Request Detail ##
                - question_id : 문제 PK
                - selection_ids : 사용자가 정답이라고 택한 보기의 PK List
                ''',
)
async def quiz_final_submit(
        quiz_id: int,
        request: List[QuizSubmitRequest],
        user=Depends(auth.auth_wrapper)
):
    if user.is_admin:
        return res.post_exception(status.HTTP_401_UNAUTHORIZED, "사용자 권한이 존재하지 않습니다.")

    result = await service.final_submit_quiz_answer(quiz_id, user.id, request)

    # 사용자가 해당 퀴즈를 최종 제출한 이력이 존재하는 경우
    if result == -1:
        return res.post_exception(444, "해당 퀴즈의 최종 제출 이력이 있어 최종 제출이 불가능합니다.")

    # 출제 문제 수와 답안 제출 문제 수가 일치하지 않은 경우
    elif result == -2:
        return res.post_exception(445, "출제 문제 수와 답안 제출 문제 수가 일치하지 않습니다.")

    return res.post_success()