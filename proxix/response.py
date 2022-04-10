import sys
import traceback
from typing import Any, Iterable, Optional, Tuple

from six import text_type

from .request import Request


class RemoteException(Exception):
    def __init__(self, message, sys_exc_info):
        # type: (text_type, Tuple[Any, Any, Any]) -> None
        super(RemoteException, self).__init__(message)
        self.sys_exc_info = sys_exc_info

    @classmethod
    def create_from_current(cls):
        # type: () -> RemoteException
        exc_info = sys.exc_info()
        return cls(
            u"\n\r{}".format("".join(traceback.format_exception(*exc_info))),
            exc_info,
        )


class Response(object):
    def __init__(self, request, value=None, remote_exception=None):
        # type: (Request, Optional[Any], Optional[RemoteException]) -> None
        self.request = request
        self.value = value
        self.remote_exception = remote_exception
