from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.db_models import AnalysisHistory, Vulnerability, Transformation

router = APIRouter(prefix="/history", tags=["History"])

@router.get("")
def get_analysis_history(db: Session = Depends(get_db)):
    records = db.query(AnalysisHistory).order_by(AnalysisHistory.created_at.desc()).limit(50).all()
    results = []
    for r in records:
        vuln_count = db.query(Vulnerability).filter(Vulnerability.analysis_id == r.id).count()
        results.append({
            "id": r.id,
            "file_name": r.file_name,
            "language": r.language,
            "total_lines": r.total_lines,
            "total_tokens": r.total_tokens,
            "ast_nodes_count": r.ast_nodes_count,
            "security_score": r.security_score,
            "syntax_valid": r.syntax_valid,
            "status": r.status,
            "parsing_time_ms": r.parsing_time_ms,
            "vulnerabilities_count": vuln_count,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return results

@router.get("/{analysis_id}")
def get_analysis_detail(analysis_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    vulns = db.query(Vulnerability).filter(Vulnerability.analysis_id == analysis_id).all()
    transformations = db.query(Transformation).filter(Transformation.analysis_id == analysis_id).all()

    return {
        "id": record.id,
        "file_name": record.file_name,
        "language": record.language,
        "source_code": record.source_code,
        "total_lines": record.total_lines,
        "total_tokens": record.total_tokens,
        "ast_nodes_count": record.ast_nodes_count,
        "functions_count": record.functions_count,
        "variables_count": record.variables_count,
        "security_score": record.security_score,
        "syntax_valid": record.syntax_valid,
        "parsing_time_ms": record.parsing_time_ms,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "tokens_data": record.tokens_data,
        "ast_data": record.ast_data,
        "semantic_data": record.semantic_data,
        "ir_data": record.ir_data,
        "cfg_data": record.cfg_data,
        "vulnerabilities": [
            {
                "id": v.id,
                "vuln_id": v.vuln_id,
                "name": v.name,
                "category": v.category,
                "cwe_id": v.cwe_id,
                "cwe_name": v.cwe_name,
                "severity": v.severity,
                "confidence": v.confidence,
                "line_number": v.line_number,
                "vulnerable_snippet": v.vulnerable_snippet,
                "root_cause": v.root_cause,
                "attack_scenario": v.attack_scenario,
                "security_impact": v.security_impact,
                "recommended_solution": v.recommended_solution,
                "suggested_fix": v.suggested_fix
            } for v in vulns
        ],
        "transformations": [
            {
                "id": t.id,
                "description": t.description,
                "original_code": t.original_code,
                "transformed_code": t.transformed_code,
                "diff_data": t.diff_data,
                "is_verified": t.is_verified,
                "verification_status": t.verification_status,
                "explanation": t.explanation,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in transformations
        ]
    }

@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    db.delete(record)
    db.commit()
    return {"message": f"Analysis {analysis_id} deleted successfully."}

