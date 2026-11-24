import ast
from typing import List, Tuple, Any, Dict
from app.schemas.compiler_schemas import IRInstructionItem

class IRGenerator:
    """
    Intermediate Representation (IR) Generator.
    Produces Three-Address Code (TAC) / Quadruple instructions
    suitable for compiler optimization passes and control-flow analysis.
    """

    def __init__(self):
        self.instructions: List[IRInstructionItem] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, prefix: str = "L") -> str:
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def emit(self, opcode: str, arg1: str = None, arg2: str = None, result: str = None, line: int = None, comment: str = None) -> IRInstructionItem:
        instr = IRInstructionItem(
            index=len(self.instructions),
            opcode=opcode,
            arg1=arg1,
            arg2=arg2,
            result=result,
            line=line,
            comment=comment
        )
        self.instructions.append(instr)
        return instr

    @classmethod
    def generate(cls, raw_ast: Any, code: str, language: str = "python") -> List[IRInstructionItem]:
        lang = (language or "python").lower()
        gen = cls()
        if lang == "c":
            return gen._generate_c_ir(code)
        elif lang == "java":
            return gen._generate_java_ir(code)
        else:
            return gen._generate_python_ir(raw_ast, code)

    def _generate_python_ir(self, tree: Any, code: str) -> List[IRInstructionItem]:
        if not isinstance(tree, ast.AST):
            return self._generate_fallback_ir(code)

        class PyIRVisitor(ast.NodeVisitor):
            def __init__(self, ir_gen: IRGenerator):
                self.ir = ir_gen

            def visit_FunctionDef(self, node):
                self.ir.emit("FUNC_ENTRY", arg1=node.name, line=node.lineno, comment=f"Function {node.name}")
                for arg in node.args.args:
                    self.ir.emit("PARAM_DEF", arg1=arg.arg, line=node.lineno)
                for stmt in node.body:
                    self.visit(stmt)
                self.ir.emit("FUNC_EXIT", arg1=node.name, line=node.lineno)

            def visit_Assign(self, node):
                val_temp = self.visit_expr(node.value)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.ir.emit("ASSIGN", arg1=val_temp, result=target.id, line=node.lineno)
                    elif isinstance(target, ast.Attribute):
                        target_name = f"{target.value.id}.{target.attr}" if isinstance(target.value, ast.Name) else "attr"
                        self.ir.emit("ASSIGN_ATTR", arg1=val_temp, result=target_name, line=node.lineno)

            def visit_Return(self, node):
                ret_val = None
                if node.value:
                    ret_val = self.visit_expr(node.value)
                self.ir.emit("RETURN", arg1=ret_val, line=node.lineno)

            def visit_If(self, node):
                test_temp = self.visit_expr(node.test)
                label_else = self.ir.new_label("L_ELSE")
                label_end = self.ir.new_label("L_ENDIF")

                self.ir.emit("JUMP_IF_FALSE", arg1=test_temp, result=label_else, line=node.lineno)
                for stmt in node.body:
                    self.visit(stmt)
                self.ir.emit("JUMP", result=label_end, line=node.lineno)

                self.ir.emit("LABEL", result=label_else, line=node.lineno)
                for stmt in node.orelse:
                    self.visit(stmt)
                self.ir.emit("LABEL", result=label_end, line=node.lineno)

            def visit_While(self, node):
                label_start = self.ir.new_label("L_LOOP_START")
                label_end = self.ir.new_label("L_LOOP_END")

                self.ir.emit("LABEL", result=label_start, line=node.lineno)
                test_temp = self.visit_expr(node.test)
                self.ir.emit("JUMP_IF_FALSE", arg1=test_temp, result=label_end, line=node.lineno)
                for stmt in node.body:
                    self.visit(stmt)
                self.ir.emit("JUMP", result=label_start, line=node.lineno)
                self.ir.emit("LABEL", result=label_end, line=node.lineno)

            def visit_For(self, node):
                label_start = self.ir.new_label("L_FOR_START")
                label_end = self.ir.new_label("L_FOR_END")
                iter_temp = self.visit_expr(node.iter)
                target_name = node.target.id if isinstance(node.target, ast.Name) else "elem"

                self.ir.emit("ITER_INIT", arg1=iter_temp, result=target_name, line=node.lineno)
                self.ir.emit("LABEL", result=label_start, line=node.lineno)
                cond_temp = self.ir.new_temp()
                self.ir.emit("ITER_HAS_NEXT", arg1=iter_temp, result=cond_temp, line=node.lineno)
                self.ir.emit("JUMP_IF_FALSE", arg1=cond_temp, result=label_end, line=node.lineno)
                self.ir.emit("ITER_NEXT", arg1=iter_temp, result=target_name, line=node.lineno)
                for stmt in node.body:
                    self.visit(stmt)
                self.ir.emit("JUMP", result=label_start, line=node.lineno)
                self.ir.emit("LABEL", result=label_end, line=node.lineno)

            def visit_Expr(self, node):
                self.visit_expr(node.value)

            def visit_expr(self, expr_node) -> str:
                if isinstance(expr_node, ast.Constant):
                    return repr(expr_node.value)
                elif isinstance(expr_node, ast.Name):
                    return expr_node.id
                elif isinstance(expr_node, ast.BinOp):
                    l = self.visit_expr(expr_node.left)
                    r = self.visit_expr(expr_node.right)
                    op_name = type(expr_node.op).__name__.upper()
                    temp = self.ir.new_temp()
                    self.ir.emit(f"BINOP_{op_name}", arg1=l, arg2=r, result=temp, line=getattr(expr_node, 'lineno', None))
                    return temp
                elif isinstance(expr_node, ast.Compare):
                    l = self.visit_expr(expr_node.left)
                    op_name = type(expr_node.ops[0]).__name__.upper()
                    r = self.visit_expr(expr_node.comparators[0])
                    temp = self.ir.new_temp()
                    self.ir.emit(f"CMP_{op_name}", arg1=l, arg2=r, result=temp, line=getattr(expr_node, 'lineno', None))
                    return temp
                elif isinstance(expr_node, ast.Call):
                    func_name = "func"
                    if isinstance(expr_node.func, ast.Name):
                        func_name = expr_node.func.id
                    elif isinstance(expr_node.func, ast.Attribute):
                        func_name = f"{getattr(expr_node.func.value, 'id', 'obj')}.{expr_node.func.attr}"
                    
                    arg_temps = [self.visit_expr(a) for a in expr_node.args]
                    for at in arg_temps:
                        self.ir.emit("PARAM", arg1=at, line=getattr(expr_node, 'lineno', None))
                    res_temp = self.ir.new_temp()
                    self.ir.emit("CALL", arg1=func_name, arg2=str(len(arg_temps)), result=res_temp, line=getattr(expr_node, 'lineno', None))
                    return res_temp
                elif isinstance(expr_node, ast.Attribute):
                    obj_name = getattr(expr_node.value, 'id', 'obj')
                    return f"{obj_name}.{expr_node.attr}"
                return self.ir.new_temp()

        visitor = PyIRVisitor(self)
        visitor.visit(tree)
        if not self.instructions:
            self.emit("NOP", line=1, comment="Empty program")
        return self.instructions

    def _generate_c_ir(self, code: str) -> List[IRInstructionItem]:
        import re
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if not sline or sline.startswith("//"):
                continue
            if sline.startswith("if (") or sline.startswith("if("):
                cond = sline[sline.find('(')+1:sline.rfind(')')]
                lbl = self.new_label("L_ELSE")
                self.emit("JUMP_IF_FALSE", arg1=cond, result=lbl, line=idx)
            elif "return" in sline:
                parts = sline.replace(";", "").split("return")
                val = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                self.emit("RETURN", arg1=val, line=idx)
            elif "=" in sline and not sline.startswith("if"):
                parts = sline.replace(";", "").split("=", 1)
                lhs = parts[0].strip().split()[-1]
                rhs = parts[1].strip()
                self.emit("ASSIGN", arg1=rhs, result=lhs, line=idx)
            elif "(" in sline and sline.endswith(");"):
                fname = sline[:sline.find('(')].strip().split()[-1]
                args = sline[sline.find('(')+1:sline.rfind(')')].strip()
                t = self.new_temp()
                self.emit("CALL", arg1=fname, arg2=args, result=t, line=idx)
        if not self.instructions:
            self.emit("NOP", line=1)
        return self.instructions

    def _generate_java_ir(self, code: str) -> List[IRInstructionItem]:
        import re
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if not sline or sline.startswith("//") or sline.startswith("import") or sline.startswith("package"):
                continue
            if "class " in sline:
                cname = re.findall(r'class\s+([A-Za-z0-9_]+)', sline)
                name = cname[0] if cname else "Class"
                self.emit("CLASS_DEF", arg1=name, line=idx)
            elif "return" in sline:
                val = sline.replace("return", "").replace(";", "").strip()
                self.emit("RETURN", arg1=val if val else None, line=idx)
            elif "=" in sline and not sline.startswith("if"):
                parts = sline.replace(";", "").split("=", 1)
                lhs = parts[0].strip().split()[-1]
                rhs = parts[1].strip()
                self.emit("ASSIGN", arg1=rhs, result=lhs, line=idx)
            elif "(" in sline and sline.endswith(");"):
                fname = sline[:sline.find('(')].strip().split()[-1]
                args = sline[sline.find('(')+1:sline.rfind(')')].strip()
                t = self.new_temp()
                self.emit("CALL", arg1=fname, arg2=args, result=t, line=idx)
        if not self.instructions:
            self.emit("NOP", line=1)
        return self.instructions

    def _generate_fallback_ir(self, code: str) -> List[IRInstructionItem]:
        for idx, line in enumerate(code.splitlines(), 1):
            if line.strip():
                self.emit("RAW_STMT", arg1=line.strip()[:40], line=idx)
        return self.instructions

