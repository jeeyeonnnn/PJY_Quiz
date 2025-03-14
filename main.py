from fastapi import FastAPI
import uvicorn

from app.user.endpoint import router as user_router
from app.quiz.endpoint import router as quiz_router

app = FastAPI(docs_url="/api-docs", openapi_url="/open-api-docs")
app.include_router(user_router)
app.include_router(quiz_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
