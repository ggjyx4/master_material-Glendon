from fastapi import APIRouter, Depends, HTTPException
from schemas.material_input_schemas import (
    CreateMaterialRequest, 
    MaterialResponse, 
    UpdateDraftRequest, 
    SubmitVersionRequest, 
    EditVerifiedRequest
)
from logics.material_input_logics import MaterialService

# 1. Create Router
router = APIRouter(
    prefix="/material_input",
    tags=["Material Input"]
)

def get_service():
    return MaterialService()

# ------------------------------------------------------------------

@router.post("/create_and_submit", response_model=MaterialResponse, summary="Create & Submit Immediately")
def create_and_submit_material(
    request: CreateMaterialRequest,
    service: MaterialService = Depends(get_service)
):
    """
    Creates a new material and immediately submits it (bypassing draft status).
    """
    try:
        return service.create_material(
            request_data=request.model_dump(exclude_none=True), 
            is_submit=True
        )
    except Exception as e:
        # Catch logic errors (e.g., database constraint violations)
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------

@router.post("/create_draft", response_model=MaterialResponse, summary="Create New Draft")
def create_material_draft(
    request: CreateMaterialRequest,
    service: MaterialService = Depends(get_service)
):
    try:
        return service.create_material(
            request_data=request.model_dump(exclude_none=True), 
            is_submit=False
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------

@router.post("/update_draft", response_model=MaterialResponse, summary="Update Existing Draft")
def update_draft(
    request: UpdateDraftRequest,
    service: MaterialService = Depends(get_service)
):
    try:
        return service.update_draft(
            document_id=request.document_id,
            updates=request.model_dump(exclude={'document_id'}, exclude_none=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------

@router.post("/submit_version", response_model=MaterialResponse, summary="Submit Draft to Unverified")
def submit_version(
    request: SubmitVersionRequest,
    service: MaterialService = Depends(get_service)
):
    try:
        return service.submit_version(
            document_id=request.document_id,
            final_updates=request.form_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------

@router.post("/edit_verified", response_model=MaterialResponse, summary="Revise Verified Document")
def edit_verified(
    request: EditVerifiedRequest,
    service: MaterialService = Depends(get_service)
):
    try:
        return service.create_revision_from_verified(
            document_id=request.document_id,
            updates=request.form_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))