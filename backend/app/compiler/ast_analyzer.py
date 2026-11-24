import ast
from typing import Any, Tuple, Dict
from app.schemas.compiler_schemas import ASTNodeItem

class ASTAnalyzer:
    """
    Transforms raw language-specific AST objects into a standardized
    hierarchical ASTNodeItem structure for visual interactive tree rendering.
    """

    @staticmethod
    def to_tree(raw_ast: Any, language: str = "python") -> Tuple[ASTNodeItem, int]:
        lang = (language or "python").lower()
        node_counter = [0]

        if lang == "c":
            root_node = ASTAnalyzer._convert_c_ast(raw_ast, node_counter)
        elif lang == "java":
            root_node = ASTAnalyzer._convert_java_ast(raw_ast, node_counter)
        else:
            root_node = ASTAnalyzer._convert_python_ast(raw_ast, node_counter)

        return root_node, node_counter[0]

    @staticmethod
    def _convert_python_ast(node: Any, counter: list, parent_path: str = "0") -> ASTNodeItem:
        if node is None:
            counter[0] += 1
            return ASTNodeItem(
                id=f"node-{counter[0]}",
                type="None",
                label="None",
                children=[],
                properties={}
            )

        counter[0] += 1
        node_id = f"node-{counter[0]}"
        node_type = type(node).__name__
        line = getattr(node, 'lineno', None)
        col = getattr(node, 'col_offset', None)

        # Build informative label
        label = node_type
        props: Dict[str, Any] = {}

        if isinstance(node, ast.FunctionDef):
            label = f"def {node.name}(...)"
            props["name"] = node.name
            props["args"] = [a.arg for a in node.args.args]
        elif isinstance(node, ast.AsyncFunctionDef):
            label = f"async def {node.name}(...)"
            props["name"] = node.name
        elif isinstance(node, ast.ClassDef):
            label = f"class {node.name}"
            props["name"] = node.name
        elif isinstance(node, ast.Name):
            label = f"Name: {node.id}"
            props["id"] = node.id
            props["ctx"] = type(node.ctx).__name__
        elif isinstance(node, ast.Constant):
            val_repr = repr(node.value)
            if len(val_repr) > 30:
                val_repr = val_repr[:27] + "..."
            label = f"Constant: {val_repr}"
            props["value"] = str(node.value)
        elif isinstance(node, ast.Call):
            func_name = ASTAnalyzer._get_call_name(node.func)
            label = f"Call: {func_name}()"
            props["func"] = func_name
        elif isinstance(node, ast.Assign):
            label = "Assign (=)"
        elif isinstance(node, ast.BinOp):
            op_name = type(node.op).__name__
            label = f"BinOp ({op_name})"
        elif isinstance(node, ast.Compare):
            ops = [type(op).__name__ for op in node.ops]
            label = f"Compare ({', '.join(ops)})"
        elif isinstance(node, ast.If):
            label = "If Statement"
        elif isinstance(node, ast.For):
            label = "For Loop"
        elif isinstance(node, ast.While):
            label = "While Loop"
        elif isinstance(node, ast.Return):
            label = "Return"
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            label = f"import {', '.join(names)}"
            props["modules"] = names
        elif isinstance(node, ast.ImportFrom):
            names = [alias.name for alias in node.names]
            label = f"from {node.module or ''} import {', '.join(names)}"
            props["module"] = node.module

        children: list[ASTNodeItem] = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        children.append(ASTAnalyzer._convert_python_ast(item, counter))
            elif isinstance(value, ast.AST):
                children.append(ASTAnalyzer._convert_python_ast(value, counter))

        return ASTNodeItem(
            id=node_id,
            type=node_type,
            label=label,
            line=line,
            column=col,
            children=children,
            properties=props
        )

    @staticmethod
    def _get_call_name(func_node: Any) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return f"{ASTAnalyzer._get_call_name(func_node.value)}.{func_node.attr}"
        return "call"

    @staticmethod
    def _convert_java_ast(node: Any, counter: list) -> ASTNodeItem:
        counter[0] += 1
        node_id = f"node-{counter[0]}"

        if hasattr(node, '__class__'):
            node_type = node.__class__.__name__
        else:
            node_type = type(node).__name__

        label = node_type
        line = None
        props: Dict[str, Any] = {}

        if hasattr(node, 'position') and node.position:
            line = node.position.line

        if hasattr(node, 'name'):
            label = f"{node_type}: {node.name}"
            props["name"] = str(node.name)
        elif hasattr(node, 'value'):
            label = f"{node_type}: {str(node.value)[:25]}"
            props["value"] = str(node.value)

        children: list[ASTNodeItem] = []
        if hasattr(node, 'children'):
            for child in node.children:
                if child is not None:
                    if isinstance(child, (list, tuple)):
                        for subchild in child:
                            if hasattr(subchild, '__class__') and not isinstance(subchild, (str, int, float, bool)):
                                children.append(ASTAnalyzer._convert_java_ast(subchild, counter))
                    elif hasattr(child, '__class__') and not isinstance(child, (str, int, float, bool)):
                        children.append(ASTAnalyzer._convert_java_ast(child, counter))

        return ASTNodeItem(
            id=node_id,
            type=node_type,
            label=label,
            line=line,
            column=None,
            children=children,
            properties=props
        )

    @staticmethod
    def _convert_c_ast(node: Any, counter: list) -> ASTNodeItem:
        counter[0] += 1
        node_id = f"node-{counter[0]}"

        # pycparser AST or GenericCNode
        if hasattr(node, 'node_type'):
            node_type = node.node_type
            label = f"{node_type}: {node.name}" if node.name else node_type
            line = getattr(node, 'line', 1)
            props = getattr(node, 'properties', {})
            children = [ASTAnalyzer._convert_c_ast(child, counter) for child in getattr(node, 'children', [])]
            return ASTNodeItem(
                id=node_id,
                type=node_type,
                label=label,
                line=line,
                children=children,
                properties=props
            )

        # Standard pycparser Node
        node_type = type(node).__name__
        label = node_type
        line = 1
        props: Dict[str, Any] = {}

        if hasattr(node, 'coord') and node.coord:
            line = getattr(node.coord, 'line', 1)

        if hasattr(node, 'name') and node.name:
            label = f"{node_type}: {node.name}"
            props["name"] = str(node.name)

        children: list[ASTNodeItem] = []
        if hasattr(node, 'children'):
            for _, child in node.children():
                if child:
                    children.append(ASTAnalyzer._convert_c_ast(child, counter))

        return ASTNodeItem(
            id=node_id,
            type=node_type,
            label=label,
            line=line,
            children=children,
            properties=props
        )

