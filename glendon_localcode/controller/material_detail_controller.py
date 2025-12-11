from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from schemas.material_detail_schemas import ( 
    MaterialDetailResponse, 
    TechnicalDetailResponse, 
    CostDetailResponse,
    MaterialIDRequest,
    VersionHistoryItem
)
from data_access.material_detail_data_access import MaterialDetailDataAccess
from logics.material_detail_logics import MaterialDetailLogics

router = APIRouter(
    prefix="/material_details",
    tags=["Materials"]
)

def get_data_access():
    return MaterialDetailDataAccess()

def get_logics():
    return MaterialDetailLogics()

# ------------------------------------------------------------------

@router.post("/dashboard", response_model=MaterialDetailResponse)
def get_material_detail(
    request: MaterialIDRequest,
    data_access: MaterialDetailDataAccess = Depends(get_data_access),
    logics: MaterialDetailLogics = Depends(get_logics)
):
    version_row = data_access.get_current_version_row(request.document_id)
    if not version_row:
        raise HTTPException(status_code=404, detail="Material not found")
        
    return logics.build_material_detail(version_row)

# ------------------------------------------------------------------

@router.post("/technical", response_model=TechnicalDetailResponse)
def get_technical_detail(
    request: MaterialIDRequest,
    data_access: MaterialDetailDataAccess = Depends(get_data_access),
    logics: MaterialDetailLogics = Depends(get_logics)
):
    version_row = data_access.get_current_version_row(request.document_id)
    if not version_row:
        raise HTTPException(status_code=404, detail="Material not found")
        
    return logics.build_technical_detail(version_row)

# ------------------------------------------------------------------

@router.post("/cost", response_model=CostDetailResponse)
def get_cost_detail(
    request: MaterialIDRequest,
    data_access: MaterialDetailDataAccess = Depends(get_data_access),
    logics: MaterialDetailLogics = Depends(get_logics)
):
    version_row = data_access.get_current_version_row(request.document_id)
    if not version_row:
        raise HTTPException(status_code=404, detail="Material not found")
        
    return logics.build_cost_detail(version_row)

# ------------------------------------------------------------------

@router.post("/history", response_model=List[VersionHistoryItem])
def get_version_history(
    request: MaterialIDRequest,
    data_access: MaterialDetailDataAccess = Depends(get_data_access),
    logics: MaterialDetailLogics = Depends(get_logics)
):
    history_rows = data_access.get_version_history_rows(request.document_id)
    return logics.build_version_history(history_rows)

# ------------------------------------------------------------------

@router.post("/full_row", response_model=Dict[str, Any])
def get_material_full_row(
    request: MaterialIDRequest,
    data_access: MaterialDetailDataAccess = Depends(get_data_access),
    logics: MaterialDetailLogics = Depends(get_logics)
):
    try:
        version_row = data_access.get_current_version_row(request.document_id)
        if not version_row:
            return {}
        return logics.build_full_row(version_row)
    except Exception as e:
        return {}