from typing import Dict, Any
from app.verification.syntax_verifier import SyntaxVerifier
from app.verification.semantic_verifier import SemanticVerifier
from app.security.vulnerability_engine import VulnerabilityEngine
from app.compiler.parser import ParserEngine
from app.schemas.compiler_schemas import VerificationResponse

class RegressionVerifier:
    """
    Automated Regression Verification Engine.
    Executes multi-stage verification pipeline whenever a transformation or optimization is applied:
      Stage 1: Syntax Validation
      Stage 2: Semantic Equivalence & Symbol Preservation
      Stage 3: Security Regression & Vulnerability Mitigation Verification
    """

    @classmethod
    def run_verification(cls, original_code: str, transformed_code: str, language: str = "python") -> VerificationResponse:
        details: Dict[str, Any] = {}

        # Stage 1: Syntax Validation
        syntax_valid, syntax_errors = SyntaxVerifier.verify(transformed_code, language)
        details["syntax_valid"] = syntax_valid
        details["syntax_errors"] = syntax_errors
        if not syntax_valid:
            return VerificationResponse(
                syntax_valid=False,
                semantic_valid=False,
                regression_passed=False,
                overall_status="Rejected",
                details={
                    "stage": "Syntax Validation",
                    "reason": f"Syntax errors detected in transformed code: {syntax_errors}",
                    **details
                }
            )

        # Stage 2: Semantic Verification
        semantic_valid, semantic_notes, sem_details = SemanticVerifier.verify(original_code, transformed_code, language)
        details["semantic_valid"] = semantic_valid
        details["semantic_notes"] = semantic_notes
        details.update(sem_details)
        if not semantic_valid:
            return VerificationResponse(
                syntax_valid=True,
                semantic_valid=False,
                regression_passed=False,
                overall_status="Rejected",
                details={
                    "stage": "Semantic Verification",
                    "reason": f"Semantic integrity check failed: {'; '.join(semantic_notes)}",
                    **details
                }
            )

        # Stage 3: Security Regression Verification
        # Check original vs transformed vulnerabilities
        _, orig_ast, _ = ParserEngine.parse(original_code, language)
        _, trans_ast, _ = ParserEngine.parse(transformed_code, language)

        orig_scan = VulnerabilityEngine.scan(orig_ast, original_code, language)
        trans_scan = VulnerabilityEngine.scan(trans_ast, transformed_code, language)

        details["original_score"] = orig_scan.security_score
        details["transformed_score"] = trans_scan.security_score
        details["original_vulnerabilities_count"] = orig_scan.total_vulnerabilities
        details["transformed_vulnerabilities_count"] = trans_scan.total_vulnerabilities
        details["mitigated_vulnerabilities"] = orig_scan.total_vulnerabilities - trans_scan.total_vulnerabilities

        regression_passed = trans_scan.security_score >= orig_scan.security_score
        details["regression_passed"] = regression_passed

        overall_status = "Passed" if regression_passed else "Warning"

        return VerificationResponse(
            syntax_valid=True,
            semantic_valid=True,
            regression_passed=regression_passed,
            overall_status=overall_status,
            details=details
        )

