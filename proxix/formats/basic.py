from builtins import bytes, str
from types import MappingProxyType
from typing import Any, Dict, List, Tuple, Union

from ..class_resolution import CLASS_HIERARCHY_TYPE, resolve_hierarchy
from ..format import Format, FormatError
from ..generated_manager import BrokenDownClass
from ..proxy import Proxy
from ..request import Request
from ..response import RemoteException, Response

NoneType = type(None)
IMMUTABLE_TYPES = (bool, int, float, str, bytes, NoneType)
ALLOWED_TYPES = Union[Dict, Tuple["ALLOWED_TYPES", ...], bool, int, float, str, bytes, None, NoneType]  # type: ignore
IMMUTABLE_TYPES_NAMES = tuple(t.__name__ for t in IMMUTABLE_TYPES)  # type: ignore


class DummyClass(object):
    pass


TRANSLATED_HIERARCHY_TYPE = Dict[str, Union[str, List[str], List["TRANSLATED_HIERARCHY_TYPE"]]]  # type: ignore


def _translate_resolved_class(cls, resolved):
    # type: (type, CLASS_HIERARCHY_TYPE) -> TRANSLATED_HIERARCHY_TYPE
    return dict(
        m=cls.__module__,
        n=cls.__name__,
        d=list(set(dir(cls)) - set(dir(DummyClass))),
        b=[
            _translate_resolved_class(k, v)
            for k, v in resolved.items()
            if k is not object
        ],
    )


def _translated_to_broken_down_class(obj_value):
    # type: (TRANSLATED_HIERARCHY_TYPE) -> BrokenDownClass
    return BrokenDownClass(
        name=obj_value[u"n"],  # type: ignore
        module=obj_value["m"],  # type: ignore
        extra_dir=obj_value["d"],  # type: ignore
        bases=[_translated_to_broken_down_class(b) for b in obj_value["b"]],  # type: ignore
    )


class BasicFormat(Format[Dict[str, ALLOWED_TYPES]]):
    def translate_to_builtins(self, obj):
        # type: (Any) -> Dict[str, ALLOWED_TYPES]
        if isinstance(obj, type):
            return dict(
                t=type.__name__,
                v=_translate_resolved_class(obj, resolve_hierarchy(obj)),
            )
        obj_type = type(obj)
        for t in IMMUTABLE_TYPES:
            if obj_type == t:
                return dict(t=obj_type.__name__, v=obj)
        if obj_type == tuple:
            return dict(
                t=tuple.__name__, v=tuple(self.translate_to_builtins(v) for v in obj)
            )
        if obj_type == dict:
            return dict(
                t=dict.__name__,
                v={k: self.translate_to_builtins(v) for k, v in obj.items()},
            )
        if obj_type == MappingProxyType:
            return dict(
                t=MappingProxyType.__name__,
                v={k: self.translate_to_builtins(v) for k, v in obj.items()},
            )
        if isinstance(obj_type, Proxy):
            return dict(t=u"p", v=obj.__obj_id)
        if obj_type == Request:
            return dict(
                t=u"rq",
                v=dict(
                    request_type=obj.request_type.value,
                    obj_id=self.translate_to_builtins(obj.obj_id),
                    args=tuple(self.translate_to_builtins(v) for v in obj.args or ()),
                    kwds={
                        k: self.translate_to_builtins(v)
                        for k, v in (obj.kwds or {}).items()
                    },
                ),
            )
        if obj_type == RemoteException:
            return dict(
                t=u"re",
                v=dict(
                    sys_exc_info=self.translate_to_builtins(obj.sys_exc_info),
                    formatted_traceback=self.translate_to_builtins(obj.args[0]),
                ),
            )
        if obj_type == Response:
            return dict(
                t=u"rp",
                v=dict(
                    request=self.translate_to_builtins(obj.request),
                    value=self.translate_to_builtins(obj.value),
                    remote_exception=self.translate_to_builtins(obj.remote_exception),
                ),
            )
        return dict(
            t=u"o",
            v=dict(
                i=self.proxy_manager.save(obj),
                c=self.translate_to_builtins(obj_type),
            ),
        )

    def translate_from_builtins(self, obj):
        # type: (Dict[str, ALLOWED_TYPES]) -> Union[ALLOWED_TYPES, Proxy, Response, Request, Any]
        if not isinstance(obj, dict) or u"t" not in obj or u"v" not in obj:
            raise FormatError(
                u"Incorrect format passed with {}. Expected dict with keys 't' and 'v'".format(
                    obj
                )
            )
        obj_type = obj[u"t"]
        obj_value = obj[u"v"]
        if obj_type == type.__name__:
            return self.generated_manager.generate(_translated_to_broken_down_class(obj_value=obj_value))  # type: ignore
        if obj_type in IMMUTABLE_TYPES_NAMES:
            return obj_value
        if obj_type == tuple.__name__ and hasattr(obj_value, u"__iter__"):
            return tuple(self.translate_from_builtins(v) for v in obj_value)  # type: ignore
        if obj_type == dict.__name__ and hasattr(obj_value, u"items"):
            return {k: self.translate_from_builtins(v) for k, v in obj_value.items()}  # type: ignore
        if obj_type == MappingProxyType.__name__ and hasattr(obj_value, u"items"):
            return {k: self.translate_from_builtins(v) for k, v in obj_value.items()}  # type: ignore
        if obj_type == u"p" and isinstance(obj_value, int):
            return self.proxy_manager.get(obj_value)
        if obj_type == u"rq" and isinstance(obj_value, dict):
            obj_id = self.translate_from_builtins(obj_value[u"obj_id"])
            if obj_id is not None:
                assert isinstance(obj_id, int)  # Sanity check
            args = tuple(
                self.translate_from_builtins(v) for v in (obj_value[u"args"] or ())
            )
            return Request(
                request_type=Request.TYPE(obj_value[u"request_type"]),
                obj_id=obj_id,
                args=args,
                kwds={
                    k: self.translate_from_builtins(v)
                    for k, v in obj_value[u"kwds"].items()
                },
            )
        if obj_type == u"re" and isinstance(obj_value, dict):
            sys_exc_info = self.translate_from_builtins(obj_value[u"sys_exc_info"])
            formatted_traceback = self.translate_from_builtins(
                obj_value[u"formatted_traceback"]
            )
            return RemoteException(formatted_traceback, sys_exc_info=sys_exc_info)  # type: ignore
        if obj_type == u"rp" and isinstance(obj_value, dict):
            request = self.translate_from_builtins(obj_value[u"request"])
            assert isinstance(request, Request)
            value = self.translate_from_builtins(obj_value[u"value"])
            remote_exception = self.translate_from_builtins(
                obj_value[u"remote_exception"]
            )
            assert isinstance(remote_exception, (type(None), RemoteException))
            return Response(
                request=request,
                value=value,
                remote_exception=remote_exception,
            )
        if obj_type == u"o":
            return self.translate_from_builtins(obj_value[u"c"])(  # type: ignore
                dispatcher=self.dispatcher,
                obj_id=obj_value[u"i"],  # type: ignore
            )
        raise FormatError(u"Unknown type passed {}".format(str(obj_type)))
