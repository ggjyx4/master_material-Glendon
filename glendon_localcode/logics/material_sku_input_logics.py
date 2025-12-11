from typing import List
from data_access.material_sku_input_data_access import SkuDataAccess

class SkuLogics: 
    def __init__(self):
        # 1. Instantiate Data Access
        self.data_access = SkuDataAccess()

    def get_skus_for_material(self, document_id: str) -> List[dict]:
        # 2. Call instance method (self.data_access)
        skus = self.data_access.get_skus_by_master_id(document_id)
        return skus

    def create_new_sku(self, request) -> dict:
        # 1. Generate ID
        new_sku_id = self._generate_next_sku_id()

        # 2. Convert Request to Dict
        # (request is a Pydantic model)
        data_dict = request.model_dump()

        # 3. Save
        new_row = self.data_access.create_sku(new_sku_id, data_dict)
        return new_row

    def _generate_next_sku_id(self) -> str:
        last_id = self.data_access.get_latest_sku_id()
        
        if last_id and last_id.startswith("SKU"):
            try:
                last_num = int(last_id[3:])
                return f"SKU{last_num + 1:03d}"
            except ValueError:
                return "SKU001"
        return "SKU001"