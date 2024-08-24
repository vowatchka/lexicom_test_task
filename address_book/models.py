from pydantic import BaseModel


class ErrorModel(BaseModel):
    detail: str


class PersonModel(BaseModel):
    first_name: str
    last_name: str


class AddressModel(BaseModel):
    person: PersonModel
    address: str
