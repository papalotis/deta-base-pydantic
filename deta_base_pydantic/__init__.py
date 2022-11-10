"""
A package providing a deta base interface for pydantic models.
The package provides a BaseModelWithKey class that can be used as a base class for pydantic models.
If you do not want to use that class, you can use the Base class directly, but it has to have
a field named key of type str.

The module does not subclass the deta classes but tries to mimic their interface as closely as possible.
"""

__version__ = "0.1.1.post1"

from pydantic import BaseModel
from deta import Deta
from deta.base import Util
from typing import Generic, TypeVar, Type, Any
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from dataclasses import dataclass


class BaseModelWithKey(BaseModel):
    key: str | None = None


EXPIRE_AT_TYPE = int | float | datetime

T = TypeVar("T", bound=BaseModel)


@dataclass
class FetchResponsePydantic(Generic[T]):
    count: int
    last: str | None
    items: list[T]


class PydanticDetaBase(Generic[T]):
    def __init__(self, datatype: Type[T], name: str, deta: Deta) -> None:
        self._base = deta.Base(name)
        self._datatype = datatype

        if "key" not in self._datatype.__fields__:
            raise ValueError(f"datatype ({self._datatype}) must have a key field")

    @property
    def util(self) -> Util:
        return self._base.util

    def put(
        self, item: T, *, expire_in: int = None, expire_at: EXPIRE_AT_TYPE = None
    ) -> Any | None:
        item_dict = jsonable_encoder(item)
        return self._base.put(item_dict, expire_in=expire_in, expire_at=expire_at)

    def get(self, key: str) -> T:
        item_dict = self._base.get(key)
        return self._datatype(**item_dict)

    def delete(self, key: str) -> None:
        return self._base.delete(key)

    def insert(
        self, item: T, *, expire_in: int = None, expire_at: int = None
    ) -> Any | None:
        item_dict = jsonable_encoder(item)
        return self._base.insert(item_dict, expire_in=expire_in, expire_at=expire_at)

    def put_many(
        self, items: list[T], *, expire_in: int = None, expire_at: EXPIRE_AT_TYPE = None
    ) -> Any:
        items_dict = [jsonable_encoder(item) for item in items]
        return self._base.put_many(items_dict, expire_in=expire_in, expire_at=expire_at)

    def update(
        self,
        updates: dict[str, Any],
        key: str,
        *,
        expire_in: int = None,
        expire_at: EXPIRE_AT_TYPE = None,
    ) -> None:
        return self._base.update(updates, key, expire_in=expire_in, expire_at=expire_at)

    def fetch(
        self, query: dict[str, Any] = None, *, limit: int = None, last: str = None
    ) -> FetchResponsePydantic[T]:
        query_result = self._base.fetch(query, limit=limit, last=last)

        parsed_items = [self._datatype(**item) for item in query_result.items]

        return FetchResponsePydantic(
            query_result.count, query_result.last, parsed_items
        )


# if __name__ == "__main__":

#     class TestModel(BaseModelWithKey):
#         name: str
#         age: int

#     base = PydanticDetaBase(Deta(), TestModel, "test")

#     reveal_type(base.get("abc"))

#     reveal_type(base.fetch().items[0])
