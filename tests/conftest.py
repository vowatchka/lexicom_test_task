from typing import AsyncIterable, Literal, Optional, Union

import httpx
import pytest
from _pytest.fixtures import FixtureRequest
from pytest_redis.config import get_config
from redis import asyncio as redis

from address_book import routers, service
from address_book.api import create_app


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def redisdb(
    request: FixtureRequest, redis_proc, dbnum: int = 0, decode: Optional[bool] = None
) -> AsyncIterable[redis.Redis]:
    """
    Оригинал кода взят из pytest-redis. И синхронный клиент заменен на асинхронный.
    """
    config = get_config(request)

    redis_host = redis_proc.host
    redis_port = redis_proc.port
    redis_username = redis_proc.username
    redis_password = redis_proc.password
    redis_db = dbnum
    decode_responses: Union[Literal[True], Literal[False]] = decode if decode is not None else config["decode"]

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        username=redis_username,
        password=redis_password,
        unix_socket_path=redis_proc.unixsocket,
        decode_responses=decode_responses,
    )

    yield redis_client
    await redis_client.flushall()


@pytest.fixture
async def redis_address_book(redisdb: redis.Redis):
    yield service.RedisAddressBook(redisdb)


@pytest.fixture
def app(redis_address_book):
    _app = create_app()

    _app.dependency_overrides[routers.addresses.redis_address_book] = lambda: redis_address_book

    yield _app


@pytest.fixture
async def client(app):
    async with httpx.AsyncClient(base_url="http://testserver", transport=httpx.ASGITransport(app=app)) as _client:
        yield _client
