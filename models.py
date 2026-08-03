from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel


class ItemKind(StrEnum):
    freezer = auto()


class ItemCreate(BaseModel):
    kind: ItemKind
    data: dict


class Item(ItemCreate):
    id: int
    created_at: datetime
