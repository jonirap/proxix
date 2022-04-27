import importlib
import sys
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping, NamedTuple

from .proxy import ExceptionProxy, Proxy

BrokenDownClass = NamedTuple(
    "BrokenDownClass",
    [
        ("name", str),
        ("module", str),
        ("bases", Iterable["BrokenDownClass"]),  # type: ignore
        ("extra_dir", Iterable[str]),
    ],
)


def _extra_dir_generator(func_name):
    # type: (str) -> Callable[[Proxy, Iterable[Any], Mapping[str, Any]], Any]
    def _random(self, *args, **kwds):
        # type: (Proxy, Iterable[Any], Mapping[str, Any]) -> Any
        return getattr(self, func_name)(*args, **kwds)

    _random.__name__ = func_name
    return _random


class GeneratedManager(object):
    def __init__(self, module_prefix=u"remote"):
        # type: (str) -> None
        self._module_prefix = module_prefix

    def generate(self, cls):
        # type: (BrokenDownClass) -> type
        try:
            module = importlib.import_module(
                u"{}.{}".format(self._module_prefix, cls.module)
            )
            imported_class = getattr(module, cls.name)  # type: type
            return imported_class
        except (ImportError, AttributeError):
            is_exception = any(b.name == "BaseException" for b in cls.bases)
            bases = [self.generate(b) for b in cls.bases if b.name != "BaseException"]
            if not is_exception:
                is_exception = any(issubclass(b, ExceptionProxy) for b in bases)
            if not any(issubclass(b, Proxy) for b in bases):
                bases.insert(0, ExceptionProxy if is_exception else Proxy)
            created_class = type(
                cls.name,
                tuple(bases),
                {name: _extra_dir_generator(name) for name in cls.extra_dir},
            )  # type: type
            base_module_name = cls.module.split(u".")[-1]
            module = ModuleType(base_module_name)
            sys.modules["{}.{}".format(self._module_prefix, cls.module)] = module
            setattr(module, cls.name, created_class)
            return created_class
