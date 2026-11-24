import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class CommandInjectionRule:
    """
    Detects OS Command Injection (CWE-78) and Dynamic Code Execution (CWE-95).
    Identifies invocations of system execution shells, subprocess calls with shell=True,
    eval(), exec(), and runtime process builders without proper argument escaping.
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class CmdVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                func_name = ""
                full_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    full_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                    obj_name = getattr(node.func.value, 'id', '')
                    full_name = f"{obj_name}.{func_name}"

                # 1. os.system, os.popen
                if full_name in ("os.system", "os.popen"):
                    vulns.append(CommandInjectionRule._create_cmd_vuln(
                        line_no=line_no,
                        snippet=snippet,
                        sink=f"Call to {full_name}()",
                        suggested_fix="subprocess.run(['command', arg], check=True, capture_output=True)"
                    ))

                # 2. subprocess.* with shell=True
                elif full_name in ("subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_output"):
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            vulns.append(CommandInjectionRule._create_cmd_vuln(
                                line_no=line_no,
                                snippet=snippet,
                                sink=f"{full_name}(..., shell=True)",
                                suggested_fix="subprocess.run(['command', arg1, arg2], shell=False, check=True)"
                            ))

                # 3. Dynamic code execution: eval(), exec()
                elif func_name in ("eval", "exec"):
                    vulns.append(CommandInjectionRule._create_eval_vuln(
                        line_no=line_no,
                        snippet=snippet,
                        sink=f"Builtin {func_name}() execution"
                    ))

                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            CmdVisitor().visit(tree)

        # Fallback regex scan
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'os\.system\s*\(', sline) and not any(v.line_number == idx for v in vulns):
                vulns.append(CommandInjectionRule._create_cmd_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="os.system() invocation",
                    suggested_fix="subprocess.run(['command', arg], check=True)"
                ))
            elif re.search(r'shell\s*=\s*True', sline) and not any(v.line_number == idx for v in vulns):
                vulns.append(CommandInjectionRule._create_cmd_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="shell=True in process execution",
                    suggested_fix="subprocess.run(['command', arg], shell=False, check=True)"
                ))

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # system(cmd); popen(cmd, "r");
            if re.search(r'\b(system|popen)\s*\([^\)]+\)', sline):
                vulns.append(CommandInjectionRule._create_cmd_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink=f"Call to {sline[:sline.find('(')].strip()}",
                    suggested_fix="Use execve() or posix_spawn() with an explicit argument vector (char* argv[]) instead of shell invocation."
                ))
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # Runtime.getRuntime().exec(...) or ProcessBuilder(cmd + ...)
            if re.search(r'Runtime\.getRuntime\(\)\.exec\s*\(', sline) or \
               re.search(r'new\s+ProcessBuilder\s*\([^)]*\+', sline):
                vulns.append(CommandInjectionRule._create_cmd_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="Runtime.getRuntime().exec() or unseparated ProcessBuilder",
                    suggested_fix="ProcessBuilder pb = new ProcessBuilder(Arrays.asList(\"command\", safeArg));\nProcess p = pb.start();"
                ))
            elif re.search(r'engine\.eval\s*\(', sline):
                vulns.append(CommandInjectionRule._create_eval_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="ScriptEngine.eval() dynamic evaluation"
                ))
        return vulns

    @staticmethod
    def _create_cmd_vuln(line_no: int, snippet: str, sink: str, suggested_fix: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-INJ-002",
            name="Command Injection (Improper Neutralization of Special Elements used in an OS Command)",
            category="Injection",
            cwe_id="CWE-78",
            cwe_name="Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
            severity="Critical",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Invoking shell command interpreter with unvalidated argument string at sink: {sink}.",
            attack_scenario="An attacker provides input containing command separators (e.g. '; rm -rf /' or '& cat /etc/passwd') to achieve arbitrary remote shell code execution.",
            security_impact="Complete server compromise, unauthorized access to host file system, privilege escalation.",
            recommended_solution="Execute target programs with strict argument arrays and disable shell execution (shell=False).",
            suggested_fix=suggested_fix
        )

    @staticmethod
    def _create_eval_vuln(line_no: int, snippet: str, sink: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-INJ-003",
            name="Improper Control of Generation of Code ('Code Injection')",
            category="Injection",
            cwe_id="CWE-94",
            cwe_name="Improper Control of Generation of Code ('Code Injection')",
            severity="Critical",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Dynamic evaluation of untrusted code via {sink}.",
            attack_scenario="An attacker provides Python/Java expression payloads (e.g., __import__('os').system('id')) leading to immediate arbitrary code execution.",
            security_impact="Arbitrary remote code execution within application privileges.",
            recommended_solution="Use safe parsing alternatives such as ast.literal_eval() or structured data serialization (JSON) instead of eval().",
            suggested_fix="import ast\nresult = ast.literal_eval(safe_input)"
        )

