import abc
from typing import Optional

from . import models


class AddressAlreadyExistsError(Exception):
    """Адрес уже существует."""

    pass


class AddressNotFoundError(Exception):
    """Адрес не найден."""

    pass


class AddressBook(abc.ABC):
    """Адресная книга."""

    @abc.abstractmethod
    async def search(self, phone_pattern: str) -> list[models.AddressModelOut]:
        """
        Поиск адресов.

        :param phone_pattern: шаблон номера телефона для поиска адресов.
        """
        pass

    @abc.abstractmethod
    async def get(self, phone: str) -> Optional[models.AddressModel]:
        """
        Получить адрес по номеру телефона.

        :param phone: номер телефона.
        :return: адрес или `None`, если по номеру телефона `phone` адрес не найден.
        """
        pass

    @abc.abstractmethod
    async def add(self, phone: str, address: models.AddressModel):
        """
        Добавить адрес.

        :param phone: номер телефона.
        :param address: адрес.

        :raise AddressAlreadyExistsError: когда уже существует адрес, связанный с номером телефона `phone`.
        """
        pass

    @abc.abstractmethod
    async def change(self, phone: str, new_address: models.AddressModel):
        """
        Изменить адрес.

        :param phone: номер телефона.
        :param new_address: новый адрес.

        :raise AddressNotFoundError: когда не найден адрес по номеру телефона `phone`.
        """
        pass
