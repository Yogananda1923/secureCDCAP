import ast
import re
from typing import List
from app.schemas.compiler_schemas import VulnerabilityItem

class SQLInjectionRule:
    """
    Detects SQL Injection (CWE-89) across Python, C, and Java.
    Identifies dynamic SQL string concatenation, f-strings, format specifiers,
    or string addition directly used in query execution sinks.
    """

    @staticmethod
    def scan_python(tree: ast.AST, code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()

        class SQLVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id

                # Common database execution sinks
                if func_name in ("execute", "executemany", "raw", "raw_query"):
                    if node.args:
                        arg0 = node.args[0]
                        line_no = getattr(node, 'lineno', 1)
                        snippet = lines[line_no - 1].strip() if line_no <= len(lines) else "cursor.execute(...)"

                        # Check for f-string: f"SELECT ... {user_input}"
                        if isinstance(arg0, ast.JoinedStr):
                            vulns.append(SQLInjectionRule._create_vuln(
                                line_no=line_no,
                                snippet=snippet,
                                sink="JoinedStr (f-string in cursor.execute)",
                                suggested_fix="cursor.execute(\"SELECT * FROM users WHERE username = ?\", (username,))"
                            ))
                        # Check for binary string concatenation: "SELECT ... " + user_input
                        elif isinstance(arg0, ast.BinOp) and isinstance(arg0.op, (ast.Add, ast.Mod)):
                            vulns.append(SQLInjectionRule._create_vuln(
                                line_no=line_no,
                                snippet=snippet,
                                sink=f"BinOp ({type(arg0.op).__name__} string interpolation)",
                                suggested_fix="cursor.execute(\"SELECT * FROM users WHERE username = ?\", (username,))"
                            ))
                        # Check for .format() call: "SELECT ... {}".format(user_input)
                        elif isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Attribute) and arg0.func.attr == "format":
                            vulns.append(SQLInjectionRule._create_vuln(
                                line_no=line_no,
                                snippet=snippet,
                                sink="str.format() in query sink",
                                suggested_fix="cursor.execute(\"SELECT * FROM users WHERE username = ?\", (username,))"
                            ))
                self.generic_visit(node)

        if isinstance(tree, ast.AST):
            SQLVisitor().visit(tree)

        # Fallback check for queries constructed and passed
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            if re.search(r'execute\s*\(\s*f["\'](SELECT|INSERT|UPDATE|DELETE|DROP)', sline, re.IGNORECASE):
                if not any(v.line_number == idx for v in vulns):
                    vulns.append(SQLInjectionRule._create_vuln(
                        line_no=idx,
                        snippet=sline,
                        sink="f-string query execution",
                        suggested_fix="cursor.execute(\"SELECT ... WHERE id = ?\", (user_id,))"
                    ))

        return vulns

    @staticmethod
    def scan_c(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # sprintf(query, "SELECT * FROM users WHERE id = '%s'", input);
            if re.search(r'sprintf\s*\([^,]+,\s*["\'].*(SELECT|INSERT|UPDATE|DELETE).*%s', sline, re.IGNORECASE) or \
               re.search(r'sqlite3_exec\s*\([^,]+,\s*query', sline, re.IGNORECASE) and 'sprintf' in code:
                vulns.append(SQLInjectionRule._create_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="sprintf formatting into SQL query buffer",
                    suggested_fix="sqlite3_prepare_v2(db, \"SELECT * FROM users WHERE id = ?\", -1, &stmt, NULL);\nsqlite3_bind_text(stmt, 1, input, -1, SQLITE_STATIC);"
                ))
        return vulns

    @staticmethod
    def scan_java(code: str, file_name: str) -> List[VulnerabilityItem]:
        vulns: List[VulnerabilityItem] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            sline = line.strip()
            # statement.executeQuery("SELECT ... " + input)
            if re.search(r'(executeQuery|executeUpdate)\s*\(\s*["\'].*(SELECT|INSERT|UPDATE|DELETE).*["\']\s*\+', sline, re.IGNORECASE) or \
               re.search(r'(executeQuery|executeUpdate)\s*\(\s*query\s*\)', sline) and ('+ username' in code or '+ id' in code or '+ input' in code):
                vulns.append(SQLInjectionRule._create_vuln(
                    line_no=idx,
                    snippet=sline,
                    sink="Dynamic SQL string concatenation in Statement.executeQuery()",
                    suggested_fix="PreparedStatement pstmt = conn.prepareStatement(\"SELECT * FROM users WHERE username = ?\");\npstmt.setString(1, username);\nResultSet rs = pstmt.executeQuery();"
                ))
        return vulns

    @staticmethod
    def _create_vuln(line_no: int, snippet: str, sink: str, suggested_fix: str) -> VulnerabilityItem:
        return VulnerabilityItem(
            vuln_id="SEC-INJ-001",
            name="SQL Injection (Improper Neutralization of Special Elements used in an SQL Command)",
            category="Injection",
            cwe_id="CWE-89",
            cwe_name="Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
            severity="Critical",
            confidence="High",
            line_number=line_no,
            vulnerable_snippet=snippet,
            root_cause=f"Direct concatenation of untrusted input into SQL query string at sink: {sink}.",
            attack_scenario="An adversary enters ' OR '1'='1' or ' UNION SELECT username, password FROM users -- into input fields to bypass authentication or extract sensitive database tables.",
            security_impact="Unauthorized database access, complete data exfiltration, authentication bypass, data destruction.",
            recommended_solution="Replace dynamic SQL string concatenation with parameterized prepared statements or query bindings.",
            suggested_fix=suggested_fix
        )

