from fastapi import FastAPI
import uvicorn

from app.user.endpoint import router as user_router

app = FastAPI(docs_url="/api-docs", openapi_url="/open-api-docs")
app.include_router(user_router)
# if __name__ == "__main__":
#     app.include_router(user_router)
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
