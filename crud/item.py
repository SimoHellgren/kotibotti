from sqlite3 import Connection

from models import Item, ItemCreate, ItemKind

__all__ = [
    "create",
    "delete",
    "get",
    "get_all",
    "get_all_of_kind",
    "update",
]


def get_all(conn: Connection) -> list[Item]:
    result = conn.execute("SELECT * FROM item").fetchall()

    return [Item(**x) for x in result]


def get_all_of_kind(conn: Connection, kind: ItemKind) -> list[Item]:
    result = conn.execute("SELECT * FROM item WHERE kind = ?", (kind,)).fetchall()

    return [Item(**x) for x in result]


def get(conn, id: int) -> Item:
    result = conn.execute("SELECT * FROM item WHERE id = ?", (id,)).fetchone()

    return Item(**result)


def create(conn: Connection, kind: ItemKind, name: str) -> Item:
    item_in = ItemCreate(kind=kind, data={"name": name})

    result = conn.execute(
        "INSERT INTO item(kind,data) VALUES(?,?) RETURNING *",
        (item_in.kind, item_in.data),
    ).fetchone()

    return Item(**result)


def update(conn: Connection, id: int, data: dict) -> Item:
    result = conn.execute(
        "UPDATE item SET data = ? WHERE id = ? RETURNING *", (data, id)
    ).fetchone()

    return Item(**result)


def delete(conn: Connection, id: int) -> Item:
    result = conn.execute("DELETE FROM item WHERE id = ? RETURNING *", (id,)).fetchone()
    return Item(**result)
