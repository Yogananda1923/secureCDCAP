import pytest
import sys
import os

# Add backend directory to sys.path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.compiler.lexer import LexerEngine
from app.compiler.parser import ParserEngine
from app.compiler.ast_analyzer import ASTAnalyzer
from app.compiler.semantic_analyzer import SemanticAnalyzer
from app.compiler.intermediate_representation import IRGenerator
from app.compiler.control_flow import CFGBuilder
from app.security.vulnerability_engine import VulnerabilityEngine
from app.optimizer.secure_transformations import SecureTransformer
from app.verification.regression_verifier import RegressionVerifier
from app.testing.test_runner import TestRunnerEngine
from app.testing.test_registry import PREDEFINED_TEST_CASES

def test_lexer_tokenization():
    code = "def add(x, y):\n    return x + y # sum"
    tokens, metrics = LexerEngine.tokenize(code, "python")
    assert len(tokens) > 0
    assert metrics["keywords"] >= 2  # def, return
    assert metrics["comments"] >= 1

def test_parser_and_ast_python():
    code = "x = 42\ny = x + 1"
    is_valid, raw_ast, errors = ParserEngine.parse(code, "python")
    assert is_valid is True
    assert raw_ast is not None
    tree, node_count = ASTAnalyzer.to_tree(raw_ast, "python")
    assert node_count > 0
    assert tree.type == "Module"

def test_semantic_analysis():
    code = """
def test_func():
    a = 10
    b = 20
    return a
    unreachable_var = 30
"""
    is_valid, raw_ast, _ = ParserEngine.parse(code, "python")
    semantic = SemanticAnalyzer.analyze(raw_ast, code, "python")
    assert "b" in semantic.unused_variables
    assert len(semantic.unreachable_lines) > 0

def test_ir_and_cfg_generation():
    code = """
def check(val):
    if val > 10:
        return True
    return False
"""
    is_valid, raw_ast, _ = ParserEngine.parse(code, "python")
    ir = IRGenerator.generate(raw_ast, code, "python")
    assert len(ir) > 0
    cfg = CFGBuilder.build(ir)
    assert len(cfg.blocks) >= 2
    assert len(cfg.edges) >= 1

def test_security_vulnerability_detection():
    vuln_code = """
import os
def execute_query(cursor, user_id):
    cursor.execute(f"SELECT * FROM accounts WHERE id = '{user_id}'")
    os.system("echo 'logged'")
"""
    is_valid, raw_ast, _ = ParserEngine.parse(vuln_code, "python")
    scan = VulnerabilityEngine.scan(raw_ast, vuln_code, "python")
    assert scan.total_vulnerabilities >= 2
    vuln_names = [v.name for v in scan.vulnerabilities]
    assert any("SQL Injection" in name for name in vuln_names)
    assert any("Command Injection" in name for name in vuln_names)
    assert scan.security_score < 70

def test_secure_transformation():
    vuln_code = """
def get_user(cursor, username):
    cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
"""
    transformed, fixes, opts, diff_lines, explanation = SecureTransformer.transform(vuln_code, "python")
    assert "?" in transformed
    assert len(fixes) > 0
    assert len(diff_lines) > 0

def test_regression_verifier():
    orig_code = 'cursor.execute(f"SELECT * FROM users WHERE id = \'{user_id}\'")'
    fixed_code = 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
    verif = RegressionVerifier.run_verification(orig_code, fixed_code, "python")
    assert verif.syntax_valid is True
    assert verif.overall_status in ("Passed", "Warning")

def test_predefined_test_cases_count():
    assert len(PREDEFINED_TEST_CASES) >= 30
    py_cases = [t for t in PREDEFINED_TEST_CASES if t["language"] == "python"]
    c_cases = [t for t in PREDEFINED_TEST_CASES if t["language"] == "c"]
    java_cases = [t for t in PREDEFINED_TEST_CASES if t["language"] == "java"]
    assert len(py_cases) >= 10
    assert len(c_cases) >= 10
    assert len(java_cases) >= 10

def test_test_runner_execution():
    summary = TestRunnerEngine.run_all(language="python")
    assert summary.total_tests >= 10
    assert summary.passed > 0
    assert summary.success_percentage >= 80.0

