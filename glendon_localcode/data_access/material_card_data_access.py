from data_access.base import BaseRepository
from psycopg2.extras import RealDictCursor

class MaterialCardDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('master_materials')
    
    def fetch_all_master_materials(self, status_list: list):
        if not status_list:
            return []

        query = """
            SELECT 
                m.document_id,
                v.material_name,
                v.material_type,
                v.status,
                v.ver_num,
                v.original_cost_per_unit,
                v.native_cost_currency,
                
                -- Extra fields for Card UI
                v.weight_per_unit,
                v.weight_uom,
                v.fabric_composition,
                v.supplier_name,
                v.master_material_id, -- The human readable one
                v.ref_id,
                v.picture_id,

                m.created_at
            FROM master_materials m
            JOIN material_versions v 
              ON m.document_id = v.document_id 
              AND m.current_version = v.ver_num
            WHERE v.status = ANY(%s)
            ORDER BY m.created_at DESC
        """
        
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (status_list,))
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Error fetching list: {e}")
            return [] 
        finally:
            conn.close()