from typing import List, Optional

from pydantic import BaseModel

from app.quiz.dto.service import QuizInfo, QuestionInfoService
from app.util.pagination import pagination


class Quizzes(BaseModel):
    page: pagination.Page
    quizzes: List[QuizInfo]

    class Config:
        json_schema_extra = {
            "example": {
                "page": {
                    "total_page": 2,
                    "total_count": 3,
                    "current_page": 2
                },
                "quizzes": [
                    {
                        "id": 6,
                        "name": "상식 QUIZ 22 !!!!",
                        "total_question_count": 7,
                        "question_count": 6,
                        "is_random": True,
                        "status": 0
                    }
                ]
            }
        }


class QuizDetail(BaseModel):
    id: int
    name: str
    total_question_count: int
    question_count: int
    pagination_count: int
    is_random: bool
    correct_question_count: int
    page: pagination.Page
    questions: List[QuestionInfoService]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 4,
                "name": "국가별 수도 알아보기!",
                "total_question_count": 2,
                "question_count": 2,
                "pagination_count": 1,
                "is_random": True,
                "correct_question_count": 0,
                "page": {
                    "total_page": 2,
                    "total_count": 2,
                    "current_page": 1
                },
                "questions": [
                    {
                        "id": 4,
                        "name": "미국의 수도는?",
                        "user_answer": [
                            12
                        ],
                        "selections": [
                            {
                                "id": 9,
                                "name": "로스앤젤레스",
                                "is_correct": False
                            },
                            {
                                "id": 10,
                                "name": "뉴욕",
                                "is_correct": False
                            },
                            {
                                "id": 12,
                                "name": "시카고",
                                "is_correct": False
                            },
                            {
                                "id": 11,
                                "name": "워싱턴 D.C.",
                                "is_correct": True
                            }
                        ]
                    }
                ]
            }
        }