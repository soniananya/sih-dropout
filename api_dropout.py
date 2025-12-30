from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

from dropout_model import analyze_student_dropout_risk, analyze_batch_students

router = APIRouter()


# -----------------------------
# Request Schemas
# -----------------------------
class SingleStudentRequest(BaseModel):
    form_response: Dict


class BatchStudentRequest(BaseModel):
    form_responses: List[Dict]


# -----------------------------
# API ENDPOINTS
# -----------------------------

@router.post("/analyze")
def analyze_single_student(request: SingleStudentRequest):
    """
    Analyze dropout risk for one student.
    """
    try:
        result = analyze_student_dropout_risk(request.form_response)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-batch")
def analyze_multiple_students(request: BatchStudentRequest):
    """
    Analyze dropout risk for multiple students.
    """
    try:
        results = analyze_batch_students(request.form_responses)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
