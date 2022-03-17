from typing import Any, Dict, Optional


class ProxyManager(object):
    def __init__(self, initial_state=None):
        # type: (Optional[Dict[int, Any]]) -> None
        self._proxied = initial_state or dict()

    def save(self, obj):
        # type: (Any) -> int
        obj_id = id(obj)
        self._proxied[obj_id] = obj
        return obj_id

    def get(self, obj_id):
        # type: (int) -> Any
        return self._proxied[obj_id]

    def delete(self, obj_id):
        if obj_id in self._proxied:
            self._proxied.pop(obj_id)
