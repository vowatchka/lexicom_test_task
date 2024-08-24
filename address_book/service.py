import abc
import json

from pydantic import BaseModel
from redis import asyncio as redis


class Person(BaseModel):
    first_name: str
    last_name: str


class Address(BaseModel):
    person: Person
    address: str


class AddressAlreadyExistsError(Exception):
    """Адрес уже существует."""

    pass


class AddressNotFoundError(Exception):
    """Адрес не найден."""

    pass


class AddressBook(abc.ABC):
    """Адресная книга."""

    async def search(self, phone_pattern: str) -> list[Address]:
        """Поиск адресов."""
        pass

    async def add(self, phone: str, address: Address):
        """Добавить адрес."""
        pass

    async def change(self, phone: str, new_address: Address):
        """Изменить адрес."""
        pass


class RedisAddressBook(AddressBook):
    """Адресная книга с хранилищем в Redis."""

    def __init__(self, storage: redis.Redis):
        self._storage = storage

    async def _set_address(self, phone: str, address: Address):
        await self._storage.set(phone, json.dumps(address.model_dump()))

    async def search(self, phone_pattern: str) -> list[Address]:
        addresses = list()

        keys = await self._storage.keys(phone_pattern)
        for key in keys:
            stored_address = await self._storage.get(key)
            addresses.append(Address.model_validate(json.loads(stored_address)))

        return addresses

    async def add(self, phone: str, address: Address):
        if await self._storage.exists(phone):
            raise AddressAlreadyExistsError(f"для телефона {phone!r} адрес уже существует")
        await self._set_address(phone, address)

    async def change(self, phone: str, new_address: Address):
        if not (await self._storage.exists(phone)):
            raise AddressNotFoundError(f"для телефона {phone!r} адрес не найден")
        await self._set_address(phone, new_address)
