import json
import random
from itertools import permutations
from typing import List, Optional

from app.config.model import User
from app.quiz.dto.request import QuestionInfoRequest, SelectionInfoRequest, QuizPreSaveRequest
from app.quiz import repository
from app.quiz.dto.service import QuizInfo, QuestionInfoService, SelectionInfoService
from app.util.pagination import pagination


def save_new_quiz(name: str, select_count: int, pagination_count: int, is_random: bool, questions: List[QuestionInfoRequest]):
    '''
    :param name: 퀴즈 이름
    :param select_count: 출제할 문제 수
    :param pagination_count: 한 목록에 보여질 문제의 수 (페이지 네이션)
    :param is_random: 퀴즈 출제 시 랜덤 여부
    :param questions: 퀴즈의 문제 데이터

    :return: int
            quiz PK : 성공적으로 퀴즈 생성 완료 (새로 생성된 퀴즈의 PK가 반환)
            -1 : 퀴즈에 문제가 한 개도 없는 경우
            -2 : 설정한 출제 문제 수가 총 문제 수보다 작은 경우
            -3 : 특정 문제에 보기가 2개 미만인 경우
            -4 : 특정 문제에 정답이 한 개라도 존재하지 않은 경우
    '''
    return repository.save_new_quiz(name, select_count, pagination_count, is_random, questions)


def get_all_quiz_by_auth(limit: int, page: int, user: User):
    total_quiz_count, quiz_info = repository.get_all_quiz_by_auth_and_limit(
        limit, page, user.id, user.is_admin
    )

    quizzes = [QuizInfo.model_validate(quiz) for quiz in quiz_info]
    page_info = pagination.get_page_data(total_quiz_count, limit, page)

    return page_info, quizzes


def get_quiz_detail(quiz_id: int, user: User, page: int):
    quiz_name, total_question_count, question_count, pagination_count, is_random, status, correct_question_count = \
        repository.get_quiz_info_by_id(quiz_id, user.id, user.is_admin)

    # 관리자가 아닌 경우
    if not user.is_admin:
        questions = []

        # 랜덤 출제 + 사용자가 한번도 해당 퀴즈에 진입한 적이 없는 경우
        if is_random and repository.not_exist_pre_save_by_quiz_and_user_idx(quiz_id, user.id):
            version_num = 1

            if is_random:
                max_version = repository.get_max_quiz_version_by_quiz_id(quiz_id)
                version_num = random.randint(1, max_version)

            # 랜덤 출제한 퀴즈 임시 저장
            repository.update_quiz_version_by_user(user.id, quiz_id, version_num)

        question_ids, selection_info, pre_save_answer = repository.get_quiz_version_by_quiz_id_and_user_id(quiz_id, user.id)
        question_ids, selection_info = json.loads(question_ids), json.loads(selection_info)

        page_info = pagination.get_page_data(len(question_ids), pagination_count, page)
        question_info = repository.get_question_info_by_ids(
            question_ids[(page-1)*pagination_count : page*pagination_count]
        )

        for question_id, question_name in question_info:
            selection_ids = selection_info[str(question_id)]
            questions.append(QuestionInfoService(
                id=question_id,
                name=question_name,
                user_answer=get_user_answer(pre_save_answer, question_id, user.id),
                selections=[
                    SelectionInfoService.model_validate(selection) for selection in
                    repository.get_selection_info_by_ids(selection_ids)
                ]
            ))

        return (
            quiz_name, total_question_count, question_count, pagination_count,
            is_random, status, correct_question_count, page_info, questions
        )

    # 관리자인 경우
    # 관리자는 랜덤 출제 + 출제 문항 수 상관 없이 모든 문제의 정보를 볼 수 있게 설정
    else:
        questions = repository.get_quiz_info_by_id_and_user(quiz_id)
        page_info = pagination.get_page_data(len(questions), pagination_count, page)
        question_info = []

        for question_id, question_name in questions[(page-1)*pagination_count:page*pagination_count]:
            question_info.append(QuestionInfoService(
                id=question_id,
                name=question_name,
                user_answer=None,
                selections=[
                    SelectionInfoService.model_validate(selection) for selection in
                    repository.get_selections_by_question_id_and_is_random(question_id, is_random)
                ]
            ))
        return (
            quiz_name, total_question_count, question_count,
            pagination_count, is_random, status,
            correct_question_count, page_info, question_info
        )


def quiz_version_update(quiz_id: int):
    '''
    @ 퀴즈가 새로 생성 시 가능한 버전을 미리 세팅하는 함수
    - 랜덤인 경우 : 최대 10개의 버전을 만들어 사용자에게 랜덤으로 지급
    - 랜덤이 아닌 경우 : 차례대로 문항을 배분

    :param quiz_id: 퀴즈 PK
    '''

    is_random, s_count, question_ids = repository.get_quiz_is_random_and_question_ids_by_quiz_id(quiz_id)

    if is_random:
        perm = list(permutations(question_ids, s_count))
        random.shuffle(perm)
        version_num = 1

        for ramdom_question_ids in perm[:10]:
            question_info, selection_info = [], {}
            for question_id in ramdom_question_ids:
                selection_ids = repository.get_selection_ids_by_question_id(question_id)
                random.shuffle(selection_ids)
                question_info.append(question_id)
                selection_info[question_id] = selection_ids

            repository.add_quiz_version(quiz_id, version_num, question_info, selection_info)
            version_num += 1

    else:
        question_info, selection_info = [], {}
        for question_id in question_ids[:s_count]:
            selection_ids = repository.get_selection_ids_by_question_id(question_id)
            question_info.append(question_id)
            selection_info[question_id] = selection_ids

        repository.add_quiz_version(quiz_id, 1, question_info, selection_info)


def get_user_answer(pre_save_answer: Optional[str], question_id: int, user_idx: int):
    '''
    @ 해당 문제에 대해 유저가 선택한 답안을 return

    :param pre_save_answer: 임시 저장된 퀴즈의 정답 데이터 (json 형태의 String 혹은 None)
    :param question_id: 문제 PK
    :param user_idx: 사용자 PK

    :return: None 혹은 List[int]
    '''

    # 임시 저장을 한번도 안한 경우
    if pre_save_answer is None:
        return None

    pre_save_answer = json.loads(pre_save_answer)

    # 임시 저장은 했지만, 해당 문제는 푼 적이 없는 경우
    if str(question_id) not in pre_save_answer:
        return None

    final_answer = repository.get_final_answer_by_question_id_and_user_id(question_id, user_idx)

    #
    if final_answer is None:
        return pre_save_answer[str(question_id)]

    return json.loads(final_answer)


def update_pre_save_data(quiz_id: int, user_idx: int, request: List[QuizPreSaveRequest]):
    if repository.is_exist_submit_log(quiz_id, user_idx):
        return -1

    pre_save_answer = {}

    for quiz_answer_info in request:
        pre_save_answer[quiz_answer_info.question_id] = quiz_answer_info.selection_ids

    repository.update_pre_save_data(quiz_id, user_idx, json.dumps(pre_save_answer))
    return True