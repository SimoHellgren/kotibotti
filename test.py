from crud import freezer
from db import connect

with connect("db.sqlite") as conn:
    items = freezer.get_all(conn)

    for item in items:
        print(item)
