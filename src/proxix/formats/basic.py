from builtins import bytes, str
from typing import Any, Dict, Tuple, Union

from ..format import Format, FormatError
from ..proxy import Proxy
from ..request import Request
from ..response import Response

IMMUTABLE_TYPES = (int, float, str, bytes, None)
ALLOWED_TYPES = Union[Dict, Tuple, int, float, str, bytes, None]
IMMUTABLE_TYPES_NAMES = (u"int", u"float", u"str", u"bytes", u"None")


class BasicFormat(Format[Dict[str, ALLOWED_TYPES]]):
    def translate_to_builtins(self, obj):
        # type: (Any) -> Dict[str, ALLOWED_TYPES]
        obj_type = type(obj)
        for t in IMMUTABLE_TYPES:
            if obj_type == t:
                return dict(t=str(t), v=obj)
        if obj_type == tuple:
            return dict(
                t=str(tuple), v=tuple(self.translate_to_builtins(v) for v in obj)
            )
        if obj_type == dict:
            return dict(
                t=str(dict),
                v={k: self.translate_to_builtins(v) for k, v in obj.items()},
            )
        if obj_type == Proxy:
            return dict(t=u"p", v=obj.__obj_id)
        if obj_type == Request:
            return dict(
                t=u"rq",
                v=dict(
                    request_type=obj.request_type.value,
                    obj_id=self.translate_to_builtins(obj.obj_id),
                    args=tuple(self.translate_to_builtins(v) for v in obj.args),
                    kwds={
                        k: self.translate_to_builtins(v) for k, v in obj.kwds.items()
                    },
                ),
            )
        if obj_type == Response:
            return dict(
                t="rp",
                v=dict(
                    request=self.translate_to_builtins(obj.request),
                    value=self.translate_to_builtins(obj.value),
                    error=self.translate_to_builtins(obj.error),
                ),
            )
        return dict(t=u"o", v=self.proxy_manager.save(obj))

    def translate_from_builtins(self, obj):
        # type: (Dict[str, ALLOWED_TYPES]) -> Union[ALLOWED_TYPES, Proxy, Response, Request]
        if not isinstance(obj, dict) or u"t" not in obj or u"v" not in obj:
            raise FormatError(
                u"Incorrect format passed. Expected dict with keys 't' and 'v'"
            )
        obj_type = obj[u"t"]
        obj_value = obj[u"v"]
        if obj_type in IMMUTABLE_TYPES_NAMES:
            return obj_value
        if obj_type == str(tuple) and isinstance(obj_value, tuple):
            return tuple(self.translate_from_builtins(v) for v in obj_value)
        if obj_type == str(dict) and isinstance(obj_value, dict):
            return {k: self.translate_from_builtins(v) for k, v in obj_value.items()}
        if obj_type == u"p" and isinstance(obj_value, int):
            return self.proxy_manager.get(obj_value)
        if obj_type == u"rq" and isinstance(obj_value, dict):
            obj_id = self.translate_from_builtins(obj_value[u"obj_id"])
            if obj_id is not None:
                assert isinstance(obj_id, int)  # Sanity check
            args = self.translate_from_builtins(obj_value[u"args"])
            if args is not None:
                assert isinstance(args, tuple)  # Sanity check
            return Request(
                request_type=Request.TYPE(obj_value[u"request_type"]),
                obj_id=obj_id,
                args=args,
                kwds={
                    k: self.translate_from_builtins(v)
                    for k, v in obj_value[u"kwds"].items()
                },
            )
        if obj_type == u"rp" and isinstance(obj_value, dict):
            request = self.translate_from_builtins(obj_value[u"request"])
            assert isinstance(request, Request)
            value = self.translate_from_builtins(obj_value[u"value"])
            error = self.translate_from_builtins(obj_value[u"error"])
            if error is not None:
                assert isinstance(error, Exception)
            return Response(
                request=request,
                value=value,
                error=error,
            )
        if obj_type == u"o" and isinstance(obj_value, int):
            return self.proxy_creation_func(obj_value)
        raise FormatError(u"Unknown type passed {}".format(str(obj_type)))
