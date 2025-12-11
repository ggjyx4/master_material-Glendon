from data_access.base import BaseRepository
from psycopg2.extras import RealDictCursor

class MaterialDetailDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('master_materials')
    
    def get_current_version_row(self, document_id: str):
        """
        Fetches the FULL details of the 'Current' version.
        """
        # Join on m.document_id = v.document_id (Foreign Key)
        query = """
            SELECT 
                v.*, 
                m.created_at as master_created_at, 
                m.created_by as master_created_by,
                m.last_verified_date,
                m.last_verified_by
            FROM master_materials m
            JOIN material_versions v 
              ON m.document_id = v.document_id 
              AND m.current_version = v.ver_num
            WHERE m.document_id = %s
        """
        
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (document_id,))
                result = cur.fetchone()
                
                if not result:
                    # Fallback to latest if not set
                    fallback_query = """
                        SELECT * FROM material_versions 
                        WHERE document_id = %s 
                        ORDER BY ver_num DESC LIMIT 1
                    """
                    cur.execute(fallback_query, (document_id,))
                    return cur.fetchone()

                return result
        finally:
            conn.close()

    def get_version_history_rows(self, document_id: str):
        query = """
            SELECT * FROM material_versions
            WHERE document_id = %s
            ORDER BY ver_num ASC
        """
        
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (document_id,))
                return cur.fetchall()
        finally:
            conn.close()