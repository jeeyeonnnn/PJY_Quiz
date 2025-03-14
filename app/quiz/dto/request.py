from typing import List

from pydantic import BaseModel

class SelectionInfoRequest(BaseModel):
    name: str
    is_correct: bool

class QuestionInfoRequest(BaseModel):
    name: str
    selections: List[SelectionInfoRequest]


class QuizInfo(BaseModel):
    name: str
    select_count: int
    pagination_count: int
    is_random: bool
    questions: List[QuestionInfoRequest]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "국가별 수도 알아보기!",
                "select_count": 12,
                "pagination_count": 2,
                "is_random": False,
                "questions": [
                    {
                        "name": "대한민국의 수도는?",
                        "selections": [
                            {
                                "name": "서울",
                                "is_correct": True
                            },
                            {
                                "name": "부산",
                                "is_correct": False
                            },
                            {
                                "name": "인천",
                                "is_correct": False
                            },
                            {
                                "name": "대전",
                                "is_correct": False
                            }
                        ]
                    },
                    {
                        "name": "미국의 수도는?",
                        "selections": [
                            {
                                "name": "로스앤젤레스",
                                "is_correct": False
                            },
                            {
                                "name": "뉴욕",
                                "is_correct": False
                            },
                            {
                                "name": "워싱턴 D.C.",
                                "is_correct": True
                            },
                            {
                                "name": "시카고",
                                "is_correct": False
                            }
                        ]
                    }
                ]
            }
        }

class QuizPreSaveRequest(BaseModel):
    question_id: int
    selection_ids: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": 12,
                "selection_ids": [234, 1245]
            }
        }