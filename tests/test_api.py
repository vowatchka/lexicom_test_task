import httpx
import pytest

from address_book import redis_address_book
from address_book.api import models


class TestApi:
    """Тестирование API."""

    phone = "9206114947"
    address = {
        "person": {
            "first_name": "test",
            "last_name": "test",
        },
        "address": "test",
    }
    new_addresses = [
        {
            "person": {
                "first_name": "test1",
                "last_name": "test",
            },
            "address": "test",
        },
        {
            "person": {
                "first_name": "test",
                "last_name": "test1",
            },
            "address": "test",
        },
        {
            "person": {
                "first_name": "test",
                "last_name": "test",
            },
            "address": "test1",
        },
        {
            "person": {
                "first_name": "test1",
                "last_name": "test1",
            },
            "address": "test1",
        },
    ]

    addresses_url = "/api/addresses"

    @pytest.mark.parametrize(
        "index",
        [i for i in range(1, 9)],
    )
    async def test_search_address_ok(
        self, client: httpx.AsyncClient, index: int, redis_address_book_depend: redis_address_book.RedisAddressBook
    ):
        """Проверка, что адрес успешно находится по номеру телефона."""
        # добавляем адрес
        address = models.AddressModel.model_validate(self.address)
        await redis_address_book_depend.add(self.phone, address)

        response = await client.get(f"{self.addresses_url}?phone={self.phone[:-1 * index]}")
        assert response.status_code == 200
        assert response.json() == [{**self.address, "phone": self.phone}]

    async def test_search_empty_adresses_list(self, client: httpx.AsyncClient):
        """Проверка получения пустого списка адресов, когда адрес не найден."""
        response = await client.get(f"{self.addresses_url}?phone={self.phone}")
        assert response.status_code == 200
        assert response.json() == list()

    @pytest.mark.parametrize(
        "index",
        [i for i in range(1, 9)],
    )
    async def test_search_many_addresses_by_pattern(
        self, client: httpx.AsyncClient, index: int, redis_address_book_depend: redis_address_book.RedisAddressBook
    ):
        # добавляем адреса
        addresses: list[models.AddressModelOut] = list()
        addresses.append(models.AddressModelOut.model_validate({**self.address, "phone": self.phone}))
        for idx, addr in enumerate(self.new_addresses):
            addresses.append(models.AddressModelOut.model_validate({**addr, "phone": self.phone[:-1] + str(idx)}))

        addresses = sorted(addresses, key=lambda x: x.phone)

        for address in addresses:
            await redis_address_book_depend.add(address.phone, address)

        response = await client.get(f"{self.addresses_url}?phone={self.phone[:-1 * index]}")
        assert response.status_code == 200
        assert len(response.json()) == len(addresses)
        assert response.json() == [addr.model_dump() for addr in addresses]

    async def test_add_address_ok(self, client: httpx.AsyncClient):
        """Проверка, что адрес добавляется успешно."""
        response = await client.post(f"{self.addresses_url}/{self.phone}", json=self.address)
        assert response.status_code == 201
        assert response.json() == self.address

        # проверяем адрес
        response = await client.get(f"{self.addresses_url}?phone={self.phone}")
        assert response.status_code == 200
        assert response.json() == [{**self.address, "phone": self.phone}]

    async def test_add_when_address_already_exists(
        self, client: httpx.AsyncClient, redis_address_book_depend: redis_address_book.RedisAddressBook
    ):
        """Проверка, что адрес не добавляется и не изменяется, если адрес уже записан."""
        # добавляем адрес
        address = models.AddressModel.model_validate(self.address)
        await redis_address_book_depend.add(self.phone, address)

        # пытаемся добавить такой же адрес снова
        response = await client.post(f"{self.addresses_url}/{self.phone}", json=self.address)
        assert response.status_code == 409
        assert response.json() == {"detail": f"с телефоном {self.phone!r} уже связан другой адрес"}

    @pytest.mark.parametrize(
        "phone",
        [
            "1",
            "123",
            *("9" + (str(i) * i) for i in range(1, 9)),
        ],
    )
    async def test_add_when_invalid_phone(self, client: httpx.AsyncClient, phone: str):
        """Проверка, что адрес не добавляется, когда указан неверный формат номера телефона."""
        response = await client.post(f"{self.addresses_url}/{phone}", json=self.address)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "new_address",
        new_addresses,
    )
    async def test_change_address_ok(
        self,
        client: httpx.AsyncClient,
        new_address: dict,
        redis_address_book_depend: redis_address_book.RedisAddressBook,
    ):
        """Проверка, что адрес изменяется успешно."""
        # добавляем адрес
        address = models.AddressModel.model_validate(self.address)
        await redis_address_book_depend.add(self.phone, address)

        # изменяем адрес
        response = await client.put(f"{self.addresses_url}/{self.phone}", json=new_address)
        assert response.status_code == 200
        assert response.json() == new_address

        # проверяем адрес
        response = await client.get(f"{self.addresses_url}?phone={self.phone}")
        assert response.status_code == 200
        assert response.json() == [{**new_address, "phone": self.phone}]

    async def test_change_when_address_not_found(self, client: httpx.AsyncClient):
        """Проверка, что адрес не изменяется, когда такого адреса нет."""
        response = await client.put(f"{self.addresses_url}/{self.phone}", json=self.address)
        assert response.status_code == 404
        assert response.json() == {"detail": f"для телефона {self.phone!r} адрес не найден"}

    @pytest.mark.parametrize(
        "phone",
        [
            "1",
            "123",
            *("9" + (str(i) * i) for i in range(1, 9)),
        ],
    )
    async def test_change_when_invalid_phone(
        self, client: httpx.AsyncClient, phone: str, redis_address_book_depend: redis_address_book.RedisAddressBook
    ):
        """Проверка, что адрес не изменяется, когда указан неверный формат номера телефона."""
        # добавляем адрес
        address = models.AddressModel.model_validate(self.address)
        await redis_address_book_depend.add(self.phone, address)

        # изменяем адрес
        response = await client.put(f"{self.addresses_url}/{phone}", json=self.new_addresses[0])
        assert response.status_code == 422
