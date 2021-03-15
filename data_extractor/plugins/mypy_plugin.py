# Standard Library
from typing import Callable, Optional, Type

# Third Party Library
from mypy.nodes import CallExpr, IndexExpr, NameExpr, TypeInfo
from mypy.plugin import FunctionContext, MethodSigContext, Plugin
from mypy.types import AnyType, CallableType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, UninhabitedType, UnionType


class DataExtractorPlugin(Plugin):
    def check_field_generic_type(self, ctx: FunctionContext) -> MypyType:
        rv_type = ctx.default_return_type
        if not isinstance(rv_type, Instance):
            return rv_type

        if rv_type.args and not isinstance(rv_type.args[0], UninhabitedType):
            return rv_type

        # # check parameter "type"
        # type_idx = ctx.callee_arg_names.index("type")
        # type_arg = ctx.args[type_idx]
        # if type_arg:
        #    args = [type_arg[0].node]
        # else:
        if not self.options.disallow_any_generics:
            return self.apply_any_generic(type=rv_type)
        else:
            return rv_type

    def apply_any_generic(self, type: Instance) -> Instance:
        any_type = AnyType(TypeOfAny.special_form)
        args = [any_type]
        return type.copy_modified(args=args)

    def check_is_many(self, ctx: FunctionContext) -> bool:
        is_many_idx = ctx.callee_arg_names.index("is_many")
        is_many_exprs = ctx.args[is_many_idx]
        if is_many_exprs:
            is_many_expr = is_many_exprs[0]
            if isinstance(is_many_expr, NameExpr):
                if is_many_expr.fullname == "builtins.True":
                    return True

        return False

    def make_field_type_annotations(self, ctx: FunctionContext) -> MypyType:
        # check parameter "is_many"
        expr = ctx.context
        assert isinstance(expr, CallExpr)

        key = str((expr.line, expr.column))

        callee = expr.callee
        if isinstance(callee, IndexExpr):
            callee = callee.base
        assert isinstance(callee, NameExpr)

        sym_field_class = callee.node
        assert isinstance(sym_field_class, TypeInfo)
        if self.check_is_many(ctx):
            sym_field_class.metadata[key] = {"is_many": True}
        else:
            sym_field_class.metadata[key] = {"is_many": False}

        rv_type = self.check_field_generic_type(ctx)
        return rv_type

    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], MypyType]]:
        if fullname == "data_extractor.item.Field":
            return self.make_field_type_annotations

        return super().get_function_hook(fullname)

    def apply_is_many_on_field_extract_method(
        self, ctx: MethodSigContext
    ) -> CallableType:
        key = str((ctx.type.line, ctx.type.column))
        origin: CallableType = ctx.default_signature
        origin_ret_type = origin.ret_type
        assert isinstance(origin_ret_type, UnionType)

        self_class = ctx.type
        assert isinstance(self_class, Instance)
        ret_type = origin_ret_type.items[int(self_class.type.metadata[key]["is_many"])]
        return origin.copy_modified(ret_type=ret_type)

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], CallableType]]:
        if fullname == "data_extractor.item.Field.extract":
            return self.apply_is_many_on_field_extract_method

        return super().get_method_signature_hook(fullname)


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
