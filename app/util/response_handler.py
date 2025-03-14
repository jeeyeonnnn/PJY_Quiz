from typing import Union

from fastapi import status
from starlette.responses import JSONResponse


class ResponseHandler:
    @staticmethod
    def post_success():
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={'message': 'success'}
        )

    @staticmethod
    def post_exception(code, message: str):
        return JSONResponse(
            status_code=code,
            content={'message': message}
        )

    @staticmethod
    def post_custom(key: str, value: str):
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={key: value}
        )

res = ResponseHandler()