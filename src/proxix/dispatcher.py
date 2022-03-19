from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple

from six import text_type

if TYPE_CHECKING:
    from .response import Response

from .request import Request


class Dispatcher(object):
    def __init__(self, send_request):
        # type: (Callable[[Request], Response]) -> None
        self.send_request = send_request

    def get_proxied_attribute(self, obj_id, name):
        # type: (int, text_type) -> Any
        return self.send_request(
            Request(
                Request.TYPE.getattribute,
                obj_id=obj_id,
                args=(name,),
            )
        ).value

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
        # type: (int, Optional[Tuple], Optional[Dict]) -> Any
        return self.send_request(
            Request(Request.TYPE.call, obj_id=obj_id, args=args, kwds=kwds)
        ).value

    def eval(self, source, globals=None, locals=None):
        # type: (text_type, Dict, Dict) -> Any
        return self.send_request(
            Request(
                Request.TYPE.eval,
                kwds=dict(source=source, globals=globals, locals=locals),
            )
        ).value
