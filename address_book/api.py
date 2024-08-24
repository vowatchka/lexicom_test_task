from fastapi import FastAPI

from . import handlers, service
from .routers import api_router


def create_app():
    app = FastAPI(
        title="Address Book",
        description="Address Book",
        version="0.0.1",
        contact={
            "name": "Vladimir Saltykov",
            "url": "https://github.com/vowatchka",
            "email": "vowatchka@mail.ru",
        },
        license_info={
            "name": "MIT",
            "identifier": "MIT",
        },
        exception_handlers={
            service.AddressAlreadyExistsError: handlers.common_handler(409),
            service.AddressNotFoundError: handlers.common_handler(404),
        },
    )

    app.include_router(api_router)

    return app
