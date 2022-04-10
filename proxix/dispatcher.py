from typing import Any, Callable, Dict, Optional, Tuple

from six import text_type

from .request import Request


class Dispatcher(object):
    def __init__(self, send_request):
        # type: (Callable[[Request], Any]) -> None
        self.send_request = send_request

    def import_module(self, name):
        # type: (text_type) -> Any
        return self.send_request(Request(Request.TYPE.import_module, args=(name,)))

    def get_proxied_attribute(self, obj_id, name):
        # type: (int, text_type) -> Any
        return self.send_request(
            Request(
                Request.TYPE.getattribute,
                obj_id=obj_id,
                args=(name,),
            )
        )

    def set_proxied_attribute(self, obj_id, name, value):
        # type: (int, text_type, Any) -> None
        self.send_request(
            Request(
                Request.TYPE.setattr,
                obj_id=obj_id,
                args=(name, value),
            )
        )

    def call(self, obj_id, args=None, kwds=None):
        # type: (int, Optional[Tuple[Any, ...]], Optional[Dict[str, Any]]) -> Any
        return self.send_request(
            Request(Request.TYPE.call, obj_id=obj_id, args=args, kwds=kwds)
        )

    def eval(self, source, globals=None, locals=None):
        # type: (text_type, Optional[Dict[str, Any]], Optional[Dict[str, Any]]) -> Any
        return self.send_request(
            Request(
                Request.TYPE.eval,
                args=(source, globals, locals),
            )
        )
