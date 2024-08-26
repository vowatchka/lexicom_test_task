import json
import os
from typing import Optional

from redis import asyncio as redis

from ..api import address_book, models


class RedisAddressBook(address_book.AddressBook):
    """Адресная книга с хранилищем в Redis."""

    def __init__(self, storage: redis.Redis):
        self._storage = storage

    async def _set_address(self, phone: str, address: models.AddressModel):
        await self._storage.set(phone, json.dumps(address.model_dump()))

    async def search(self, phone_pattern: str) -> list[models.AddressModelOut]:
        addresses: list[models.AddressModelOut] = list()

        keys = await self._storage.keys(phone_pattern)
        for key in keys:
            stored_address = await self._storage.get(key)
            stored_address = json.loads(stored_address)
            stored_address["phone"] = key

            addresses.append(models.AddressModelOut.model_validate(stored_address))

        return [addr for addr in sorted(addresses, key=lambda x: x.phone)]

    async def get(self, phone: str) -> Optional[models.AddressModel]:
        stored_address = await self._storage.get(phone)
        if not stored_address:
            return None
        return models.AddressModel.model_validate(json.loads(stored_address))

    async def add(self, phone: str, address: models.AddressModel):
        if await self._storage.exists(phone):
            raise address_book.AddressAlreadyExistsError(f"с телефоном {phone!r} уже связан другой адрес")
        await self._set_address(phone, address)

    async def change(self, phone: str, new_address: models.AddressModel):
        if not (await self._storage.exists(phone)):
            raise address_book.AddressNotFoundError(f"для телефона {phone!r} адрес не найден")
        await self._set_address(phone, new_address)


async def redis_address_book() -> address_book.AddressBook:
    yield RedisAddressBook(redis.from_url(os.getenv("REDIS_URL")))
