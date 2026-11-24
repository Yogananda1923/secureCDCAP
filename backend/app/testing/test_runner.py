import time
from typing import List, Optional, Dict, Any
from app.compiler.parser import ParserEngine
from app.security.vulnerability_engine import VulnerabilityEngine
from app.testing.test_registry import PREDEFINED_TEST_CASES
from app.schemas.compiler_schemas import TestRunResult, TestSuiteSummary

class TestRunnerEngine:
    """
    Automated Test Runner for Compiler Security & Verification Suite.
    Runs test cases against genuine compiler and semantic vulnerability engines,
    validating detections, classifications, and execution timings.
    """

    @classmethod
    def run_test(cls, test_case: Dict[str, Any]) -> TestRunResult:
        start_time = time.perf_counter()

        test_id = test_case["test_id"]
        name = test_case["name"]
        lang = test_case["language"]
        cat = test_case["category"]
        code = test_case["source_code"]
        expected_det = test_case.get("expected_detection", "Clean")
        expected_sev = test_case.get("expected_severity", "None")

        error_message = None
        actual_det = "Clean"
        actual_sev = "None"
        passed = False

        try:
            # 1. Parse code
            is_valid, ast_tree, parse_errors = ParserEngine.parse(code, lang)
            
            # 2. Run Vulnerability Engine scan
            scan_res = VulnerabilityEngine.scan(ast_tree, code, lang, file_name=f"{test_id}_{lang}")

            if scan_res.vulnerabilities:
                # Find most critical vulnerability
                top_vuln = scan_res.vulnerabilities[0]
                actual_det = top_vuln.name
                actual_sev = top_vuln.severity
                
                # Check if any detected vulnerability matches expected
                matched = False
                for v in scan_res.vulnerabilities:
                    if expected_det.lower() in v.name.lower() or expected_det.lower() in v.category.lower():
                        actual_det = v.name
                        actual_sev = v.severity
                        matched = True
                        break

                if expected_det == "Clean":
                    passed = False
                    error_message = f"Expected clean code, but found {len(scan_res.vulnerabilities)} vulnerabilities (top: {actual_det})"
                else:
                    passed = matched
                    if not passed:
                        error_message = f"Expected detection '{expected_det}', but detected: {[v.name for v in scan_res.vulnerabilities]}"
            else:
                actual_det = "Clean"
                actual_sev = "None"
                if expected_det in ("Clean", "None", ""):
                    passed = True
                else:
                    passed = False
                    error_message = f"Expected '{expected_det}', but no vulnerabilities were flagged by engine"

        except Exception as e:
            passed = False
            error_message = f"Execution exception: {str(e)}"

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return TestRunResult(
            test_id=test_id,
            name=name,
            language=lang,
            category=cat,
            status="Passed" if passed else "Failed",
            expected_detection=expected_det,
            actual_detection=actual_det,
            expected_severity=expected_sev,
            actual_severity=actual_sev,
            execution_time_ms=elapsed_ms,
            error_message=error_message,
            passed=passed
        )

    @classmethod
    def run_all(
        cls,
        language: Optional[str] = None,
        category: Optional[str] = None
    ) -> TestSuiteSummary:
        filtered = PREDEFINED_TEST_CASES
        if language:
            filtered = [t for t in filtered if t["language"].lower() == language.lower()]
        if category:
            filtered = [t for t in filtered if t["category"].lower() == category.lower()]

        results: List[TestRunResult] = []
        total_time = 0.0
        passed_count = 0
        failed_count = 0

        for tc in filtered:
            res = cls.run_test(tc)
            results.append(res)
            total_time += res.execution_time_ms
            if res.passed:
                passed_count += 1
            else:
                failed_count += 1

        total = len(results)
        pct = round((passed_count / total * 100.0) if total > 0 else 0.0, 1)
        avg_time = round((total_time / total) if total > 0 else 0.0, 2)

        return TestSuiteSummary(
            total_tests=total,
            passed=passed_count,
            failed=failed_count,
            skipped=0,
            success_percentage=pct,
            average_execution_time_ms=avg_time,
            results=results
        )

    @classmethod
    def run_by_id(cls, test_id: str) -> Optional[TestRunResult]:
        for tc in PREDEFINED_TEST_CASES:
            if tc["test_id"].upper() == test_id.upper():
                return cls.run_test(tc)
        return None

