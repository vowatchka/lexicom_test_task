import os
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from redis import asyncio as redis

from .. import models, service

addresses_router = APIRouter(prefix="/addresses", tags=["Addresses"])


async def redis_address_book():
    yield service.RedisAddressBook(redis.from_url(os.getenv("REDIS_URL")))


PhoneQuery = Annotated[
    str,
    Query(
        pattern=r"^9\d*",
        description="Шаблон номера телефона, по которому будет осуществляться поиск адресов",
        min_length=1,
        max_length=10,
    ),
]
PhonePath = Annotated[
    str,
    Path(
        pattern=r"^9\d+{9}$",
        description="Номер телефона",
    ),
]
AddressBook = Annotated[service.RedisAddressBook, Depends(redis_address_book)]


@addresses_router.get(
    "",
    summary="Найти адреса",
    description="Поиск адресов, чьи номера телефонов совпадают с указанным",
    status_code=200,
)
async def search_addresses(phone: PhoneQuery, address_book: AddressBook) -> list[models.AddressModel]:
    addresses = await address_book.search(f"{phone}*")
    return [models.AddressModel.model_validate(addr.model_dump()) for addr in addresses]


@addresses_router.post(
    "/{phone}",
    summary="Добавить адрес",
    description="Добавление адреса по номеру телефона",
    status_code=201,
    response_description="Address Appended",
    responses={
        409: {"model": models.ErrorModel, "description": "Address Already Exists"},
    },
)
async def add_address(phone: PhonePath, body: models.AddressModel, address_book: AddressBook) -> models.AddressModel:
    await address_book.add(phone, service.Address.model_validate(body.model_dump()))
    return body


@addresses_router.put(
    "/{phone}",
    summary="Изменить адрес",
    description="Изменение адреса по номеру телефона",
    status_code=200,
    response_description="Address Changed",
    responses={
        404: {"model": models.ErrorModel, "description": "Address Not Found"},
    },
)
async def change_address(phone: PhonePath, body: models.AddressModel, address_book: AddressBook) -> models.AddressModel:
    await address_book.change(phone, service.Address.model_validate(body.model_dump()))
    return body
