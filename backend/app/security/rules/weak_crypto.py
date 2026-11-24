import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class WeakCryptoRule:
    """
    Detects Use of Broken or Risky Cryptographic Algorithms (CWE-327 / CWE-328)
    and Insecure Random Number Generators (CWE-330).
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class CryptoVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                line_no = getattr(node, 'lineno', 1)
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else ""

                call_name = ""
                if isinstance(node.func, ast.Attribute):
                    obj = getattr(node.func.value, 'id', '')
                    call_name = f"{obj}.{node.func.attr}"
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id

                # 1. Weak Hashing: hashlib.md5 or hashlib.sha1 or hashlib.new('md5')
                if call_name in ("hashlib.md5", "hashlib.sha1", "md5", "sha1"):
                    vulns.append(WeakCryptoRule._create_hash_vuln(line_no, snippet, call_name))
                elif call_name == "hashlib.new" and node.args:
                    if isinstance(node.args[0], ast.Constant) and str(node.args[0].value).lower() in ("md5", "sha1"):
                        vulns.append(WeakCryptoRule._create_hash_vuln(line_no, snippet, f"hashlib.new('{node.args[0].value}')"))

                # 2. Insecure Random: random.random(), random.randint(), random.choice() in auth/token contexts
                elif call_name in ("random.random", "random.randint", "random.choice", "random.randrange"):
                    if any(term in snippet.lower() for term in ("token", "key", "auth", "session", "password", "salt", "nonce", "secret")):
                        vulns.append(WeakCryptoRule._create_random_vuln(line_no, snippet, call_name))

                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            CryptoVisitor().visit(tree)

        # Regex fallback scan
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'hashlib\.(md5|sha1)\s*\(', sline) and not any(v.line_number == idx for v in vulns):
                vulns.append(WeakCryptoRule._create_hash_vuln(idx, sline, "hashlib"))
            elif re.search(r'random\.(randint|random|choice)\s*\(', sline) and any(term in sline.lower() for term in ("token", "key", "password", "auth")):
                if not any(v.line_number == idx for v in vulns):
                    vulns.append(WeakCryptoRule._create_random_vuln(idx, sline, "random"))

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # MD5_Init or SHA1_Init or rand() for tokens
            if re.search(r'\b(MD5_Init|SHA1_Init|MD5\(|SHA1\()\b', sline):
                vulns.append(WeakCryptoRule._create_hash_vuln(idx, sline, "C Crypto Lib (MD5/SHA1)"))
            elif re.search(r'\brand\s*\(\s*\)', sline) and any(k in sline.lower() for k in ("token", "key", "secret", "nonce", "id")):
                vulns.append(WeakCryptoRule._create_random_vuln(idx, sline, "rand()"))
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'MessageDigest\.getInstance\s*\(\s*["\'](MD5|SHA-1|SHA1)["\']\s*\)', sline, re.IGNORECASE):
                vulns.append(WeakCryptoRule._create_hash_vuln(idx, sline, "MessageDigest.getInstance('MD5/SHA-1')"))
            elif re.search(r'new\s+Random\s*\(', sline) and any(k in sline.lower() for k in ("token", "key", "otp", "password")):
                vulns.append(WeakCryptoRule._create_random_vuln(idx, sline, "java.util.Random"))
        return vulns

    @staticmethod
    def _create_hash_vuln(line_no: int, snippet: str, sink: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-CRY-001",
            name="Use of Weak or Deprecated Cryptographic Hash Algorithm",
            category="Authentication & Cryptography",
            cwe_id="CWE-328",
            cwe_name="Use of Weak Hash",
            severity="Medium",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Use of cryptographically broken hash function (MD5/SHA-1) via {sink}.",
            attack_scenario="An attacker computes hash collisions or pre-image attacks to forge authentication tokens, digital signatures, or crack hashed passwords using rainbow tables.",
            security_impact="Integrity loss, credential recovery, digital signature forgery.",
            recommended_solution="For password hashing, migrate to Argon2id, bcrypt, or scrypt. For data integrity, migrate to SHA-256 or SHA-512.",
            suggested_fix="import hashlib\nhashed = hashlib.sha256(data.encode()).hexdigest()\n# Or for passwords: from argon2 import PasswordHasher; ph = PasswordHasher()"
        )

    @staticmethod
    def _create_random_vuln(line_no: int, snippet: str, sink: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-CRY-002",
            name="Use of Insufficiently Random Values in Security Context",
            category="Authentication & Cryptography",
            cwe_id="CWE-330",
            cwe_name="Use of Insufficiently Random Values",
            severity="Medium",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Use of predictable pseudo-random generator ({sink}) for security-sensitive tokens.",
            attack_scenario="An adversary predicts internal PRNG state after observing a few generated tokens and predicts future reset tokens or session keys.",
            security_impact="Session hijacking, password reset token prediction, authentication bypass.",
            recommended_solution="Use a cryptographically secure pseudo-random number generator (CSPRNG) such as Python's 'secrets' module or Java's 'SecureRandom'.",
            suggested_fix="import secrets\nsecure_token = secrets.token_hex(32)"
        )

