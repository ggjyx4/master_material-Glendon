from .base import BaseRepository


class SkuDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('material_sku')
    
    def get_master_material(self, doc_id: str):
        """Fetches a master material row by document_id"""
        return self.search(document_id=doc_id)

    def get_skus_by_master_row(self, master_row):
        """Fetches all SKUs linked to a specific master material row"""
        return self.search(master_material=master_row)

    def get_latest_sku(self):
        """Fetches the most recently created SKU (by ID) to help with ID generation"""
        # Note: Depending on volume, you might want a separate counter table later
        rows = self.search(tables.order_by("id", ascending=False))
        return rows[0] if len(rows) > 0 else None

    def create_sku(self, id, master_row, request_data: dict):
        """Inserts the new SKU row"""
        return self.add_row(
            id=id,
            master_material=master_row,
            ref_id=request_data.get('ref_id'),
            qr_data=request_data.get('qr_data'),
            sku_cost_override=request_data.get('sku_cost_override'),
            color=request_data.get('color'),
            size=request_data.get('size')
        )