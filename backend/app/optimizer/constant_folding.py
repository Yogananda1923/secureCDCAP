import ast
from typing import Tuple, List

class ConstantFoldingOptimizer(ast.NodeTransformer):
    """
    Compiler Optimization Pass: Constant Folding and Algebraic Simplification.
    Evaluates compile-time constant arithmetic, boolean logic, and string concatenations.
    """

    def __init__(self):
        super().__init__()
        self.folded_count = 0
        self.transformations: List[str] = []

    def visit_BinOp(self, node):
        self.generic_visit(node)
        # Check if both operands are constants
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            lval = node.left.value
            rval = node.right.value
            try:
                result = None
                if isinstance(node.op, ast.Add):
                    result = lval + rval
                elif isinstance(node.op, ast.Sub):
                    result = lval - rval
                elif isinstance(node.op, ast.Mult):
                    result = lval * rval
                elif isinstance(node.op, ast.Div):
                    if rval != 0:
                        result = lval / rval
                elif isinstance(node.op, ast.FloorDiv):
                    if rval != 0:
                        result = lval // rval
                elif isinstance(node.op, ast.Mod):
                    if rval != 0:
                        result = lval % rval
                elif isinstance(node.op, ast.Pow):
                    if abs(rval) <= 100:  # Prevent huge integer calculation
                        result = lval ** rval

                if result is not None:
                    self.folded_count += 1
                    desc = f"Folded constant expression ({repr(lval)} {type(node.op).__name__} {repr(rval)}) -> {repr(result)}"
                    self.transformations.append(desc)
                    return ast.copy_location(ast.Constant(value=result), node)
            except Exception:
                pass
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.operand, ast.Constant):
            val = node.operand.value
            try:
                res = None
                if isinstance(node.op, ast.USub):
                    res = -val
                elif isinstance(node.op, ast.UAdd):
                    res = +val
                elif isinstance(node.op, ast.Not):
                    res = not val
                if res is not None:
                    self.folded_count += 1
                    self.transformations.append(f"Folded unary expression on constant {repr(val)} -> {repr(res)}")
                    return ast.copy_location(ast.Constant(value=res), node)
            except Exception:
                pass
        return node

    @classmethod
    def optimize(cls, tree: ast.AST) -> Tuple[ast.AST, int, List[str]]:
        optimizer = cls()
        new_tree = optimizer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree, optimizer.folded_count, optimizer.transformations

