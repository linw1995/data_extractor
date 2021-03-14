# Standard Library
from typing import Callable, Optional, Type

# Third Party Library
from mypy.plugin import FunctionContext, Plugin
from mypy.types import AnyType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, UninhabitedType


class DataExtractorPlugin(Plugin):
    def apply_any_generic(self, ctx: FunctionContext) -> MypyType:
        rv_type = ctx.default_return_type
        if not isinstance(rv_type, Instance):
            return rv_type

        if rv_type.args and not isinstance(rv_type.args[0], UninhabitedType):
            return rv_type

        any_type = AnyType(TypeOfAny.special_form)
        rv_type = rv_type.copy_modified(args=[any_type])
        return rv_type

    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], MypyType]]:
        if not self.options.disallow_any_generics:
            if fullname == "data_extractor.item.Field":
                return self.apply_any_generic

        return super().get_function_hook(fullname)


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
