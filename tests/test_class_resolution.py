from parametrization import Parametrization

from proxix.class_resolution import CLASS_HIERARCHY_TYPE, resolve_hierarchy


class A0(object):
    pass


class A1(object):
    pass


class B0A0(A0):
    pass


class B1A01(A0, A1):
    pass


class C0B0A0A1(B0A0, A1):
    pass


class SomeException(Exception):
    pass


@Parametrization.parameters("original_class", "result_dict")  # type: ignore
@Parametrization.case("Direct object", original_class=A0, result_dict={object: {}})  # type: ignore
@Parametrization.case("Single object inheritance", original_class=B0A0, result_dict={A0: {object: {}}})  # type: ignore
@Parametrization.case("Dual object inheritance", original_class=B1A01, result_dict={A1: {object: {}}, A0: {object: {}}})  # type: ignore
@Parametrization.case("Two layer inheritance", original_class=C0B0A0A1, result_dict={A1: {object: {}}, B0A0: {A0: {object: {}}}})  # type: ignore
@Parametrization.case("Exception object", original_class=SomeException, result_dict={Exception: {BaseException: {object: {}}}})  # type: ignore
def test_resolve_hierarchy_correct(original_class, result_dict):
    # type: (type, CLASS_HIERARCHY_TYPE) -> None
    assert resolve_hierarchy(original_class) == result_dict
