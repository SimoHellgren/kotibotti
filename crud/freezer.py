from sqlite3 import Connection

from models import FreezerData, FreezerItem, Item, ItemKind

from . import item

__all__ = [
    "create",
    "delete",
    "get",
    "get_all",
    "update",
]


# TODO: this should be generalized when new item kinds appear.
def _to_freezer_item(item: Item):
    return FreezerItem(**item.model_dump())


def get_all(conn: Connection) -> list[FreezerItem]:
    items = item.get_all_of_kind(conn, kind=ItemKind.freezer)

    return [*map(_to_freezer_item, items)]


def get(conn: Connection, id: int) -> FreezerItem:
    return _to_freezer_item(item.get(conn, id))


def create(conn: Connection, data: dict) -> FreezerItem:
    validated = FreezerData(**data)
    return _to_freezer_item(item.create(conn, ItemKind.freezer, validated.model_dump()))


def update(conn: Connection, id: int, data: dict) -> FreezerData:
    validated = FreezerData(**data)
    return _to_freezer_item(item.update(conn, id, validated.model_dump()))


def delete(conn: Connection, id: int) -> FreezerData:
    return _to_freezer_item(item.delete(conn, id))
