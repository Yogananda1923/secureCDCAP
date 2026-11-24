import ast
import re
from typing import Any, List, Set, Tuple
from app.compiler.symbol_table import SymbolTable
from app.schemas.compiler_schemas import (
    SemanticResult,
    SemanticIssueItem,
    SymbolItem,
    ScopeItem
)

PYTHON_BUILTINS = {
    'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set', 'tuple',
    'bool', 'type', 'open', 'sum', 'min', 'max', 'abs', 'all', 'any', 'enumerate',
    'zip', 'map', 'filter', 'sorted', 'reversed', 'isinstance', 'issubclass',
    'input', 'hasattr', 'getattr', 'setattr', 'delattr', 'id', 'hash', 'repr',
    'dir', 'help', 'format', 'round', 'pow', 'chr', 'ord', 'super', 'iter', 'next',
    'True', 'False', 'None', 'Exception', 'ValueError', 'TypeError', 'KeyError',
    'IndexError', 'FileNotFoundError', 'IOError', 'RuntimeError', 'BaseException'
}

C_BUILTINS = {
    'printf', 'scanf', 'malloc', 'free', 'calloc', 'realloc', 'exit', 'strlen',
    'strcpy', 'strncpy', 'strcat', 'strncat', 'strcmp', 'strncmp', 'sprintf',
    'snprintf', 'fopen', 'fclose', 'fread', 'fwrite', 'fprintf', 'fscanf',
    'fgets', 'fputs', 'puts', 'getchar', 'putchar', 'memcpy', 'memset', 'memmove',
    'sizeof', 'NULL', 'stdin', 'stdout', 'stderr'
}

JAVA_BUILTINS = {
    'System', 'String', 'Integer', 'Double', 'Float', 'Boolean', 'Character',
    'Math', 'Object', 'Class', 'Thread', 'Exception', 'RuntimeException',
    'List', 'ArrayList', 'Map', 'HashMap', 'Set', 'HashSet', 'Arrays', 'Collections',
    'Scanner', 'File', 'FileInputStream', 'FileOutputStream', 'BufferedReader',
    'null', 'true', 'false', 'this', 'super'
}

class SemanticAnalyzer:
    """
    Performs semantic checks including scope analysis, symbol resolution,
    undefined variable detection, unused variable analysis, unreachable code detection,
    and type mismatch heuristics.
    """

    @staticmethod
    def analyze(raw_ast: Any, code: str, language: str = "python") -> SemanticResult:
        lang = (language or "python").lower()
        if lang == "c":
            return SemanticAnalyzer._analyze_c(raw_ast, code)
        elif lang == "java":
            return SemanticAnalyzer._analyze_java(raw_ast, code)
        else:
            return SemanticAnalyzer._analyze_python(raw_ast, code)

    @staticmethod
    def _analyze_python(tree: Any, code: str) -> SemanticResult:
        sym_table = SymbolTable()
        issues: List[SemanticIssueItem] = []
        undefined_vars: Set[str] = set()
        unreachable_lines: List[int] = []
        type_warnings: List[str] = []

        if not isinstance(tree, ast.AST):
            return SemanticResult(
                symbols=[],
                scopes=[sym_table.global_scope.to_schema()],
                undefined_variables=[],
                unused_variables=[],
                unreachable_lines=[],
                type_warnings=[],
                issues=[]
            )

        # Visitor for scope and symbol resolution
        class SemanticVisitor(ast.NodeVisitor):
            def __init__(self):
                self.imported_modules: Set[str] = set()

            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.asname or alias.name
                    sym_table.define(name, "module", node.lineno, data_type="module")
                    self.imported_modules.add(name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                for alias in node.names:
                    name = alias.asname or alias.name
                    sym_table.define(name, "import", node.lineno, data_type="imported_symbol")
                    self.imported_modules.add(name)
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                # Define function in enclosing scope
                sym_table.define(node.name, "function", node.lineno, data_type="callable")
                
                # Enter function scope
                sym_table.enter_scope(node.name)
                for arg in node.args.args:
                    arg_type = "unknown"
                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                        arg_type = arg.annotation.id
                    sym_table.define(arg.arg, "parameter", node.lineno, data_type=arg_type)
                
                # Check for unreachable code inside body
                has_terminal = False
                for stmt in node.body:
                    if has_terminal:
                        unreachable_lines.append(stmt.lineno)
                        issues.append(SemanticIssueItem(
                            issue_type="UnreachableCode",
                            severity="Warning",
                            message=f"Statement is unreachable after return/raise at line {stmt.lineno}",
                            line=stmt.lineno
                        ))
                    if isinstance(stmt, (ast.Return, ast.Raise)):
                        has_terminal = True
                    self.visit(stmt)

                sym_table.exit_scope()

            def visit_ClassDef(self, node):
                sym_table.define(node.name, "class", node.lineno, data_type="type")
                sym_table.enter_scope(f"class_{node.name}")
                self.generic_visit(node)
                sym_table.exit_scope()

            def visit_Assign(self, node):
                # First visit value (RHS)
                self.visit(node.value)
                # Then register targets (LHS)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        inferred_type = SemanticAnalyzer._infer_type(node.value)
                        sym_table.define(target.id, "variable", node.lineno, data_type=inferred_type)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                sym_table.define(elt.id, "variable", node.lineno)

            def visit_Name(self, node):
                name = node.id
                if isinstance(node.ctx, ast.Load):
                    if (name not in PYTHON_BUILTINS and 
                        not sym_table.is_defined(name) and 
                        name not in self.imported_modules):
                        undefined_vars.add(name)
                        issues.append(SemanticIssueItem(
                            issue_type="UndefinedVariable",
                            severity="Error",
                            message=f"Usage of potentially undefined variable or symbol '{name}'",
                            line=node.lineno,
                            column=node.col_offset
                        ))
                    else:
                        sym_table.mark_used(name)
                self.generic_visit(node)

            def visit_BinOp(self, node):
                # Type mismatch check: e.g. "str" + 42
                left_type = SemanticAnalyzer._infer_type(node.left)
                right_type = SemanticAnalyzer._infer_type(node.right)
                if left_type != "unknown" and right_type != "unknown" and left_type != right_type:
                    if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                        # If string + int/float, invalid
                        if (left_type == "str" and right_type in ("int", "float")) or \
                           (left_type in ("int", "float") and right_type == "str"):
                            msg = f"Type mismatch: Binary operation between '{left_type}' and '{right_type}' at line {node.lineno}"
                            type_warnings.append(msg)
                            issues.append(SemanticIssueItem(
                                issue_type="TypeMismatch",
                                severity="Warning",
                                message=msg,
                                line=node.lineno
                            ))
                self.generic_visit(node)

        visitor = SemanticVisitor()
        visitor.visit(tree)

        # Detect unused variables (skip special names like _, __)
        all_symbols = sym_table.get_all_symbols()
        unused_vars: List[str] = []
        for sym in all_symbols:
            if sym.symbol_type in ("variable", "parameter") and not sym.is_used:
                if not sym.name.startswith("_") and sym.name not in ("self", "cls"):
                    unused_vars.append(sym.name)
                    issues.append(SemanticIssueItem(
                        issue_type="UnusedVariable",
                        severity="Info",
                        message=f"Variable '{sym.name}' declared at line {sym.declared_line} is never read or used",
                        line=sym.declared_line
                    ))

        return SemanticResult(
            symbols=all_symbols,
            scopes=sym_table.get_all_scope_schemas(),
            undefined_variables=list(undefined_vars),
            unused_variables=unused_vars,
            unreachable_lines=unreachable_lines,
            type_warnings=type_warnings,
            issues=issues
        )

    @staticmethod
    def _infer_type(node: Any) -> str:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int):
                return "int"
            elif isinstance(node.value, float):
                return "float"
            elif isinstance(node.value, str):
                return "str"
            elif isinstance(node.value, bool):
                return "bool"
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        return "unknown"

    @staticmethod
    def _analyze_c(raw_ast: Any, code: str) -> SemanticResult:
        sym_table = SymbolTable()
        issues: List[SemanticIssueItem] = []
        undefined_vars: Set[str] = set()
        unused_vars: List[str] = []
        unreachable_lines: List[int] = []

        lines = code.splitlines()
        decl_regex = re.compile(r'\b(int|char|float|double|void|size_t|long)\s+(\*+)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\b')
        func_regex = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        # First pass: collect declarations
        declared_names = set(C_BUILTINS)
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # Ignore comments
            if sline.startswith("//") or sline.startswith("/*") or sline.startswith("#"):
                continue
            for match in decl_regex.finditer(sline):
                var_type, _, var_name = match.groups()
                if var_name not in ('if', 'while', 'for', 'return', 'main'):
                    sym_table.define(var_name, "variable", idx, data_type=var_type)
                    declared_names.add(var_name)

        # Second pass: check usages and unreachable code
        in_return = False
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if sline.startswith("return ") or sline.startswith("return;"):
                in_return = True
                continue
            if sline == "}":
                in_return = False
                continue
            if in_return and sline and not sline.startswith("//"):
                unreachable_lines.append(idx)
                issues.append(SemanticIssueItem(
                    issue_type="UnreachableCode",
                    severity="Warning",
                    message=f"C statement unreachable after return at line {idx}",
                    line=idx
                ))

            # Check usages
            tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', sline)
            for tok in tokens:
                if tok in declared_names:
                    sym_table.mark_used(tok)

        # Check unused symbols
        for sym in sym_table.get_all_symbols():
            if not sym.is_used:
                unused_vars.append(sym.name)
                issues.append(SemanticIssueItem(
                    issue_type="UnusedVariable",
                    severity="Info",
                    message=f"Variable '{sym.name}' declared at line {sym.declared_line} is unused",
                    line=sym.declared_line
                ))

        return SemanticResult(
            symbols=sym_table.get_all_symbols(),
            scopes=sym_table.get_all_scope_schemas(),
            undefined_variables=list(undefined_vars),
            unused_variables=unused_vars,
            unreachable_lines=unreachable_lines,
            type_warnings=[],
            issues=issues
        )

    @staticmethod
    def _analyze_java(raw_ast: Any, code: str) -> SemanticResult:
        sym_table = SymbolTable()
        issues: List[SemanticIssueItem] = []
        undefined_vars: Set[str] = set()
        unused_vars: List[str] = []
        unreachable_lines: List[int] = []

        lines = code.splitlines()
        decl_regex = re.compile(r'\b(int|String|boolean|double|float|long|char|List|Map|Set|Scanner|File)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b')

        declared_names = set(JAVA_BUILTINS)
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if sline.startswith("//") or sline.startswith("/*") or sline.startswith("import ") or sline.startswith("package "):
                continue
            for match in decl_regex.finditer(sline):
                var_type, var_name = match.groups()
                sym_table.define(var_name, "variable", idx, data_type=var_type)
                declared_names.add(var_name)

        in_return = False
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if sline.startswith("return ") or sline.startswith("return;") or sline.startswith("throw "):
                in_return = True
                continue
            if sline == "}":
                in_return = False
                continue
            if in_return and sline and not sline.startswith("//"):
                unreachable_lines.append(idx)
                issues.append(SemanticIssueItem(
                    issue_type="UnreachableCode",
                    severity="Warning",
                    message=f"Java statement unreachable after return/throw at line {idx}",
                    line=idx
                ))

            tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', sline)
            for tok in tokens:
                if tok in declared_names:
                    sym_table.mark_used(tok)

        for sym in sym_table.get_all_symbols():
            if not sym.is_used:
                unused_vars.append(sym.name)
                issues.append(SemanticIssueItem(
                    issue_type="UnusedVariable",
                    severity="Info",
                    message=f"Java variable '{sym.name}' declared at line {sym.declared_line} is unused",
                    line=sym.declared_line
                ))

        return SemanticResult(
            symbols=sym_table.get_all_symbols(),
            scopes=sym_table.get_all_scope_schemas(),
            undefined_variables=list(undefined_vars),
            unused_variables=unused_vars,
            unreachable_lines=unreachable_lines,
            type_warnings=[],
            issues=issues
        )

