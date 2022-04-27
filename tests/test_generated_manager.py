import importlib

from parametrization import Parametrization

from proxix.generated_manager import BrokenDownClass, GeneratedManager


@Parametrization.parameters("broken_class")  # type: ignore
@Parametrization.case(  # type: ignore
    "Basic",
    broken_class=BrokenDownClass(
        name="Name", module="module_name", bases=[], extra_dir=[]
    ),
)
@Parametrization.case(  # type: ignore
    "1 base",
    broken_class=BrokenDownClass(
        name="Name",
        module="module_name",
        bases=[
            BrokenDownClass(name="Name2", module="new_module", bases=[], extra_dir=[])
        ],
        extra_dir=[],
    ),
)
@Parametrization.parameters("prefix")  # type: ignore
@Parametrization.case("Normal Prefix", prefix="normal")  # type: ignore
@Parametrization.case("Numbered Prefix", prefix="a3")  # type: ignore
def test_resolve_hierarchy_correct(broken_class, prefix):
    # type: (BrokenDownClass, str) -> None
    cls = GeneratedManager(module_prefix=prefix).generate(broken_class)
    assert cls.__name__ == broken_class.name
    assert (
        getattr(
            importlib.import_module("{}.{}".format(prefix, broken_class.module)),
            broken_class.name,
        )
        is cls
    )
    mro_names = [b.__name__ for b in cls.mro()]
    assert all(b.name in mro_names for b in broken_class.bases)
    assert all(hasattr(cls, fname) for fname in broken_class.extra_dir)
