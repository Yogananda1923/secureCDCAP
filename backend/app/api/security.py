from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.compiler.parser import ParserEngine
from app.security.vulnerability_engine import VulnerabilityEngine
from app.schemas.compiler_schemas import SecurityScanResponse

router = APIRouter(prefix="/security", tags=["Security Verification"])

class SecurityScanRequest(BaseModel):
    code: str
    language: str = "python"
    file_name: Optional[str] = "source_file"

@router.post("/scan", response_model=SecurityScanResponse)
def scan_security(request: SecurityScanRequest):
    code = request.code
    lang = request.language.lower()
    file_name = request.file_name or "source_file"

    if not code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    is_valid, raw_ast, parse_errors = ParserEngine.parse(code, lang)
    scan_result = VulnerabilityEngine.scan(raw_ast, code, lang, file_name)

    return scan_result

