from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.testing.test_registry import PREDEFINED_TEST_CASES
from app.testing.test_runner import TestRunnerEngine
from app.schemas.compiler_schemas import (
    TestCaseItem,
    TestRunResult,
    TestSuiteSummary
)

router = APIRouter(prefix="/tests", tags=["Test Management"])

class RunSingleTestRequest(BaseModel):
    test_id: str

class RunAllTestsRequest(BaseModel):
    language: Optional[str] = None
    category: Optional[str] = None

@router.get("", response_model=List[TestCaseItem])
def list_test_cases():
    test_items = []
    for tc in PREDEFINED_TEST_CASES:
        test_items.append(TestCaseItem(
            test_id=tc["test_id"],
            name=tc["name"],
            language=tc["language"],
            category=tc["category"],
            description=tc.get("description"),
            source_code=tc["source_code"],
            expected_detection=tc.get("expected_detection"),
            expected_severity=tc.get("expected_severity"),
            expected_verification=tc.get("expected_verification", "Passed")
        ))
    return test_items

@router.post("/run", response_model=TestRunResult)
def run_single_test(request: RunSingleTestRequest):
    result = TestRunnerEngine.run_by_id(request.test_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Test case '{request.test_id}' not found.")
    return result

@router.post("/run-all", response_model=TestSuiteSummary)
def run_all_tests(request: RunAllTestsRequest):
    return TestRunnerEngine.run_all(
        language=request.language,
        category=request.category
    )

