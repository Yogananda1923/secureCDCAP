import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class InputValidationRule:
    """
    Detects Deserialization of Untrusted Data (CWE-502) and
    Improper Input Validation (CWE-20).
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class DeserVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                call_name = ""
                if isinstance(node.func, ast.Attribute):
                    obj = getattr(node.func.value, 'id', '')
                    call_name = f"{obj}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id

                # 1. pickle.loads or pickle.load
                if call_name in ("pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"):
                    vulns.append(InputValidationRule._create_pickle_vuln(line_no, snippet, call_name))
                # 2. yaml.load without SafeLoader
                elif call_name == "yaml.load":
                    has_safe_loader = False
                    for kw in node.keywords:
                        if kw.arg == "Loader":
                            loader_str = ast.unparse(kw.value) if hasattr(ast, 'unparse') else ""
                            if "SafeLoader" in loader_str or "CSafeLoader" in loader_str:
                                has_safe_loader = True
                    if not has_safe_loader and len(node.args) == 1:
                        vulns.append(InputValidationRule._create_pickle_vuln(line_no, snippet, "yaml.load() without SafeLoader"))

                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            DeserVisitor().visit(tree)

        # Regex fallback scan
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'pickle\.(loads|load)\s*\(', sline) and not any(v.line_number == idx for v in vulns):
                vulns.append(InputValidationRule._create_pickle_vuln(idx, sline, "pickle.loads"))

        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # ObjectInputStream.readObject()
            if re.search(r'\breadObject\s*\(\s*\)', sline):
                vulns.append(InputValidationRule._create_pickle_vuln(
                    idx, sline, "ObjectInputStream.readObject()"
                ))
        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        # C deserialization or unvalidated input
        vulns: List[VulnerabilityItem] = []
        return vulns

    @staticmethod
    def _create_pickle_vuln(line_no: int, snippet: str, sink: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-INP-001",
            name="Deserialization of Untrusted Data (Arbitrary Code Execution via Deserialization)",
            category="Input Validation",
            cwe_id="CWE-502",
            cwe_name="Deserialization of Untrusted Data",
            severity="Critical",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Deserializing untrusted serialized stream using {sink}.",
            attack_scenario="An attacker provides a crafted pickled/serialized object containing __reduce__ magic method payloads that trigger os.system execution upon deserialization.",
            security_impact="Immediate arbitrary remote code execution, server takeover.",
            recommended_solution="Never deserialize untrusted data with pickle or raw object streams. Use structured, safe data interchange formats such as JSON or Protocol Buffers.",
            suggested_fix="import json\ndata = json.loads(untrusted_payload)"
        )

