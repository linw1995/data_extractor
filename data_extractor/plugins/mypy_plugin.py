# Standard Library
from typing import Callable, Dict, Optional, Type

# Third Party Library
from mypy.checker import TypeChecker
from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    IndexExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    TypeAlias,
    TypeInfo,
)
from mypy.nodes import Var as VarExpr
from mypy.plugin import (
    AttributeContext,
    FunctionContext,
    MethodContext,
    MethodSigContext,
    Plugin,
)
from mypy.traverser import TraverserVisitor
from mypy.types import AnyType, CallableType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, UninhabitedType, UnionType


class RelationshipVisitor(TraverserVisitor):
    def __init__(self) -> None:
        self.relationships: Dict[str, str] = {}

    def is_field_assignment_stmt(self, stmt: AssignmentStmt) -> bool:
        if not isinstance(stmt.rvalue, CallExpr):
            return False

        call_expr: CallExpr = stmt.rvalue
        callee_expr = call_expr.callee
        if isinstance(callee_expr, NameExpr):
            callee_node = callee_expr.node
            if (
                isinstance(callee_node, TypeInfo)
                and callee_node.fullname == "data_extractor.item.Field"
            ):
                return True
            elif (
                isinstance(callee_node, TypeAlias)
                and callee_node.target.type.fullname == "data_extractor.item.Field"
            ):
                return True
        elif (
            isinstance(callee_expr, IndexExpr)
            and callee_expr.base.node.fullname == "data_extractor.item.Field"
        ):
            return True

        return False

    def anal_assignment_stmt(self, stmt: AssignmentStmt) -> None:
        if self.is_field_assignment_stmt(stmt):
            rvalue_loc = str((stmt.rvalue.line, stmt.rvalue.column))
            for lvalue in stmt.lvalues:
                expr = lvalue.node
                if isinstance(expr, VarExpr):
                    lvalue_loc = str((expr.line, expr.column))
                    self.relationships[rvalue_loc] = lvalue_loc

    def visit_assignment_stmt(self, o: AssignmentStmt) -> None:
        self.anal_assignment_stmt(o)
        super().visit_assignment_stmt(o)


class ModificationVisitor(TraverserVisitor):
    def __init__(self, type_info: TypeInfo, attr_name: str):
        self.type_info = type_info
        self.attr_name = attr_name

    def visit_assignment_stmt(self, o):
        return super().visit_assignment_stmt(o)


class DataExtractorPlugin(Plugin):
    cache: Dict[str, Dict[str, str]] = {}

    def get_current_code(self, ctx: FunctionContext) -> MypyFile:
        return ctx.api.modules[ctx.api.tscope.module]

    def anal_code(self, code: MypyFile) -> Dict[str, str]:
        if code.fullname not in self.cache:
            visitor = RelationshipVisitor()
            code.accept(visitor)
            self.cache[code.fullname] = visitor.relationships

        return self.cache[code.fullname]

    def anal_is_many_modification(self, code: MypyFile, ctx: MemberExpr) -> bool:
        if code.fullname not in self.modifcation_anal_result:
            pass

    def check_field_generic_type(self, ctx: FunctionContext) -> MypyType:
        self.anal_code(self.get_current_code(ctx))
        rv_type = ctx.default_return_type
        if not isinstance(rv_type, Instance):
            return rv_type

        if rv_type.args and not isinstance(rv_type.args[0], UninhabitedType):
            return rv_type

        # # check parameter "type"
        # idx = ctx.callee_arg_names.index("type")
        # arg = ctx.args[type_idx]
        # if arg:
        #    args = [arg[0].node]
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

        relationship = self.anal_code(self.get_current_code(ctx))
        lvalue_key = str((expr.line, expr.column))
        if lvalue_key in relationship:
            key = relationship[lvalue_key]
        else:
            key = lvalue_key

        callee = expr.callee
        if isinstance(callee, IndexExpr):
            callee = callee.base
        assert isinstance(callee, NameExpr)

        sym_field_class = callee.node
        if isinstance(sym_field_class, TypeAlias):
            sym_field_class = sym_field_class.target.type
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
        origin: CallableType = ctx.default_signature
        origin_ret_type = origin.ret_type
        assert isinstance(origin_ret_type, UnionType)

        self_class = ctx.type
        assert isinstance(self_class, Instance)
        metadata = self_class.type.metadata

        # in case of stmt `Field().extract(...)`
        key = str((ctx.type.line, ctx.type.column))
        if key not in metadata:
            expr = ctx.context
            assert isinstance(expr, CallExpr)
            callee = expr.callee
            assert isinstance(callee, MemberExpr)
            name_expr = callee.expr
            assert isinstance(name_expr, NameExpr)
            obj = name_expr.node
            assert isinstance(obj, VarExpr)
            key = str((obj.line, obj.column))
            # metadata = obj.type.type.metadata

        if key in metadata:
            is_many = metadata[key]["is_many"]
            ret_type = origin_ret_type.items[int(is_many)]
            return origin.copy_modified(ret_type=ret_type)
        else:
            api = ctx.api
            assert isinstance(api, TypeChecker)
            api.fail("Cant determine extract method return type", context=ctx.context)
            return origin

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], CallableType]]:
        if fullname == "data_extractor.item.Field.extract":
            return self.apply_is_many_on_field_extract_method

        return super().get_method_signature_hook(fullname)

    def field_attribute_hook(self, ctx: AttributeContext) -> MypyType:
        if (
            isinstance(ctx.context, MemberExpr)
            and ctx.type.type.fullname == "data_extractor.item.Field"
            and ctx.context.name == "is_many"
        ):
            if self.anal_is_many_modification(self.get_current_code(ctx), ctx.context):
                print("modified")

            breakpoint()

        return ctx.default_attr_type

    def get_attribute_hook(
        self, fullname: str
    ) -> Optional[Callable[[AttributeContext], MypyType]]:
        if fullname == "data_extractor.item.Field.is_many":
            if ctx.api.tscope.module == "test_modify_is_many":
                return self.field_attribute_hook

        return super().get_attribute_hook(fullname)


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
