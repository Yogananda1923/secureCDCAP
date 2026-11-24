from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.samples.sample_registry import SAMPLE_PROGRAMS

router = APIRouter(prefix="/samples", tags=["Sample Programs"])

@router.get("", response_model=List[Dict[str, Any]])
def list_samples():
    return SAMPLE_PROGRAMS

@router.get("/{sample_id}")
def get_sample_by_id(sample_id: str):
    for s in SAMPLE_PROGRAMS:
        if s["id"] == sample_id:
            return s
    raise HTTPException(status_code=404, detail="Sample program not found.")

