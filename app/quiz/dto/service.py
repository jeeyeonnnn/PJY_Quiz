from typing import Optional, List

from pydantic import BaseModel

class QuizInfo(BaseModel):
    id: int
    name: str
    total_question_count: int
    question_count: int
    pagination_count: int
    is_random: bool
    status: Optional[int] = None

    class Config:
        from_attributes = True


class SelectionInfoService(BaseModel):
    id: int
    name: str
    is_correct: bool

    class Config:
        from_attributes = True


class QuestionInfoService(BaseModel):
    id: int
    name: str
    user_answer: Optional[List[int]] = None
    selections: List[SelectionInfoService]
