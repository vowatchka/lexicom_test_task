from fastapi import FastAPI


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
    )

    return app
