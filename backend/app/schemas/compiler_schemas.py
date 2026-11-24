from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Lexical & Syntax ---
class TokenItem(BaseModel):
    value: str
    type: str
    line: int
    column: int
    classification: str  # Keyword, Identifier, Operator, Literal, Delimiter, Comment

class ASTNodeItem(BaseModel):
    id: str
    type: str
    label: str
    line: Optional[int] = None
    column: Optional[int] = None
    children: List['ASTNodeItem'] = []
    properties: Dict[str, Any] = {}

ASTNodeItem.model_rebuild()

# --- Semantic ---
class SymbolItem(BaseModel):
    name: str
    symbol_type: str  # variable, function, parameter, class
    scope: str
    declared_line: int
    data_type: Optional[str] = "unknown"
    is_used: bool = False
    is_initialized: bool = True

class ScopeItem(BaseModel):
    id: str
    name: str
    level: int
    parent_id: Optional[str] = None
    symbols: List[str] = []

class SemanticIssueItem(BaseModel):
    issue_type: str  # UndefinedVariable, UnusedVariable, UnreachableCode, TypeMismatch
    severity: str    # Error, Warning, Info
    message: str
    line: int
    column: Optional[int] = None

class SemanticResult(BaseModel):
    symbols: List[SymbolItem] = []
    scopes: List[ScopeItem] = []
    undefined_variables: List[str] = []
    unused_variables: List[str] = []
    unreachable_lines: List[int] = []
    type_warnings: List[str] = []
    issues: List[SemanticIssueItem] = []

# --- Intermediate Representation & CFG ---
class IRInstructionItem(BaseModel):
    index: int
    opcode: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None
    line: Optional[int] = None
    comment: Optional[str] = None

class BasicBlockItem(BaseModel):
    id: str
    label: str
    instructions: List[IRInstructionItem] = []
    predecessors: List[str] = []
    successors: List[str] = []

class CFGEdgeItem(BaseModel):
    from_block: str
    to_block: str
    label: Optional[str] = None

class CFGResult(BaseModel):
    entry_block: str
    exit_blocks: List[str] = []
    blocks: List[BasicBlockItem] = []
    edges: List[CFGEdgeItem] = []

# --- Analysis Request & Response ---
class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"  # python, c, java
    file_name: Optional[str] = "untitled.py"
    project_id: Optional[int] = None

class CodeAnalysisResponse(BaseModel):
    analysis_id: Optional[int] = None
    file_name: str
    language: str
    total_lines: int
    total_tokens: int
    ast_nodes_count: int
    functions_count: int
    variables_count: int
    syntax_valid: bool
    syntax_errors: List[str] = []
    parsing_time_ms: float
    status: str
    tokens: List[TokenItem] = []
    ast: Optional[ASTNodeItem] = None
    semantic: SemanticResult
    ir_instructions: List[IRInstructionItem] = []
    basic_blocks: List[BasicBlockItem] = []
    cfg: CFGResult

# --- Vulnerability ---
class VulnerabilityItem(BaseModel):
    id: Optional[int] = None
    vuln_id: str
    name: str
    category: str
    cwe_id: Optional[str] = None
    cwe_name: Optional[str] = None
    severity: str  # Critical, High, Medium, Low, Informational
    confidence: str = "High"
    line_number: int
    end_line_number: Optional[int] = None
    vulnerable_snippet: str
    root_cause: str
    attack_scenario: str
    security_impact: str
    recommended_solution: str
    suggested_fix: str
    is_transformed: bool = False

class SecurityScanResponse(BaseModel):
    analysis_id: Optional[int] = None
    security_score: float
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    informational_count: int
    vulnerabilities: List[VulnerabilityItem]
    severity_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    limitations_disclaimer: str

# --- Transformations & Optimization ---
class TransformationRequest(BaseModel):
    analysis_id: Optional[int] = None
    code: str
    language: str = "python"
    vulnerability_ids: Optional[List[str]] = None
    enable_optimizations: bool = True
    optimizations: Optional[List[str]] = [
        "constant_folding",
        "dead_code_elimination",
        "common_subexpression",
        "algebraic_simplification"
    ]

class TransformationExplanation(BaseModel):
    what_changed: str
    why_changed: str
    original_problem: str
    new_implementation: str
    security_benefit: str
    performance_benefit: str
    semantic_verified: bool
    regression_tests_passed: List[str] = []

class DiffLine(BaseModel):
    type: str  # 'same', 'add', 'remove', 'modify'
    original_line_num: Optional[int] = None
    modified_line_num: Optional[int] = None
    content: str

class TransformationResponse(BaseModel):
    transformation_id: Optional[int] = None
    original_code: str
    transformed_code: str
    diff_lines: List[DiffLine] = []
    transformations_applied: List[str] = []
    optimizations_applied: List[str] = []
    is_verified: bool
    verification_status: str
    explanation: TransformationExplanation
    verification_details: Dict[str, Any] = {}

class VerificationRequest(BaseModel):
    original_code: str
    transformed_code: str
    language: str = "python"

class VerificationResponse(BaseModel):
    syntax_valid: bool
    semantic_valid: bool
    regression_passed: bool
    overall_status: str  # Passed, Failed, Rejected
    details: Dict[str, Any]

# --- Testing ---
class TestCaseItem(BaseModel):
    id: Optional[int] = None
    test_id: str
    name: str
    language: str
    category: str
    description: Optional[str] = None
    source_code: str
    expected_detection: Optional[str] = None
    expected_severity: Optional[str] = None
    expected_verification: Optional[str] = "Passed"
    last_status: Optional[str] = None
    last_executed_at: Optional[datetime] = None

class TestRunResult(BaseModel):
    test_id: str
    name: str
    language: str
    category: str
    status: str  # Passed, Failed, Skipped
    expected_detection: Optional[str] = None
    actual_detection: Optional[str] = None
    expected_severity: Optional[str] = None
    actual_severity: Optional[str] = None
    execution_time_ms: float
    error_message: Optional[str] = None
    passed: bool

class TestSuiteSummary(BaseModel):
    total_tests: int
    passed: int
    failed: int
    skipped: int
    success_percentage: float
    average_execution_time_ms: float
    results: List[TestRunResult]

# --- Dashboard & Reports ---
class DashboardStats(BaseModel):
    total_analyzed_projects: int
    total_source_files: int
    total_vulnerabilities: int
    average_security_score: float
    critical_vulns_count: int
    high_vulns_count: int
    medium_vulns_count: int
    low_vulns_count: int
    tests_summary: Dict[str, Any]
    language_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    recent_analyses: List[Dict[str, Any]]

