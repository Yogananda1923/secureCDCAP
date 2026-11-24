from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Transformation, VerificationResult
from app.schemas.compiler_schemas import (
    TransformationRequest,
    TransformationResponse,
    VerificationRequest,
    VerificationResponse
)
from app.optimizer.secure_transformations import SecureTransformer
from app.verification.regression_verifier import RegressionVerifier

router = APIRouter(prefix="", tags=["Transformation & Optimization"])

@router.post("/transform", response_model=TransformationResponse)
def transform_code(request: TransformationRequest, db: Session = Depends(get_db)):
    code = request.code
    lang = request.language.lower()

    if not code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    # 1. Apply transformation
    transformed, fixes, opts, diff_lines, explanation = SecureTransformer.transform(
        code=code,
        language=lang,
        vuln_ids=request.vulnerability_ids,
        enable_optimizations=request.enable_optimizations
    )

    # 2. Run verification pipeline
    verification = RegressionVerifier.run_verification(code, transformed, lang)

    # 3. Persist transformation if analysis_id is provided
    trans_id = None
    if request.analysis_id:
        db_trans = Transformation(
            analysis_id=request.analysis_id,
            transformation_type="SecureTransformation & Optimization",
            description=explanation.what_changed,
            original_code=code,
            transformed_code=transformed,
            diff_data=[d.model_dump() for d in diff_lines],
            is_verified=verification.overall_status == "Passed",
            verification_status=verification.overall_status,
            explanation=explanation.model_dump()
        )
        db.add(db_trans)
        db.commit()
        db.refresh(db_trans)
        trans_id = db_trans.id

        db_verif = VerificationResult(
            transformation_id=db_trans.id,
            syntax_valid=verification.syntax_valid,
            semantic_valid=verification.semantic_valid,
            regression_passed=verification.regression_passed,
            overall_status=verification.overall_status,
            details=verification.details
        )
        db.add(db_verif)
        db.commit()

    return TransformationResponse(
        transformation_id=trans_id,
        original_code=code,
        transformed_code=transformed,
        diff_lines=diff_lines,
        transformations_applied=fixes,
        optimizations_applied=opts,
        is_verified=verification.overall_status == "Passed",
        verification_status=verification.overall_status,
        explanation=explanation,
        verification_details=verification.details
    )

@router.post("/verify", response_model=VerificationResponse)
def verify_transformation(request: VerificationRequest):
    return RegressionVerifier.run_verification(
        request.original_code,
        request.transformed_code,
        request.language
    )

@router.post("/optimize", response_model=TransformationResponse)
def optimize_code(request: TransformationRequest, db: Session = Depends(get_db)):
    # Focus only on optimizations
    transformed, fixes, opts, diff_lines, explanation = SecureTransformer.transform(
        code=request.code,
        language=request.language,
        vuln_ids=[],
        enable_optimizations=True
    )
    verification = RegressionVerifier.run_verification(request.code, transformed, request.language)

    return TransformationResponse(
        transformation_id=None,
        original_code=request.code,
        transformed_code=transformed,
        diff_lines=diff_lines,
        transformations_applied=fixes,
        optimizations_applied=opts,
        is_verified=verification.overall_status == "Passed",
        verification_status=verification.overall_status,
        explanation=explanation,
        verification_details=verification.details
    )

