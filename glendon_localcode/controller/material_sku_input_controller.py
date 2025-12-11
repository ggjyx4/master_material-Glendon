from fastapi import APIRouter, Depends, HTTPException
from typing import List

# Import Schemas
from schemas.material_sku_input_schemas import SkuResponse, CreateSkuRequest, SkuRequest
from logics.material_sku_input_logics import SkuLogics

router = APIRouter(
    prefix="/material_sku",
    tags=["SKU Inventory"]
)

def get_sku_logics():
    return SkuLogics()

# ------------------------------------------------------------------

@router.post("/get", response_model=List[SkuResponse], summary="Get SKUs for Material")
def get_material_sku(
    request: SkuRequest,
    logics: SkuLogics = Depends(get_sku_logics)
):
    """
    Get all SKUs associated with a specific material document ID.
    """
    try:
        raw_skus = logics.get_skus_for_material(request.document_id)
        
        # FIX: Map DB column 'master_material_document_id' to Schema field 'master_material_id'
        mapped_skus = []
        for sku in raw_skus:
            # Create a copy to avoid mutating the original if cached
            sku_dict = dict(sku)
            if 'master_material_document_id' in sku_dict:
                sku_dict['master_material_id'] = sku_dict.pop('master_material_document_id')
            mapped_skus.append(sku_dict)
            
        return mapped_skus
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=SkuResponse, summary="Create New SKU")
def create_material_sku(
    request: CreateSkuRequest,
    logics: SkuLogics = Depends(get_sku_logics)
):
    try:
        # Delegate work to the service
        new_sku = logics.create_new_sku(request)
        
        # Fix mapping for the response here as well
        if 'master_material_document_id' in new_sku:
             new_sku['master_material_id'] = new_sku.pop('master_material_document_id')
             
        return new_sku
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))