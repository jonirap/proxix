from typing import Any, Callable, Optional, Tuple

from .proxy_manager import ProxyManager
from .request import Request
from .response import RemoteException, Response


class BadRequestError(Exception):
    def __init__(self, request_type):
        # type: (Request.TYPE) -> None
        super().__init__(u"Unknown request type: {}".format(request_type))


class Processor(object):
    def __init__(self, proxy_manager):
        # type: (ProxyManager) -> None
        self.proxy_manager = proxy_manager

    @classmethod
    def _get_value_or_error(cls, func):
        # type: (Callable[[], Any]) -> Tuple[Optional[Any], Optional[Exception]]
        try:
            return func(), None
        except Exception as e:
            return None, e

    def handle(self, request):
        # type: (Request) -> Response
        obj = None
        args = tuple()  # type: Tuple[Any, ...]
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
                return Response(request=request, value=eval(*args))
            if request.request_type == Request.TYPE.import_module:
                return Response(request=request, value=__import__(*args, **kwds))
        except Exception:
            return Response(
                request=request,
                remote_exception=RemoteException.create_from_current(),
            )
        return Response(
            request=request,
            remote_exception=RemoteException("Bad Request", ("", "", "")),
        )
