import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

SECRET_KEYWORDS = {
    'password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey', 'auth_token',
    'access_token', 'private_key', 'secret_key', 'client_secret', 'bearer_token'
}

class HardcodedSecretsRule:
    """
    Detects Hardcoded Credentials and Secrets (CWE-798).
    Analyzes variable assignments, constant literals, and configuration blocks
    for sensitive credentials embedded directly into source code.
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class SecretVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                for target in node.targets:
                    var_name = ""
                    if isinstance(target, ast.Name):
                        var_name = target.id
                    elif isinstance(target, ast.Attribute):
                        var_name = target.attr

                    norm_name = var_name.lower().replace("-", "_")
                    if any(sk in norm_name for sk in SECRET_KEYWORDS):
                        # Check if RHS is a non-empty string literal
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            val = node.value.value.strip()
                            if len(val) >= 4 and not val.startswith("ENV_") and not val.startswith("${"):
                                env_var_name = var_name.upper()
                                fix = f"{var_name} = os.getenv('{env_var_name}')"
                                vulns.append(HardcodedSecretsRule._create_vuln(
                                    line_no=line_no,
                                    snippet=snippet,
                                    var_name=var_name,
                                    suggested_fix=fix
                                ))
                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            SecretVisitor().visit(tree)

        # Regex fallback scan
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            for kw in SECRET_KEYWORDS:
                pattern = rf'\b{kw}\b\s*=\s*["\']([^"\']{{5,}})["\']'
                match = re.search(pattern, sline, re.IGNORECASE)
                if match and not any(v.line_number == idx for v in vulns):
                    var_name = kw
                    fix = f"{var_name} = os.getenv('{var_name.upper()}')"
                    vulns.append(HardcodedSecretsRule._create_vuln(
                        line_no=idx,
                        snippet=sline,
                        var_name=var_name,
                        suggested_fix=fix
                    ))
                    break

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            for kw in SECRET_KEYWORDS:
                pattern = rf'\b{kw}\b\s*(\[[^\]]*\])?\s*=\s*["\']([^"\']{{4,}})["\']'
                if re.search(pattern, sline, re.IGNORECASE):
                    vulns.append(HardcodedSecretsRule._create_vuln(
                        line_no=idx,
                        snippet=sline,
                        var_name=kw,
                        suggested_fix=f"const char *{kw} = getenv(\"{kw.upper()}\");\nif (!{kw}) {{ /* handle missing secret */ }}"
                    ))
                    break
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            for kw in SECRET_KEYWORDS:
                pattern = rf'\b{kw}\b\s*=\s*["\']([^"\']{{4,}})["\']'
                if re.search(pattern, sline, re.IGNORECASE):
                    vulns.append(HardcodedSecretsRule._create_vuln(
                        line_no=idx,
                        snippet=sline,
                        var_name=kw,
                        suggested_fix=f"String {kw} = System.getenv(\"{kw.upper()}\");\nif ({kw} == null) {{ throw new IllegalStateException(\"Missing {kw.upper()}\"); }}"
                    ))
                    break
        return vulns

    @staticmethod
    def _create_vuln(line_no: int, snippet: str, var_name: str, suggested_fix: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-AUTH-001",
            name="Hardcoded Credentials / Sensitive Data in Source Code",
            category="Authentication & Cryptography",
            cwe_id="CWE-798",
            cwe_name="Use of Hard-coded Credentials",
            severity="High",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Sensitive secret or credential '{var_name}' stored directly in cleartext in the application source code.",
            attack_scenario="An attacker with repository read access, decompiled binaries, or leaked logs extracts the hardcoded credential to gain unauthorized administrative access.",
            security_impact="Credential compromise, unauthorized privileged access, loss of confidentiality across connected systems.",
            recommended_solution="Store sensitive credentials in secure environment variables or dedicated secret management services (e.g., Vault, AWS Secrets Manager, GCP Secret Manager).",
            suggested_fix=suggested_fix
        )

