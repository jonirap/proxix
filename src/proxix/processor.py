from typing import Any, Callable, Optional, Tuple

from .manager import ProxyManager
from .request import Request
from .response import Response


class BadRequestError(Exception):
    def __init__(self, request_type) -> None:
        super().__init__(u"Unknown request type: {}".format(request_type))


class Processor(object):
    def __init__(self, proxy_manager):
        # type: (ProxyManager) -> None
        self.proxy_manager = proxy_manager

    @classmethod
    def _get_value_or_error(cls, func):
        # type: (Callable) -> Tuple[Optional[Any], Optional[Exception]]
        try:
            return func(), None
        except Exception as e:
            return None, e

    def handle(self, request):
        # type: (Request) -> Response
        obj = None
        args = ()  # type: Tuple
        kwds = {}
        if request.obj_id is not None:
            obj = self.proxy_manager.get(request.obj_id)
        if request.args:
            args = request.args
        if request.kwds:
            kwds = request.kwds
        try:
            if request.request_type == Request.TYPE.getattribute:
                return Response(request=request, value=getattr(obj, *args, **kwds))
            if request.request_type == Request.TYPE.setattr:
                setattr(obj, *args, **kwds)
                return Response(request=request)
            if request.request_type == Request.TYPE.call:
                assert obj is not None
                return Response(request=request, value=obj(*args, **kwds))
            if request.request_type == Request.TYPE.eval:
                return Response(request=request, value=eval(*args, **kwds))
        except Exception as e:
            return Response(request=request, error=e)
        return Response(request=request, error=BadRequestError(request.request_type))
