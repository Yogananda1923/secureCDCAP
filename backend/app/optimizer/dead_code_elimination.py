import ast
from typing import Tuple, List

class DeadCodeEliminationOptimizer(ast.NodeTransformer):
    """
    Compiler Optimization Pass: Dead Code Elimination (DCE).
    Removes statically unreachable statements following return/raise/break/continue
    and prunes always-false conditional branches.
    """

    def __init__(self):
        super().__init__()
        self.eliminated_count = 0
        self.transformations: List[str] = []

    def visit_FunctionDef(self, node):
        node.body = self._prune_unreachable_statements(node.body, f"Function {node.name}")
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        node.body = self._prune_unreachable_statements(node.body, f"Async Function {node.name}")
        self.generic_visit(node)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        # Check if test condition is statically constant False or 0
        if isinstance(node.test, ast.Constant):
            if not bool(node.test.value):
                # if False block is dead code
                self.eliminated_count += len(node.body)
                self.transformations.append(f"Eliminated dead 'if False' branch containing {len(node.body)} statements")
                return node.orelse if node.orelse else None
            else:
                # if True block: eliminate else branch
                if node.orelse:
                    self.eliminated_count += len(node.orelse)
                    self.transformations.append(f"Eliminated dead 'else' branch of 'if True' ({len(node.orelse)} statements)")
                    node.orelse = []
                return node

        node.body = self._prune_unreachable_statements(node.body, "If-branch")
        if node.orelse:
            node.orelse = self._prune_unreachable_statements(node.orelse, "Else-branch")
        return node

    def _prune_unreachable_statements(self, statements: List[ast.stmt], context: str) -> List[ast.stmt]:
        pruned = []
        terminal_hit = False

        for stmt in statements:
            if terminal_hit:
                self.eliminated_count += 1
                line = getattr(stmt, 'lineno', '?')
                desc = f"Removed unreachable statement '{type(stmt).__name__}' at line {line} in {context}"
                self.transformations.append(desc)
            else:
                pruned.append(stmt)
                if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                    terminal_hit = True

        return pruned

    @classmethod
    def optimize(cls, tree: ast.AST) -> Tuple[ast.AST, int, List[str]]:
        optimizer = cls()
        new_tree = optimizer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree, optimizer.eliminated_count, optimizer.transformations

