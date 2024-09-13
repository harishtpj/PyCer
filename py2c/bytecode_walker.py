import ast
from typing import Optional

from py2c.exceptions import InvalidAnnotationException, NoneIsNotAllowedException, SourceCodeException
from py2c.translator_c import TranslatorC



def convert_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Add):
        return '+'
    elif isinstance(node, ast.Sub):
        return '-'
    elif isinstance(node, ast.Mult):
        return '*'
    elif isinstance(node, ast.Div):
        return '/'
    elif isinstance(node, ast.FloorDiv):
        return '//'
    elif isinstance(node, ast.Mod):
        return '%'
    elif isinstance(node, ast.Pow):
        return '**'
    elif isinstance(node, ast.RShift):
        return '>>'
    elif isinstance(node, ast.LShift):
        return '<<'
    elif isinstance(node, ast.BitOr):
        return '|'
    elif isinstance(node, ast.BitXor):
        return '^'
    elif isinstance(node, ast.BitAnd):
        return '&'
    # elif isinstance(node, ast.MatMult):
    #    return ''
    else:
        raise SourceCodeException('unknown node operator', node)


def convert_compare_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Gt):
        return '>'
    elif isinstance(node, ast.GtE):
        return '>='
    elif isinstance(node, ast.Lt):
        return '<'
    elif isinstance(node, ast.LtE):
        return '<='
    elif isinstance(node, ast.Eq):
        return '=='
    elif isinstance(node, ast.NotEq):
        return '!='
    # elif isinstance(node, ast.Is):
    #    return ''
    # elif isinstance(node, ast.IsNot):
    #    return ''
    # elif isinstance(node, ast.In):
    #    return ''
    # elif isinstance(node, ast.NotIn):
    #    return ''
    else:
        raise SourceCodeException('unknown node compare operator', node)


def convert_bool_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Or):
        return '||'
    elif isinstance(node, ast.And):
        return '&&'
    else:
        raise SourceCodeException('unknown node bool operator', node)


def convert_unary_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.UAdd):
        return '+'
    elif isinstance(node, ast.USub):
        return '-'
    elif isinstance(node, ast.Not):
        return '!'
    elif isinstance(node, ast.Invert):
        return '~'
    else:
        raise SourceCodeException('unknown node unary operator', node)


def convert_annotation(annotation_node, parent_node) -> Optional[str]:
    # Commented out, as variables can be declared in C libraries.
    # if not allow_absent and annotation_node is None:
    #     raise SourceCodeException('annotation must be!', parent_node)
    if annotation_node is None:
        return

    try:
        annotation_node.id = annotation_node.id.replace("str", "string")
    except:
        pass

    annotation_node.custom_ignore = True
    if isinstance(annotation_node, ast.Name):
        return annotation_node.id
    elif isinstance(annotation_node, ast.Constant):
        if annotation_node.value is None:
            raise NoneIsNotAllowedException('None is forbidden', parent_node)

        return annotation_node.value
    elif isinstance(annotation_node, ast.Num):
        return annotation_node.n
    elif isinstance(annotation_node, ast.Str):
        return annotation_node.s
    elif isinstance(annotation_node, ast.NameConstant):  # Python 3.4 - 3.8
        if annotation_node.value is None:
            raise NoneIsNotAllowedException('None is forbidden', parent_node)

        return convert_annotation(annotation_node.value, parent_node)

    raise InvalidAnnotationException('unknown annotation node', annotation_node)


def walk(converter, node):
    if node is None or getattr(node, 'custom_ignore', False):
        return

    parents = converter.transit_data.setdefault('parents', [])
    parent_node = parents[-1] if parents else None
    parents.append(node)

    has_while_orelse = converter.transit_data.setdefault('has_while_orelse', [])

    converter.lineno = node.lineno if hasattr(node, 'lineno') else converter.lineno
    converter.col_offset = node.col_offset if hasattr(node, 'col_offset') else converter.col_offset
    node.lineno = converter.lineno
    node.col_offset = converter.col_offset

    node.custom_ignore = True
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.value, ast.Lambda):
            lambda_node = node.value
            lambda_node.custom_ignore = True
            args = [arg.arg for arg in lambda_node.args.args]
            body = lambda_node.body
            value_expr = None
            value_lambda = (args, body)
        else:
            value_expr = node.value
            value_lambda = None

        converter.process_init_variable(
            name=node.target.id,
            value_expr=value_expr,
            annotation=convert_annotation(node.annotation, node),
            value_lambda=value_lambda,
        )

    elif isinstance(node, ast.Assign):
        # if isinstance(node.value, ast.IfExp):
        #     data = {'targets': node.targets, 'value': None}
        #     walk(converter, node.value, for_ifexpr=data)
        #     node.value = data['value']

        converter.process_assign_variable(
            names=node.targets,
            value=node.value,
        )

    elif isinstance(node, ast.AugAssign):
        converter.process_augassign_variable(
            name=node.target,
            value=node.value,
            operator=convert_op(node.op),
        )

    elif isinstance(node, ast.FunctionDef):
        pos_args = []
        for index_arg, arg in enumerate(node.args.args):  # node.args is ast.arguments
            ann_name = convert_annotation(arg.annotation, node)
            pos_arg = (ann_name, arg.arg)
            pos_args.append(pos_arg)

        docstring_comment = ast.get_docstring(node)
        if docstring_comment is not None:
            node.body[0].custom_ignore = True
            node.body[0].value.custom_ignore = True

        converter.process_def_function(
            name=node.name,
            annotation=convert_annotation(node.returns, node),
            pos_args=pos_args,
            pos_args_defaults=node.args.defaults,
            body=node.body,
            docstring_comment=docstring_comment,
        )

    elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
        converter.process_call_function(
            name=node.func,
            pos_args=node.args,
        )

    elif isinstance(node, ast.Constant):
        converter.process_constant(node.value, node)

    elif isinstance(node, ast.Num):  # Deprecated since version 3.8
        converter.process_constant(node.n, node)

    elif isinstance(node, ast.Str):  # Deprecated since version 3.8
        converter.process_constant(node.s, node)

    elif isinstance(node, ast.Name):
        converter.process_name(node.id)
        node.ctx.custom_ignore = True  # we ignore ast.Load, ast.Store and ast.Del

    elif isinstance(node, (ast.Load, ast.Store, ast.Del)):
        pass

    elif isinstance(node, ast.Delete):
        names = []
        for target_node in node.targets:
            names.append(target_node)

        converter.process_delete_variable(names)

    elif isinstance(node, ast.BinOp):
        is_need_brackets = isinstance(parent_node, (ast.BinOp, ast.UnaryOp))
        converter.process_binary_op(
            operand_left=node.left,
            operator=convert_op(node.op),
            operand_right=node.right,
            is_need_brackets=is_need_brackets,
        )

    elif isinstance(node, ast.BoolOp):
        is_need_brackets = isinstance(parent_node, (ast.BoolOp, ast.UnaryOp))
        converter.process_bool_op(
            operand_left=node.values[0],
            operator=convert_bool_op(node.op),
            operands_right=node.values[1:],
            is_need_brackets=is_need_brackets,
        )

    elif isinstance(node, ast.UnaryOp):
        converter.process_unary_op(
            operand=node.operand,
            operator=convert_unary_op(node.op),
        )

    elif isinstance(node, ast.Return):
        if isinstance(node.value, ast.Tuple):
            converter.process_multi_return(expressions=node.value)
        else:
            converter.process_return(expression=node.value)

    elif isinstance(node, ast.NameConstant):  # New in version 3.4; Deprecated since version 3.8
        if isinstance(node.value, bool):
            converter.process_constant(node.value, node)
        else:
            walk(converter, node.value)

    elif isinstance(node, ast.IfExp):
        is_need_brackets = isinstance(parent_node, (ast.Call, ast.BoolOp))
        converter.process_ifexpr(
            condition=node.test,
            body=node.body,
            orelse=node.orelse,
            is_need_brackets=is_need_brackets,
        )

    # Control flow

    elif isinstance(node, ast.If):
        ifelses = []
        orelse = node.orelse
        while orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If):
            ifelses.append((orelse[0].test, orelse[0].body))
            orelse = orelse[0].orelse
            node.orelse = None

        converter.process_if(
            condition=node.test,
            body=node.body,
            ifelses=ifelses,
            orelse=orelse,
        )

    elif isinstance(node, ast.For):
        if isinstance(node.target, ast.Name):
            name = node.target.id
        else:
            raise Exception('Unsupported target of `for`!')

        if isinstance(node.iter, ast.Call):
            converter.process_for_function(name, node.body, node.iter.func.id, node.iter.args)
        else:
            raise Exception('Unsupported iter of `for`!')

    elif isinstance(node, ast.While):
        has_while_orelse.append(bool(node.orelse))
        converter.process_while(
            condition=node.test,
            body=node.body,
            orelse=node.orelse,
        )
        has_while_orelse.pop()

    elif isinstance(node, ast.Break):
        converter.process_break(has_while_orelse[-1])

    elif isinstance(node, ast.Continue):
        converter.process_continue()

    elif isinstance(node, ast.Expr):
        if isinstance(node.value, (ast.Str, ast.Constant)) and isinstance(parent_node, ast.Module):
            comment = ''
            if isinstance(node.value, ast.Str):
                comment = node.value.s
            elif isinstance(node.value, ast.Constant):
                comment = node.value.value

            if '\n' in comment:
                converter.process_multiline_comment(comment)
            else:
                converter.process_one_comment(comment)
        else:
            converter.process_expression(
                expression=node.value,
            )

    elif isinstance(node, ast.Pass):
        pass

    elif isinstance(node, ast.Import):
        converter.process_import([(node_name.name, node_name.asname) for node_name in node.names])

    elif isinstance(node, ast.ImportFrom):
        names = [(alias.name, alias.asname) for alias in node.names]
        converter.process_import_from(node.module, names, node.level)

    elif isinstance(node, ast.Compare):
        converter.process_compare(node.left, [convert_compare_op(op) for op in node.ops], node.comparators)

    elif isinstance(node, ast.Attribute):
        converter.process_attribute(node.value, node.attr)

    elif isinstance(node, ast.Lambda):
        pos_args = []
        node.args.custom_ignore = True
        for arg in node.args.args:  # node.args is ast.arguments
            pos_args.append(arg.arg)

        converter.process_lambda(pos_args, node.body)

    # Subscripting
    elif isinstance(node, ast.Subscript):
        if isinstance(node.slice, ast.Index):  # ast.Index is for Python <=3.8;
            node.slice.custom_ignore = True
            index = node.slice.value
        elif isinstance(node.slice, ast.Constant):  # ast.Constant is for Python >= 3.9
            index = node.slice
        elif isinstance(node.slice, ast.Name):  # ast.Constant is for Python >= 3.9
            index = node.slice
        else:
            raise SourceCodeException('Unknown index node', node.slice)

        converter.process_subscript(node.value, index)

    # elif isinstance(node, ast.Slice):
    # elif isinstance(node, ast.ExtSlice):

    # Top level nodes
    elif isinstance(node, ast.Module):
        for body_node in node.body:
            walk(converter, body_node)

    # elif isinstance(node, ast.Interactive):
    # elif isinstance(node, ast.Expression):

    # Literals
    elif isinstance(node, (ast.List, ast.Tuple)):
        variable_name = None
        if parent_node and isinstance(parent_node, ast.AnnAssign):
            variable_name = parent_node.target.id

        converter.process_array(node.elts, variable_name)

    #     if isinstance(parent_node, ast.Return):
    #         converter.process_multi_return(expressions=node.elts)
    #     else:
    #         raise SourceCodeException(f'unknown node: {node.__class__.__name__}', node)

    else:
        raise SourceCodeException(f'unknown node: {node.__class__.__name__}', node)

    if parents:
        parents.pop()


def translate(translator, source_code):
    translator._walk = walk
    tree = ast.parse(source_code)
    walk(translator, tree)
    translator.save()