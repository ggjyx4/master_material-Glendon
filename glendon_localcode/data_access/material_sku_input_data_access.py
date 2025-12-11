from data_access.base import BaseRepository
from psycopg2.extras import RealDictCursor

class SkuDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('material_skus')
    
    def get_skus_by_master_id(self, document_id):
        # NOTE: Using 'master_material_document_id' as FK
        query = "SELECT * FROM material_skus WHERE master_material_document_id = %s"
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (document_id,))
                return cur.fetchall()
        finally:
            conn.close()

    def get_latest_sku_id(self):
        query = "SELECT id FROM material_skus ORDER BY id DESC LIMIT 1"
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            conn.close()

    def create_sku(self, sku_id, request_data: dict):
        query = """
            INSERT INTO material_skus (
                id, master_material_document_id, ref_id, qr_data, 
                sku_cost_override, color, size
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            sku_id,
            request_data.get('document_id'), # This is the master ID (MAT-001)
            request_data.get('ref_id'),
            request_data.get('qr_data'),
            request_data.get('sku_cost_override', 0.0),
            request_data.get('color'),
            request_data.get('size')
        )
        self.execute(query, params)
        return {"id": sku_id, **request_data}