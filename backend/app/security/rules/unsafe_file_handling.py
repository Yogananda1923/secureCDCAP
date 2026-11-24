import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class UnsafeFileHandlingRule:
    """
    Detects Insecure Temporary File Creation (CWE-377),
    Improper Exception Handling / Silent Failure (CWE-703/CWE-391),
    and Overly Permissive Resource Assignment (CWE-732).
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class FileHandlingVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                call_name = ""
                if isinstance(node.func, ast.Attribute):
                    obj = getattr(node.func.value, 'id', '')
                    call_name = f"{obj}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id

                # 1. tempfile.mktemp()
                if call_name == "tempfile.mktemp" or call_name == "mktemp":
                    vulns.append(VulnerabilityItem(
                        vuln_id="SEC-GEN-002",
                        name="Insecure Temporary File Creation (Race Condition)",
                        category="General Security",
                        cwe_id="CWE-377",
                        cwe_name="Insecure Temporary File",
                        severity="Medium",
                        confidence="High",
                        line_number=line_no,
                        vulnerable_snippet=snippet,
                        root_cause="Use of deprecated tempfile.mktemp() creates a race condition between file name generation and file creation (TOCTOU).",
                        attack_scenario="An attacker creates a symlink at the predicted temporary file path before the program opens it, hijacking access or writing to arbitrary destinations.",
                        security_impact="Symlink attacks, arbitrary file overwrite, privilege escalation.",
                        recommended_solution="Use tempfile.NamedTemporaryFile() or tempfile.mkstemp() which creates files securely with exclusive O_EXCL flags.",
                        suggested_fix="import tempfile\nwith tempfile.NamedTemporaryFile(delete=False) as temp_file:\n    temp_file.write(data)"
                    ))

                # 2. Overly permissive file permissions: chmod 0777
                elif call_name in ("os.chmod", "chmod"):
                    if node.args and len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and mode_arg.value in (0o777, 511, 0o666, 438):
                            vulns.append(VulnerabilityItem(
                                vuln_id="SEC-GEN-003",
                                name="Incorrect Permission Assignment for Critical Resource",
                                category="General Security",
                                cwe_id="CWE-732",
                                cwe_name="Incorrect Permission Assignment for Critical Resource",
                                severity="Medium",
                                confidence="High",
                                line_number=line_no,
                                vulnerable_snippet=snippet,
                                root_cause="Assigning world-readable and world-writable permissions (0777/0666) to files.",
                                attack_scenario="Local untrusted users can read, modify, or tamper with the sensitive files created by the application.",
                                security_impact="Unauthorized file modification, privilege escalation, sensitive data tampering.",
                                recommended_solution="Restrict file permissions to owner-only read/write (0o600 or 0o700).",
                                suggested_fix="os.chmod(filepath, 0o600)"
                            ))

                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                # Check for empty except or except: pass
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    vulns.append(VulnerabilityItem(
                        vuln_id="SEC-GEN-004",
                        name="Improper Exception Handling / Silent Failure",
                        category="General Security",
                        cwe_id="CWE-391",
                        cwe_name="Unchecked Error Condition",
                        severity="Low",
                        confidence="High",
                        line_number=line_no,
                        vulnerable_snippet=snippet,
                        root_cause="Silently swallowing exceptions using 'except: pass' without logging or handling errors.",
                        attack_scenario="Critical security exceptions or database connection failures fail silently, leading to undefined application states or bypass of verification logic.",
                        security_impact="Masked system failures, debugging impedance, security bypass.",
                        recommended_solution="Catch specific exception types, log the error details with logger.exception(), and fail closed.",
                        suggested_fix="except SpecificException as e:\n    logging.error(f'Operation failed: {e}')\n    raise"
                    ))

                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            FileHandlingVisitor().visit(tree)

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # mktemp or tmpnam
            if re.search(r'\b(mktemp|tmpnam)\s*\(', sline):
                vulns.append(VulnerabilityItem(
                    vuln_id="SEC-GEN-002",
                    name="Insecure Temporary File Creation (mktemp/tmpnam)",
                    category="General Security",
                    cwe_id="CWE-377",
                    cwe_name="Insecure Temporary File",
                    severity="Medium",
                    confidence="High",
                    line_number=idx,
                    vulnerable_snippet=sline,
                    root_cause="Use of unsafe mktemp() or tmpnam() vulnerable to race conditions.",
                    attack_scenario="An adversary predicts temporary file names to hijack files before creation.",
                    security_impact="Symlink attacks, arbitrary file overwrite.",
                    recommended_solution="Use mkstemp() which securely creates and opens the temporary file.",
                    suggested_fix="int fd = mkstemp(template_str);"
                ))
            elif re.search(r'chmod\s*\([^,]+,\s*0?777\)', sline):
                vulns.append(VulnerabilityItem(
                    vuln_id="SEC-GEN-003",
                    name="Overly Permissive File Permissions",
                    category="General Security",
                    cwe_id="CWE-732",
                    cwe_name="Incorrect Permission Assignment for Critical Resource",
                    severity="Medium",
                    confidence="High",
                    line_number=idx,
                    vulnerable_snippet=sline,
                    root_cause="File permission set to world writable (0777).",
                    attack_scenario="Local adversaries modify application files.",
                    security_impact="Local privilege escalation.",
                    recommended_solution="Use 0600 (S_IRUSR | S_IWUSR).",
                    suggested_fix="chmod(path, S_IRUSR | S_IWUSR);"
                ))
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'catch\s*\([^\)]+\)\s*\{\s*\}', sline):
                vulns.append(VulnerabilityItem(
                    vuln_id="SEC-GEN-004",
                    name="Empty Catch Block / Silent Exception Suppression",
                    category="General Security",
                    cwe_id="CWE-391",
                    cwe_name="Unchecked Error Condition",
                    severity="Low",
                    confidence="High",
                    line_number=idx,
                    vulnerable_snippet=sline,
                    root_cause="Empty catch block catches and ignores exceptions silently.",
                    attack_scenario="Suppressed security exceptions prevent audit trails and lead to corrupted program state.",
                    security_impact="Masked failures and bypassed security constraints.",
                    recommended_solution="Log exceptions or rethrow handled exceptions.",
                    suggested_fix="catch (Exception e) {\n    logger.error(\"Operation failed\", e);\n    throw e;\n}"
                ))
        return vulns

