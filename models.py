from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum, auto


class ItemKind(StrEnum):
    freezer = auto()


class ItemCreate(BaseModel):
    kind: ItemKind
    data: dict


class Item(ItemCreate):
    id: int
    created_at: datetime