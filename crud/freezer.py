from functools import partial

from models import ItemKind

from . import item

__all__ = [
    "create",
    "delete",
    "get",
    "get_all",
    "update",
]


get_all = partial(item.get_all_of_kind, kind=ItemKind.freezer)

get = item.get
create = partial(item.create, kind=ItemKind.freezer)
update = item.update
delete = item.delete
