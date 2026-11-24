from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.db_models import AnalysisHistory, Vulnerability, Project
from app.testing.test_registry import PREDEFINED_TEST_CASES
from app.schemas.compiler_schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardStats)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_files = db.query(AnalysisHistory).count()
    total_vulns = db.query(Vulnerability).count()

    avg_score_res = db.query(func.avg(AnalysisHistory.security_score)).scalar()
    avg_score = round(float(avg_score_res), 1) if avg_score_res is not None else 100.0

    critical_count = db.query(Vulnerability).filter(Vulnerability.severity == "Critical").count()
    high_count = db.query(Vulnerability).filter(Vulnerability.severity == "High").count()
    medium_count = db.query(Vulnerability).filter(Vulnerability.severity == "Medium").count()
    low_count = db.query(Vulnerability).filter(Vulnerability.severity == "Low").count()

    # Language distribution
    lang_query = db.query(AnalysisHistory.language, func.count(AnalysisHistory.id)).group_by(AnalysisHistory.language).all()
    lang_dist = {lang: count for lang, count in lang_query}
    if not lang_dist:
        lang_dist = {"python": 0, "c": 0, "java": 0}

    # Severity distribution
    sev_dist = {
        "Critical": critical_count,
        "High": high_count,
        "Medium": medium_count,
        "Low": low_count
    }

    # Recent history
    recent = db.query(AnalysisHistory).order_by(AnalysisHistory.created_at.desc()).limit(8).all()
    recent_list = []
    for r in recent:
        vuln_count = db.query(Vulnerability).filter(Vulnerability.analysis_id == r.id).count()
        recent_list.append({
            "id": r.id,
            "file_name": r.file_name,
            "language": r.language,
            "security_score": r.security_score,
            "vulnerabilities_count": vuln_count,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    # Test summary
    test_summary = {
        "total_test_cases": len(PREDEFINED_TEST_CASES),
        "python_tests": len([t for t in PREDEFINED_TEST_CASES if t["language"] == "python"]),
        "c_tests": len([t for t in PREDEFINED_TEST_CASES if t["language"] == "c"]),
        "java_tests": len([t for t in PREDEFINED_TEST_CASES if t["language"] == "java"]),
    }

    return DashboardStats(
        total_analyzed_projects=max(total_projects, 1),
        total_source_files=total_files,
        total_vulnerabilities=total_vulns,
        average_security_score=avg_score,
        critical_vulns_count=critical_count,
        high_vulns_count=high_count,
        medium_vulns_count=medium_count,
        low_vulns_count=low_count,
        tests_summary=test_summary,
        language_distribution=lang_dist,
        severity_distribution=sev_dist,
        recent_analyses=recent_list
    )

