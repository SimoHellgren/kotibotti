from db import connect
import crud

data = [
    "Selleri",
    "Jäätelö",
]

with connect("db.sqlite") as conn:

    # items = [create_item(conn, "freezer", name) for name in data]
    # item = crud.delete_item(conn, 2)

    items = crud.get_all_items(conn)

    for item in items:
        print(item)
