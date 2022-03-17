from typing import Any, Callable, Optional, Tuple

from .response import Response
from .request import Request
from .manager import ProxyManager


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
        def lambda_func():
            raise BadRequestError(request.request_type)
        obj = None
        args = []
        kwds = {}
        if request.obj_id is not None:
            obj = self.proxy_manager.get(request.obj_id)
        if request.args:
            args = request.args
        if request.kwds:
            kwds = request.kwds
        if request.request_type == Request.TYPE.getattribute:
            lambda_func = lambda: getattr(obj, *args, **kwds)
        if request.request_type == Request.TYPE.setattr:
            lambda_func = lambda: setattr(obj, *args, **kwds)
        if request.request_type == Request.TYPE.call:
            lambda_func = lambda: obj(*args, **kwds)
        if request.request_type == Request.TYPE.eval:
            lambda_func = lambda: eval(*args, **kwds)
        value, error = self._get_value_or_error(lambda_func)
        return Response(request=request, value=value, error=error)
