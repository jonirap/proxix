import inspect
from typing import Dict, Set, Tuple

CLASS_HIERARCHY_TYPE = Dict[type, "CLASS_HIERARCHY_TYPE"]  # type: ignore


def resolve_hierarchy(cls):
    # type: (type) -> CLASS_HIERARCHY_TYPE
    result, _ = _resolve_hierarchy_with_blacklist(cls)
    return result


def _resolve_hierarchy_with_blacklist(cls):
    # type: (type) -> Tuple[CLASS_HIERARCHY_TYPE, Set[type]]
    subclasses = {}
    blacklist = {cls}  # type: Set[type]
    if cls is not object:
        for i, c in enumerate(inspect.getmro(cls)):
            if i == 0 or c in blacklist:
                continue
            subclasses[c], blklst = _resolve_hierarchy_with_blacklist(c)
            blacklist.update(blklst)
    return subclasses, blacklist
