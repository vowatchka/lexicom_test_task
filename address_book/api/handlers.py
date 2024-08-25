from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse

from . import models


def common_handler(status_code: int) -> Callable:
    async def handler(_: Request, ex: Exception):
        error = models.ErrorModel(detail=str(ex))

        return JSONResponse(error.model_dump(), status_code=status_code)

    return handler
