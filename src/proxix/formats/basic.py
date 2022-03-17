from ..response import Response
from ..request import Request
from ..format import Format, FormatError
from ..proxy import Proxy
from typing import Dict, Tuple, Union, Any
from builtins import str, bytes


IMMUTABLE_TYPES =(int, float, str, bytes, None)
IMMUTABLE_TYPES_TYPE = Union[Tuple, int, float, str, bytes, None]
IMMUTABLE_TYPES_NAMES = (u"int", u"float", u"str", u"bytes", u"None")


class BasicFormat(Format):
    def translate_to_builtins(self, obj):
        # type: (Any) -> Dict[str, IMMUTABLE_TYPES_TYPE]
        obj_type = type(obj)
        for t in IMMUTABLE_TYPES:
            if obj_type == t:
                return dict(t=str(t), v=obj)
        if obj_type == tuple:
            return dict(t=str(tuple), v=tuple(self.translate_to_builtins(v) for v in obj))
        if obj_type == Proxy:
            return dict(t=u"p", v=obj.__obj_id)
        if obj_type == Request:
            return dict(t=u"rq", v=dict(
                request_type=obj.request_type.value,
                obj_id=self.translate_to_builtins(obj.obj_id),
                args=tuple(self.translate_to_builtins(v) for v in obj.args),
                kwds={k: self.translate_to_builtins(v) for k, v in obj.kwds.items()},
            ))
        if obj_type == Response:
            return dict(t="rp", v=dict(
                request=self.translate_to_builtins(obj.request),
                value=self.translate_to_builtins(obj.value),
                error=self.translate_to_builtins(obj.error),
            ))
        return dict(t=u"o", v=self.proxy_manager.save(obj))

    def translate_from_builtins(self, obj):
        # type: (Dict[str, IMMUTABLE_TYPES_TYPE]) -> Union[IMMUTABLE_TYPES_TYPE, Proxy]
        if not isinstance(obj, dict) or u"t" not in obj or u"v" not in obj:
            raise FormatError(u"Incorrect format passed. Expected dict with keys 't' and 'v'")
        obj_type = obj[u"t"]
        obj_value = obj[u"v"]
        if obj_type in IMMUTABLE_TYPES_NAMES:
            return obj_value
        if obj_type == str(tuple):
            return tuple(self.translate_from_builtins(v) for v in obj_value)
        if obj_type == u"p":
            return self.proxy_manager.get(obj_value)
        if obj_type == u"rq":
            return Request(
                request_type=Request.TYPE(obj_value[u"request_type"]),
                obj_id=self.translate_from_builtins(obj_value[u"obj_id"]),
                args=self.translate_from_builtins(obj_value[u"args"]),
                kwds={k: self.translate_from_builtins(v) for k, v in obj_value[u"kwds"].items()},
            )
        if obj_type == u"rp":
            return Response(
                request=self.translate_from_builtins(obj_value[u"request"]),
                value=self.translate_from_builtins(obj_value[u"value"]),
                error=self.translate_from_builtins(obj_value[u"error"]),
            )
        if obj_type == u"o":
            return self.proxy_creation_func(obj_value)
        raise FormatError(u"Unknown type passed {}".format(obj_type))
        
