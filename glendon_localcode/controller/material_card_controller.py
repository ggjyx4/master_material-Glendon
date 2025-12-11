from fastapi import APIRouter, Depends, HTTPException
from typing import List

# Ensure these match your file structure
from logics.material_card_logics import process_material_cards
from data_access.material_card_data_access import MaterialCardDataAccess
from schemas.material_card_schemas import ListMaterialCardsRequest, MaterialCard

router = APIRouter(
    prefix="/material_cards",
    tags=["Materials", "UI"]
)

def get_data_access():
    return MaterialCardDataAccess()

@router.post("/list", response_model=List[MaterialCard])
def list_material_cards(
    request: ListMaterialCardsRequest, 
    data_access: MaterialCardDataAccess = Depends(get_data_access)
):
  try:
    # Default to active statuses if none provided
    status = request.statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]
    
    all_masters = data_access.fetch_all_master_materials(status)
    result_cards = process_material_cards(all_masters, status)
    
    return result_cards
  except Exception as e:
      # Use 500 for server/DB errors
      raise HTTPException(status_code=500, detail=str(e))