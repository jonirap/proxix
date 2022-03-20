from typing import Any, Optional

from .request import Request


class Response(object):
    def __init__(self, request, value=None, error=None):
        # type: (Request, Optional[Any], Optional[Exception]) -> None
        self.request = request
        self.value = value
        self.error = error
