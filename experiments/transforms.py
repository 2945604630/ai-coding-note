"""Finite AST interventions and general mutation operators, without label lookup."""
import ast
import copy


def _replace(source, ordinal, replacement):
    tree = ast.parse(source)
    target = list(ast.walk(tree))[ordinal]
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is target:
                setattr(parent, field, copy.deepcopy(replacement))
            elif isinstance(value, list):
                for i, child in enumerate(value):
                    if child is target:
                        value[i] = copy.deepcopy(replacement)
    return ast.unparse(ast.fix_missing_locations(tree)) + "\n"


def intervention(source, cause):
    """Return one local counterfactual for supported syntax, else None."""
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    if cause == "init_zero":
        param = tree.body[0].args.args[0].arg
        for i, node in enumerate(nodes):
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.Constant) and node.value.value == 0):
                continue
            name = node.targets[0].id
            compares = any(isinstance(c, ast.Compare) and any(isinstance(v, ast.Name) and v.id == name for v in [c.left, *c.comparators])
                           and any(isinstance(o, (ast.Gt, ast.Lt)) for o in c.ops) for c in nodes)
            if compares:
                replacement = copy.deepcopy(node)
                replacement.value = ast.Subscript(value=ast.Name(id=param, ctx=ast.Load()), slice=ast.Constant(0), ctx=ast.Load())
                return _replace(source, i, replacement)
    elif cause == "loop_end_excluded":
        for i, node in enumerate(nodes):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" and 1 <= len(node.args) <= 2:
                stop = node.args[-1]
                if isinstance(stop, ast.Name):
                    replacement = copy.deepcopy(node)
                    replacement.args[-1] = ast.BinOp(left=copy.deepcopy(stop), op=ast.Add(), right=ast.Constant(1))
                    return _replace(source, i, replacement)
    elif cause == "accumulator_overwrite":
        for loop in nodes:
            if not isinstance(loop, ast.For) or not isinstance(loop.target, ast.Name):
                continue
            for node in loop.body:
                if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                        and isinstance(node.value, ast.Name) and node.value.id == loop.target.id):
                    replacement = ast.AugAssign(target=copy.deepcopy(node.targets[0]), op=ast.Add(), value=copy.deepcopy(node.value))
                    return _replace(source, nodes.index(node), replacement)
    elif cause == "index_off_by_one":
        for i, node in enumerate(nodes):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" and len(node.args) == 1:
                stop = node.args[0]
                if (isinstance(stop, ast.BinOp) and isinstance(stop.op, ast.Add) and isinstance(stop.right, ast.Constant)
                        and stop.right.value == 1 and isinstance(stop.left, ast.Call) and isinstance(stop.left.func, ast.Name)
                        and stop.left.func.id == "len"):
                    replacement = copy.deepcopy(node)
                    replacement.args[0] = copy.deepcopy(stop.left)
                    return _replace(source, i, replacement)
    return None


def generic_mutants(source):
    """General operators include the same target faults; no pack/category lookup."""
    tree = ast.parse(source)
    mutations = []
    for i, node in enumerate(ast.walk(tree)):
        options = []
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value in {0, 1}:
            options.append(("constant", ast.Constant(1 - node.value)))
        if isinstance(node, ast.Subscript):
            options.append(("subscript_to_zero", ast.Constant(0)))
        if isinstance(node, ast.Return):
            options.append(("return_zero", ast.Return(ast.Constant(0))))
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            changes = {ast.Gt: ast.GtE, ast.Lt: ast.LtE, ast.GtE: ast.Gt, ast.LtE: ast.Lt}
            if type(node.ops[0]) in changes:
                replacement = copy.deepcopy(node)
                replacement.ops = [changes[type(node.ops[0])]()]
                options.append(("comparison_boundary", replacement))
        if isinstance(node, ast.BinOp):
            changes = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Add}
            if type(node.op) in changes:
                replacement = copy.deepcopy(node)
                replacement.op = changes[type(node.op)]()
                options.append(("binary_operator", replacement))
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
            options.append(("accumulate_to_assign", ast.Assign(targets=[copy.deepcopy(node.target)], value=copy.deepcopy(node.value))))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range" and node.args:
            for op, label in [(ast.Add(), "range_plus_one"), (ast.Sub(), "range_minus_one")]:
                replacement = copy.deepcopy(node)
                replacement.args[-1] = ast.BinOp(left=copy.deepcopy(node.args[-1]), op=op, right=ast.Constant(1))
                options.append((label, replacement))
        for label, replacement in options:
            result = _replace(source, i, replacement)
            if result != ast.unparse(tree) + "\n" and result not in {m["source"] for m in mutations}:
                mutations.append({"operator": label, "source": result})
    return mutations

