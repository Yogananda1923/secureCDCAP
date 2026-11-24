import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class PathTraversalRule:
    """
    Detects Path Traversal Vulnerabilities (CWE-22).
    Identifies unvalidated relative paths ('..', dot-dot-slash) constructed with
    user inputs and passed into file system APIs.
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class PathVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                call_name = ""
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    obj = getattr(node.func.value, 'id', '')
                    call_name = f"{obj}.{node.func.attr}"

                if call_name in ("open", "os.path.join"):
                    # Check if any argument is derived from request/input or concatenated
                    if any(isinstance(a, ast.BinOp) and isinstance(a.op, ast.Add) for a in node.args) or \
                       any(isinstance(a, ast.JoinedStr) for a in node.args):
                        if any(term in snippet.lower() for term in ("filename", "path", "file", "user_file", "doc")):
                            vulns.append(PathTraversalRule._create_vuln(line_no, snippet))

                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            PathVisitor().visit(tree)

        # Regex fallback scan
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'open\s*\(\s*["\'].*["\']\s*\+\s*(filename|file|path|user_input)', sline, re.IGNORECASE) or \
               re.search(r'open\s*\(\s*f["\'].*\{(filename|file|path|user_input)\}', sline, re.IGNORECASE):
                if not any(v.line_number == idx for v in vulns):
                    vulns.append(PathTraversalRule._create_vuln(idx, sline))

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'fopen\s*\(\s*(filename|filepath|user_input|input)', sline, re.IGNORECASE) and not 'realpath' in code:
                vulns.append(PathTraversalRule._create_vuln(idx, sline))
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'new\s+File\s*\([^,]+,\s*(filename|path|userInput)', sline, re.IGNORECASE) and not 'getCanonicalPath' in code:
                vulns.append(PathTraversalRule._create_vuln(idx, sline))
        return vulns

    @staticmethod
    def _create_vuln(line_no: int, snippet: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-GEN-001",
            name="Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
            category="General Security",
            cwe_id="CWE-22",
            cwe_name="Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
            severity="High",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause="File path opened or constructed directly from user input without path normalization or canonical directory boundary validation.",
            attack_scenario="An adversary supplies '../../../../etc/passwd' or '..\\..\\windows\\system.ini' to access arbitrary restricted files outside the intended directory.",
            security_impact="Unauthorized file disclosure, overwriting sensitive configuration files, arbitrary data manipulation.",
            recommended_solution="Canonicalize and validate paths using safe path resolving: ensure target path starts with base directory, or use os.path.basename().",
            suggested_fix="import os\nsafe_filename = os.path.basename(user_input)\nfilepath = os.path.join('/safe/dir', safe_filename)"
        )

