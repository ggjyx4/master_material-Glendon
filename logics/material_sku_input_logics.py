import datetime
from typing import List
from schemas.material_sku_input_schema import CreateSkuRequest
from data_access.material_sku_input_data_access import SkuDataAccess
import anvil.server

class SkuService:
    
    def get_skus_for_material(self, document_id: str) -> List[dict]:
        # 1. Get Master
        master_row = SkuDataAccess.get_master_material(document_id)
        
        if not master_row:
            return []

        # 2. Get SKUs
        skus = SkuDataAccess.get_skus_by_master_row(master_row)

        # 3. Convert to Dicts (Domain logic)
        return [
            {
                "id": s['id'],
                "ref_id": s['ref_id'],
                "qr_data": s['qr_data'],
                "sku_cost_override": s['sku_cost_override'] or 0.0,
                "color": s['color'],
                "size": s['size']
            }
            for s in skus
        ]

    def create_new_sku(self, request: CreateSkuRequest) -> dict:
        """Orchestrates creating a new SKU"""
        # 1. Validate Master Material
        master_row = SkuDataAccess.get_master_material(request.document_id)
        if not master_row:
            raise Exception(f"Master material not found for document_id {request.document_id}")

        # 2. Generate Next ID (Business Logic)
        new_sku_id = self._generate_next_sku_id()

        # 3. Save to DB
        # Convert Pydantic model to dict for easier passing
        new_row = SkuDataAccess.create_sku(new_sku_id, master_row, request.dict())

        # 4. Return result
        return {
            "id": new_row['id'],
            "ref_id": new_row['ref_id'],
            "qr_data": new_row['qr_data'],
            "sku_cost_override": new_row['sku_cost_override'] or 0.0,
            "color": new_row['color'],
            "size": new_row['size']
        }

    def _generate_next_sku_id(self) -> str:
        """Internal helper to calculate the next ID"""
        last_row = SkuDataAccess.get_latest_sku()
        
        if last_row and last_row['id'].startswith("SKU"):
            try:
                last_num = int(last_row['id'][3:])
                return f"SKU{last_num + 1:03d}"
            except ValueError:
                # Fallback if ID parsing fails
                return f"SKU_ERR_{datetime.now().timestamp()}" 
        
        return "SKU001"