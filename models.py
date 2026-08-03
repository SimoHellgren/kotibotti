from datetime import datetime
from enum import StrEnum, auto
from typing import Literal

from pydantic import BaseModel


class ItemKind(StrEnum):
    freezer = auto()


class ItemCreate(BaseModel):
    kind: ItemKind
    data: dict


class Item(ItemCreate):
    id: int
    created_at: datetime


class FreezerData(BaseModel):
    name: str


class FreezerItem(Item):
    kind: Literal[ItemKind.freezer] = ItemKind.freezer
    data: FreezerData
