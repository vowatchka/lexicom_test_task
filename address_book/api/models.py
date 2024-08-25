from pydantic import BaseModel, Field


class ErrorModel(BaseModel):
    detail: str


class PersonModel(BaseModel):
    first_name: str
    last_name: str


class AddressModel(BaseModel):
    person: PersonModel
    address: str


class AddressModelOut(AddressModel):
    phone: str = Field(..., pattern=r"^9\d+{9}$")
