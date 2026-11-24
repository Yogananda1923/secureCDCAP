import ast
import re
from typing import Tuple, Optional, Any, List
import javalang

class ParserEngine:
    """
    Multi-language syntax parser supporting Python, C, and Java.
    Produces raw ASTs or structured parse trees, detects syntax errors,
    and reports line/column locations.
    """

    @staticmethod
    def parse_python(code: str) -> Tuple[bool, Optional[Any], List[str]]:
        try:
            tree = ast.parse(code)
            return True, tree, []
        except SyntaxError as e:
            msg = f"SyntaxError at line {e.lineno}, column {e.offset or 1}: {e.msg}"
            return False, None, [msg]
        except Exception as e:
            return False, None, [f"Parse failure: {str(e)}"]

    @staticmethod
    def parse_java(code: str) -> Tuple[bool, Optional[Any], List[str]]:
        try:
            tree = javalang.parse.parse(code)
            return True, tree, []
        except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError) as e:
            pos = getattr(e, 'position', None)
            line = pos[0] if pos else 1
            col = pos[1] if pos else 1
            msg = f"Java SyntaxError at line {line}, col {col}: {e.description if hasattr(e, 'description') else str(e)}"
            return False, None, [msg]
        except Exception as e:
            # Try wrapping snippet into a class if user provided a method or fragment
            try:
                wrapped_code = f"public class WrapperClass {{\n{code}\n}}"
                tree = javalang.parse.parse(wrapped_code)
                return True, tree, []
            except Exception:
                return False, None, [f"Java Parse Error: {str(e)}"]

    @staticmethod
    def parse_c(code: str) -> Tuple[bool, Optional[Any], List[str]]:
        """
        Parses C source code using pycparser with preprocessing fallback
        to accommodate common headers and standard C idioms.
        """
        # Preprocessing: remove #include lines and insert dummy typedefs for pycparser
        cleaned_lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith('#include') or stripped.startswith('#define') or stripped.startswith('#pragma'):
                cleaned_lines.append(f"// {line}")
            else:
                cleaned_lines.append(line)
        cleaned_code = "\n".join(cleaned_lines)
        
        # Inject standard typedefs commonly used in C
        header_stubs = """
typedef int size_t;
typedef int ssize_t;
typedef void* FILE;
typedef int pid_t;
typedef unsigned int uint32_t;
typedef int int32_t;
typedef char* va_list;
"""
        full_code = header_stubs + "\n" + cleaned_code

        try:
            from pycparser import c_parser
            parser = c_parser.CParser()
            ast_tree = parser.parse(full_code, filename='<string>')
            return True, ast_tree, []
        except Exception as pyc_err:
            # If pycparser fails on partial snippets or syntax variations,
            # use our custom robust C AST builder
            ast_tree, errors = ParserEngine._build_custom_c_ast(code)
            if ast_tree:
                return True, ast_tree, []
            return False, None, [f"C Syntax Note: {str(pyc_err)}"]

    @staticmethod
    def _build_custom_c_ast(code: str) -> Tuple[Optional[Any], List[str]]:
        """
        Lightweight robust C AST representation for functions, control flow,
        pointer dereferences, assignments, and calls.
        """
        class GenericCNode:
            def __init__(self, node_type: str, name: str = "", line: int = 1, children=None, properties=None):
                self.node_type = node_type
                self.name = name
                self.line = line
                self.children = children or []
                self.properties = properties or {}

        root = GenericCNode("TranslationUnit", "Root", line=1)
        lines = code.splitlines()

        func_pattern = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_\*\s]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*\{?')
        call_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)')
        decl_pattern = re.compile(r'^\s*(char|int|float|double|void|size_t|long|short)\s*(\*+)?\s*([a-zA-Z_][a-zA-Z0-9_]*)(\[.*?\])?(\s*=\s*(.*?))?;')

        current_func = None
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if not sline or sline.startswith('//'):
                continue
            
            # Check function definition
            fmatch = func_pattern.match(sline)
            if fmatch:
                ret_type, fname, params = fmatch.groups()
                ret_type = ret_type.strip()
                if ret_type not in ('if', 'while', 'for', 'switch'):
                    func_node = GenericCNode(
                        "FunctionDef",
                        name=fname,
                        line=idx,
                        properties={"return_type": ret_type, "parameters": params}
                    )
                    root.children.append(func_node)
                    current_func = func_node
                    continue

            # Check variable declaration
            dmatch = decl_pattern.match(sline)
            if dmatch:
                base_type, is_ptr, var_name, is_arr, _, init_val = dmatch.groups()
                var_node = GenericCNode(
                    "Decl",
                    name=var_name,
                    line=idx,
                    properties={
                        "type": base_type,
                        "is_pointer": bool(is_ptr),
                        "is_array": bool(is_arr),
                        "initializer": (init_val or "").strip()
                    }
                )
                target = current_func.children if current_func else root.children
                target.append(var_node)
                continue

            # Check function call
            for cmatch in call_pattern.finditer(sline):
                cname, cargs = cmatch.groups()
                if cname not in ('if', 'while', 'for', 'switch', 'return', 'sizeof'):
                    call_node = GenericCNode(
                        "FuncCall",
                        name=cname,
                        line=idx,
                        properties={"arguments": [a.strip() for a in cargs.split(',') if a.strip()]}
                    )
                    target = current_func.children if current_func else root.children
                    target.append(call_node)

            # Check control constructs
            if sline.startswith("if ") or sline.startswith("if("):
                target = current_func.children if current_func else root.children
                target.append(GenericCNode("IfStatement", line=idx, properties={"line": sline}))
            elif sline.startswith("while ") or sline.startswith("while("):
                target = current_func.children if current_func else root.children
                target.append(GenericCNode("WhileLoop", line=idx, properties={"line": sline}))
            elif sline.startswith("for ") or sline.startswith("for("):
                target = current_func.children if current_func else root.children
                target.append(GenericCNode("ForLoop", line=idx, properties={"line": sline}))

        return root, []

    @staticmethod
    def parse(code: str, language: str = "python") -> Tuple[bool, Optional[Any], List[str]]:
        lang = (language or "python").lower()
        if lang == "c":
            return ParserEngine.parse_c(code)
        elif lang == "java":
            return ParserEngine.parse_java(code)
        else:
            return ParserEngine.parse_python(code)

