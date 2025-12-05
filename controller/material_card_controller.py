import anvil.server
from api_framework import APIEndpoint
from typing import List, Dict, Any

from logics import material_card_logics as logics
from data_access import material_card_data_access as data_access
from schemas import material_card_schema as schemas
# ------------------------------------------------------------------

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

  result_cards = logics.process_material_cards(all_masters, status)
  return result_cards
  

    