import anvil.server
from .api_framework import APIEndpoint
from typing import List, Dict, Any

from logics.material_card_logics import _format_single_card, process_material_cards
from data_access.material_card_data_access import MaterialCardDataAccess
from schemas.material_card_schema import ListMaterialCardsRequest, MaterialCard
# ------------------------------------------------------------------

data_access = MaterialCardDataAccess()

@anvil.server.route("/list_material_cards")
@APIEndpoint(
  name="list_material_cards",
  request_model=ListMaterialCardsRequest,
  response_model=List[MaterialCard],  # Returns a LIST of cards
  summary="List Material Cards",
  description="Get a list of material cards formatted for UI display, filtered by status.",
  tags=["Materials", "UI"]
)

def list_material_cards (request: ListMaterialCardsRequest):
  status = request.statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]
  all_masters = data_access.fetch_all_master_materials(status)

  result_cards = process_material_cards(all_masters, status)
  return result_cards
  

    