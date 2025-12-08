import anvil.server
from .api_framework import APIEndpoint
from typing import List, Dict, Any
from logics.material_sku_input_logics import SkuLogics
from data_access.material_sku_input_data_access import SkuDataAccess
from schemas.material_sku_input_schema import SkuResponse, CreateSkuRequest, SkuRequest

sku_logics = SkuLogics()

@anvil.server.route("/get_material_sku")
@APIEndpoint(
  name="get_material_sku",
  request_model=SkuRequest,
  response_model=List[SkuResponse],
  summary="Get SKUs for Material",
  tags=["SKU Inventory"]
)
def get_material_sku(request: SkuRequest):
    # Delegate work to the service
    return sku_logics.get_skus_for_material(request.document_id)


@anvil.server.route("/create_material_sku")
@APIEndpoint(
  name="create_material_sku",
  request_model=CreateSkuRequest,
  response_model=SkuResponse,
  summary="Create New SKU",
  tags=["SKU Inventory"]
)
def create_material_sku(request: CreateSkuRequest):
    # Delegate work to the service
    return sku_logics.create_new_sku(request)