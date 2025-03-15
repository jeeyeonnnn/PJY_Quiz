from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.user.endpoint import router as user_router
from app.quiz.endpoint import router as quiz_router

app = FastAPI(docs_url="/docs", openapi_url="/open-api-docs")

@app.get('/', tags=['☑️ Healthy Check'])
def heath_check():
    return 'success'

app.include_router(user_router)
app.include_router(quiz_router)

app.openapi_schema = get_openapi(
        title="🌟 [글로벌널리지] 백엔드 개발자 과제 - 박지연 🌟",
        version="1.0.0",
        description=
        "<h3> 관리자는 퀴즈 상세 조회 시 출제 문제 수와 상관없이 모든 문제를 확인할 수 있도록 설계하였습니다. <h3> \n"
        "<h3> ✔️ [POST] /sign-up  :  회원 가입 <h3> \n"
        "<h3> ✔️ [POST] /sign-in  :  로그인 (=토큰 발급) <h3> \n"
        "\n"
        "<h3> ✔️ [POST] /quiz  : 퀴즈 생성하기 (관리자) <h3> \n"
        "<h3> ✔️ [GET] /quizzes  : 퀴즈 목록 조회 <h3> \n"
        "<h3> ✔️ [GET] /quiz/{quiz_id}  : 퀴즈 상세 조회 <h3> \n"
        "<h3> ✔️ [POST] /quiz/{quiz_id}/pre-save  : 퀴즈 답안 임시 저장 (새로 고침할 경우 프론트에서 이를 호출하게끔 설계) <h3> \n"
        "<h3> ✔️ [POST] /quiz/{quiz_id}/submit  : 퀴즈 답안 최종 제출 <h3> \n"

        '''
                    ## 계정
                    
                    - 관리자 : jeeyeon
                    - 사용자 : user, jeeyeonn
        '''
        ,
        routes=app.routes,
    )