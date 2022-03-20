from builtins import str
from typing import Any

from .dispatcher import Dispatcher


class Proxy(object):
    def __init__(self, dispatcher, obj_id):
        # type: (Dispatcher, int) -> None
        self.__dispatcher = dispatcher
        self.__obj_id = obj_id

    def __getattribute__(self, __name):
        # type: (str) -> Any
        if __name in (u"__obj_id", u"__dispatcher"):
            return super(Proxy, self).__getattribute__(__name)
        else:
            return self.__dispatcher.get_proxied_attribute(self.__obj_id, __name)

    def __setattr__(self, __name, __value):
        # type: (str, Any) -> Any
        if __name in (u"__obj_id", u"__dispatcher"):
            return super(Proxy, self).__setattr__(__name, __value)
        else:
            return self.__dispatcher.set_proxied_attribute(
                self.__obj_id, __name, __value
            )

    def __call__(self, *args, **kwds):
        # type: (Any, Any) -> Any
        return self.__dispatcher.call(self.__obj_id, args, kwds)
