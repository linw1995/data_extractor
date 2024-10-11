# Standard Library
import logging

from functools import partial
from typing import Callable, Dict, List, Optional, Type, Union

# Third Party Library
from mypy.checker import TypeChecker, is_true_literal
from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    ClassDef,
    Expression,
    IndexExpr,
    MemberExpr,
    MypyFile,
    NameExpr,
    RefExpr,
    StrExpr,
    SymbolNode,
    TypeAlias,
    TypeInfo,
    Var,
)
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
from mypy.types import AnyType, CallableType, FunctionLike, Instance
from mypy.types import Type as MypyType
from mypy.types import TypedDictType, TypeOfAny, TypeType, UninhabitedType, UnionType

logger = logging.getLogger(__name__)


class RelationshipVisitor(TraverserVisitor):
    relationships: Dict[str, List[str]]

    def __init__(self) -> None:
        self.relationships = {}

    def is_data_extractor_cls(self, obj: Optional[SymbolNode]) -> bool:
        return obj is not None and obj.fullname in (
            "data_extractor.item.Field",
            "data_extractor.item.Item",
        )

    def is_making_extractor_assignment_stmt(self, stmt: AssignmentStmt) -> bool:
        rvalue = stmt.rvalue
        if not isinstance(rvalue, CallExpr):
            return False

        node: Union[Expression, SymbolNode, MypyType] = rvalue.callee
        if isinstance(node, IndexExpr):
            logger.debug("node=%s", node)
            base = node.base
            assert base is not None
            node = base

        assert isinstance(node, RefExpr)
        logger.debug("node=%s", node)
        node_ = node.node
        if node_ is None:
            return False
        node = node_

        logger.debug("node=%r", node)
        if isinstance(node, Var):
            tt = node.type
            logger.debug("tt=%s", tt)
            if not isinstance(tt, TypeType):
                return False
            node = tt.item

        logger.debug("node=%r", node)
        if isinstance(node, TypeAlias):
            node = node.target

        logger.debug("node=%r", node)
        if isinstance(node, Instance):
            return node.type.has_base("data_extractor.item.Field")

        logger.debug("node=%r", node)
        if isinstance(node, TypeInfo):
            return self.is_data_extractor_cls(node)

        return False

    def locate_field_in_classdef(self, defn: ClassDef, name: str) -> str:
        for block in defn.defs.body:
            if not isinstance(block, AssignmentStmt):
                continue

            for lvalue in block.lvalues:
                assert isinstance(lvalue, NameExpr)
                if lvalue.name == name:
                    assert block.type is not None
                    return str((block.type.line, block.type.column))
        else:  # pragma: no cover
            raise ValueError(f"Field name = {name!r} not exists in defn = {defn!s}")

    def anal_assignment_stmt(self, stmt: AssignmentStmt) -> None:
        logger.debug("stmt=%s", stmt)
        if self.is_making_extractor_assignment_stmt(stmt):
            rvalue_loc = str((stmt.rvalue.line, stmt.rvalue.column))
            logger.debug("stmt=%s, rloc=%r", stmt, rvalue_loc)
            for lvalue in stmt.lvalues:
                lvalue_loc = ""
                logger.debug(f"lvalue = {lvalue!s}")
                assert isinstance(lvalue, RefExpr)
                if isinstance(lvalue, MemberExpr):
                    expr = lvalue.expr
                    assert isinstance(expr, NameExpr)
                    node = expr.node
                    if node is None:
                        return
                    assert isinstance(node, TypeInfo)
                    lvalue_loc = self.locate_field_in_classdef(node.defn, lvalue.name)
                elif isinstance(lvalue, NameExpr):
                    node = lvalue.node
                    assert isinstance(node, SymbolNode)
                    lvalue_loc = str((node.line, node.column))

                if not lvalue_loc:  # pragma: no cover
                    logger.debug(f"n = {node!s}, stmt = {stmt!s}")
                    continue

                self.relationships.setdefault(rvalue_loc, []).append(lvalue_loc)

    def visit_assignment_stmt(self, o: AssignmentStmt) -> None:
        self.anal_assignment_stmt(o)
        super().visit_assignment_stmt(o)


class DataExtractorPlugin(Plugin):
    cache: Dict[str, Dict[str, List[str]]]
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

    def anal_code(self, code: MypyFile) -> Dict[str, List[str]]:
        logger.debug(f"code.fullname = {code.fullname!r}, self.cache = {self.cache!r}")
        if code.fullname not in self.cache:
            try:
                visitor = RelationshipVisitor()
            except TypeError:  # pragma: no cover
                # Only supports versions that are bigger than 0.820
                return {}

            code.accept(visitor)
            self.cache[code.fullname] = visitor.relationships

        return self.cache[code.fullname]

    def check_field_generic_type(self, ctx: FunctionContext) -> MypyType:
        rv_type = ctx.default_return_type
        if self.options.disallow_any_generics:
            return rv_type

        self.anal_code(self.get_current_code(ctx))

        assert isinstance(rv_type, Instance)
        if rv_type.args and not isinstance(rv_type.args[0], UninhabitedType):
            return rv_type

        return self.apply_any_generic(type=rv_type)

    def apply_any_generic(self, type: Instance) -> Instance:
        any_type = AnyType(TypeOfAny.special_form)
        args = [any_type]
        return type.copy_modified(args=args)

    def check_is_many(self, ctx: FunctionContext) -> bool:
        is_many_idx = ctx.callee_arg_names.index("is_many")
        is_many_exprs = ctx.args[is_many_idx]
        if is_many_exprs:
            return is_true_literal(is_many_exprs[0])

        return False

    def prepare_type_annotations(self, ctx: FunctionContext, fullname: str) -> MypyType:
        logger.debug("fullname=%r", fullname)

        # check parameter "is_many"
        expr = ctx.context
        assert isinstance(expr, CallExpr)

        callee = expr.callee
        if isinstance(callee, IndexExpr):
            callee = callee.base
        assert isinstance(callee, NameExpr)

        sym_field_class: Union[MypyType, SymbolNode, None] = callee.node
        if isinstance(sym_field_class, TypeAlias):
            sym_field_class = sym_field_class.target
        elif isinstance(sym_field_class, Var):
            typetype = sym_field_class.type
            assert isinstance(typetype, TypeType)
            sym_field_class = typetype.item

        if isinstance(sym_field_class, Instance):
            sym_field_class = sym_field_class.type

        assert isinstance(sym_field_class, TypeInfo)
        relationship = self.anal_code(self.get_current_code(ctx))
        lvalue_key = str((expr.line, expr.column))
        keys = [lvalue_key]
        if lvalue_key in relationship:
            keys.extend(relationship[lvalue_key])

        for key in keys:
            logger.debug(
                f"lvalue_key = {lvalue_key!r}, "
                f"key = {key!r}, relationship = {relationship!r}"
            )

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
        logger.debug("fullname=%r", fullname)
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
            callee_expr = callee.expr
            assert isinstance(callee_expr, NameExpr)
            obj = callee_expr.node
            assert isinstance(obj, Var)
            key = str((obj.line, obj.column))

        logger.debug("fullname=%r, key=%r, metadata=%r", fullname, key, metadata)
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
            logger.debug("fullname=%r, ret_type=%r", fullname, rv.ret_type)
            original = rv.ret_type
            typeddict = self.item_typeddict_mapping[item_classname]
            ret_type: Optional[MypyType]
            if isinstance(original, AnyType):  # is_many=False
                rv = rv.copy_modified(ret_type=typeddict)
            else:
                assert isinstance(original, Instance)
                if original.type.name == "list":  # is_many=True
                    ret_type = original
                    ret_type.args = (typeddict,)
                    rv = rv.copy_modified(ret_type=ret_type)
                else:  # pragma: no cover
                    api = ctx.api
                    assert isinstance(api, TypeChecker)
                    api.fail(
                        "Cant determine extract method return type", context=ctx.context
                    )
                    ret_type = None

        logger.debug(
            "fullname=%r, rv=%r, item_typeddict_mapping=%r",
            fullname,
            rv,
            self.item_typeddict_mapping,
        )
        return rv

    def get_method_signature_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodSigContext], FunctionLike]]:
        if self.is_extract_method(fullname):
            return partial(self.apply_extract_method, fullname=fullname)
        return super().get_method_signature_hook(fullname)

    def get_name_arg(self, call: CallExpr) -> str:
        name = ""
        try:
            idx = call.arg_names.index("name")
            arg = call.args[idx]
            assert isinstance(arg, StrExpr)
            name = arg.value
        except ValueError:
            pass
        return name

    def prepare_typeddict(self, ctx: DynamicClassDefContext, fullname: str) -> None:
        logger.debug("fullname=%r", fullname)
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

            param_name = self.get_name_arg(rvalue)
            logger.debug("param_name = %r from rvalue = %s", param_name, rvalue)

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

            if param_name:
                items.append(param_name)
                types.append(rvalue_type)
            else:
                for lvalue in block.lvalues:
                    assert isinstance(lvalue, NameExpr)
                    items.append(lvalue.name)
                    types.append(rvalue_type)

        callee = ctx.call.callee
        assert isinstance(callee, NameExpr)
        typeinfo = analyzer.build_typeddict_typeinfo(
            callee.name,
            items,
            types,
            set(items),
            -1,
            None,
        )
        assert typeinfo.typeddict_type is not None
        self.item_typeddict_mapping[fullname] = typeinfo.typeddict_type
        logger.debug(
            "fullname=%r, item_typeddict_mapping=%r",
            fullname,
            self.item_typeddict_mapping,
        )

    def get_dynamic_class_hook(
        self, fullname: str
    ) -> Optional[Callable[[DynamicClassDefContext], None]]:
        logger.debug("fullname=%r", fullname)
        if self.is_extractor_cls(fullname, is_item_subcls=True):
            return partial(self.prepare_typeddict, fullname=fullname)

        return super().get_dynamic_class_hook(fullname)


def plugin(version: str) -> Type[Plugin]:
    return DataExtractorPlugin
