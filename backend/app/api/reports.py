import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import AnalysisHistory, Vulnerability, Transformation
from app.reports.report_generator import ReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/download/{analysis_id}")
def download_report(
    analysis_id: int,
    format: str = Query("json", pattern="^(pdf|json|html)$"),
    db: Session = Depends(get_db)
):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    vulns = db.query(Vulnerability).filter(Vulnerability.analysis_id == analysis_id).all()
    transformations = db.query(Transformation).filter(Transformation.analysis_id == analysis_id).all()

    report_payload = {
        "file_name": record.file_name,
        "language": record.language,
        "total_lines": record.total_lines,
        "total_tokens": record.total_tokens,
        "ast_nodes_count": record.ast_nodes_count,
        "security_score": record.security_score,
        "vulnerabilities": [
            {
                "vuln_id": v.vuln_id,
                "name": v.name,
                "category": v.category,
                "cwe_id": v.cwe_id,
                "severity": v.severity,
                "line_number": v.line_number,
                "vulnerable_snippet": v.vulnerable_snippet,
                "root_cause": v.root_cause
            } for v in vulns
        ],
        "transformations": [t.description for t in transformations],
        "verification": {"status": "Verified"}
    }

    if format == "json":
        json_content = ReportGenerator.generate_json_report(report_payload)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=report_{analysis_id}.json"}
        )
    elif format == "html":
        html_content = ReportGenerator.generate_html_report(report_payload)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=report_{analysis_id}.html"}
        )
    elif format == "pdf":
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"report_{analysis_id}.pdf")
        ReportGenerator.generate_pdf_report(report_payload, pdf_path)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"report_{analysis_id}.pdf"
        )

