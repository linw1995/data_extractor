# Standard Library
import logging

from functools import partial
from typing import Callable, Dict, List, Optional, Type

# Third Party Library
from mypy.checker import TypeChecker
from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    IndexExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    SymbolNode,
    TypeAlias,
    TypeInfo,
)
from mypy.nodes import Var as VarExpr
from mypy.options import Options
from mypy.plugin import (
    DynamicClassDefContext,
    FunctionContext,
    MethodSigContext,
    Plugin,
)
from mypy.semanal import SemanticAnalyzerInterface
from mypy.semanal_typeddict import TypedDictAnalyzer
from mypy.traverser import TraverserVisitor
from mypy.types import AnyType, CallableType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypedDictType, TypeOfAny, UninhabitedType, UnionType

logger = logging.getLogger(__name__)


class RelationshipVisitor(TraverserVisitor):
    def __init__(self) -> None:
        self.relationships: Dict[str, str] = {}

    def is_data_extractor_cls(self, obj: Optional[SymbolNode]) -> bool:
        return obj is not None and obj.fullname in (
            "data_extractor.item.Field",
            "data_extractor.item.Item",
        )

    def is_field_assignment_stmt(self, stmt: AssignmentStmt) -> bool:
        if not isinstance(stmt.rvalue, CallExpr):
            return False

        call_expr: CallExpr = stmt.rvalue
        callee_expr = call_expr.callee
        if isinstance(callee_expr, NameExpr):
            callee_node = callee_expr.node
            if isinstance(callee_node, TypeInfo):
                if self.is_data_extractor_cls(callee_node):
                    return True
            elif isinstance(callee_node, TypeAlias):
                target = callee_node.target
                if isinstance(target, Instance):
                    if self.is_data_extractor_cls(target.type):
                        return True
        elif isinstance(callee_expr, IndexExpr):
            base = callee_expr.base
            if isinstance(base, NameExpr):
                if self.is_data_extractor_cls(base.node):
                    return True
        return False

    def anal_assignment_stmt(self, stmt: AssignmentStmt) -> None:
        if self.is_field_assignment_stmt(stmt):
            rvalue_loc = str((stmt.rvalue.line, stmt.rvalue.column))
            for lvalue in stmt.lvalues:
                if not isinstance(lvalue, NameExpr):
                    continue
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
    cache: Dict[str, Dict[str, str]]
    item_typeddict_mapping: Dict[str, TypedDictType]

    def __init__(self, options: Options) -> None:
        super().__init__(options)
        self.cache = {}
        self.item_typeddict_mapping = {}

    def get_current_code(self, ctx: FunctionContext) -> MypyFile:
        api = ctx.api
        assert isinstance(api, TypeChecker)
        module_name = api.tscope.module
        assert module_name is not None
        return api.modules[module_name]

    def anal_code(self, code: MypyFile) -> Dict[str, str]:
        if code.fullname not in self.cache:
            try:
                visitor = RelationshipVisitor()
            except TypeError:
                # Only supports versions that are bigger than 0.820
                return {}

            code.accept(visitor)
            self.cache[code.fullname] = visitor.relationships

        return self.cache[code.fullname]

    def check_field_generic_type(self, ctx: FunctionContext) -> MypyType:
        self.anal_code(self.get_current_code(ctx))
        rv_type = ctx.default_return_type
        if not isinstance(rv_type, Instance):
            return rv_type

        if rv_type.args and not isinstance(rv_type.args[0], UninhabitedType):
            return rv_type

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

    def prepare_type_annotations(self, ctx: FunctionContext, fullname: str) -> MypyType:
        logger.debug("prepare_type_annotations %r", fullname)

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
            target = sym_field_class.target
            assert isinstance(target, Instance)
            sym_field_class = target.type
        assert isinstance(sym_field_class, TypeInfo)

        if self.check_is_many(ctx):
            sym_field_class.metadata[key] = {"is_many": True}
        else:
            sym_field_class.metadata[key] = {"is_many": False}

        rv_type = self.check_field_generic_type(ctx)
        return rv_type

    def is_extractor_cls(self, fullname: str, is_item_subcls=False) -> bool:
        node = self.lookup_fully_qualified(fullname)
        if node is not None:
            typenode = node.node
            if isinstance(typenode, TypeInfo):
                if is_item_subcls:
                    return typenode.has_base("data_extractor.item.Item")
                else:
                    return typenode.has_base("data_extractor.item.Field")

        return False

    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], MypyType]]:
        logger.debug("get_function_hook %r", fullname)
        if self.is_extractor_cls(fullname):
            return partial(self.prepare_type_annotations, fullname=fullname)

        return super().get_function_hook(fullname)

    def apply_is_many_on_extract_method(
        self, ctx: MethodSigContext, fullname: str
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

        logger.debug("apply_is_many %r %r %r", fullname, key, metadata)
        if key in metadata:
            is_many = metadata[key]["is_many"]
            ret_type = origin_ret_type.items[int(is_many)]
            return origin.copy_modified(ret_type=ret_type)
        else:
            api = ctx.api
            assert isinstance(api, TypeChecker)
            api.fail("Cant determine extract method return type", context=ctx.context)
            return origin

    def is_extract_method(self, fullname: str) -> bool:
        suffix = ".extract"
        if fullname.endswith(suffix):
            return self.is_extractor_cls(fullname[: -len(suffix)])
        return False

    def apply_extract_method(
        self, ctx: MethodSigContext, fullname: str
    ) -> CallableType:
        rv = self.apply_is_many_on_extract_method(ctx, fullname)

        # apply item typeddict
        item_classname = fullname[: -len(".extract")]
        if item_classname in self.item_typeddict_mapping:
            logger.debug("apply_extract_method %r %r", fullname, rv.ret_type)
            original = rv.ret_type
            typeddict = self.item_typeddict_mapping[item_classname]
            ret_type: Optional[MypyType]
            if isinstance(original, AnyType):
                ret_type = typeddict
            else:
                assert isinstance(original, Instance)
                if original.type.name == "list":
                    ret_type = original
                    ret_type.args = (typeddict,)
                else:
                    api = ctx.api
                    assert isinstance(api, TypeChecker)
                    api.fail(
                        "Cant determine extract method return type", context=ctx.context
                    )
                    ret_type = None

            if ret_type is not None:
                rv = rv.copy_modified(ret_type=ret_type)

        logger.debug(
            "apply_extract_method %r %r %r", fullname, rv, self.item_typeddict_mapping
        )
        return rv

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], CallableType]]:
        if self.is_extract_method(fullname):
            return partial(self.apply_extract_method, fullname=fullname)
        return super().get_method_signature_hook(fullname)

    def prepare_typeddict(self, ctx: DynamicClassDefContext, fullname: str) -> None:
        logger.debug("prepare_typeddict %r", fullname)
        if fullname in self.item_typeddict_mapping:
            return

        api = ctx.api
        assert isinstance(api, SemanticAnalyzerInterface)
        analyzer = TypedDictAnalyzer(api.options, api, api.msg)  # type: ignore

        items: List[str] = []
        types: List[MypyType] = []
        callee = ctx.call.callee
        assert isinstance(callee, NameExpr)
        node = callee.node
        assert isinstance(node, TypeInfo)
        for block in node.defn.defs.body:
            if not isinstance(block, AssignmentStmt):
                continue

            rvalue = block.rvalue
            if not isinstance(rvalue, CallExpr):
                continue

            rvalue_type: MypyType
            callee = rvalue.callee
            if isinstance(callee, IndexExpr):
                index = callee.index
                assert isinstance(index, NameExpr)
                name = index.fullname
                assert name is not None
                named_type = api.named_type_or_none(name, [])
                assert named_type is not None
                rvalue_type = named_type
            else:
                rvalue_type = AnyType(TypeOfAny.special_form)

            for lvalue in block.lvalues:
                assert isinstance(lvalue, NameExpr)
                items.append(lvalue.name)
                types.append(rvalue_type)

        callee = ctx.call.callee
        assert isinstance(callee, NameExpr)
        typeinfo = analyzer.build_typeddict_typeinfo(
            callee.name, items, types, set(items), -1
        )
        assert typeinfo.typeddict_type is not None
        self.item_typeddict_mapping[fullname] = typeinfo.typeddict_type
        logger.debug("prepare_typeddict %r %r", fullname, self.item_typeddict_mapping)

    def get_dynamic_class_hook(
        self, fullname: str
    ) -> Optional[Callable[[DynamicClassDefContext], None]]:
        logger.debug("dynamic_class_hook %r", fullname)
        if self.options.python_version >= (3, 8):
            if self.is_extractor_cls(fullname, is_item_subcls=True):
                return partial(self.prepare_typeddict, fullname=fullname)

        return super().get_dynamic_class_hook(fullname)


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
