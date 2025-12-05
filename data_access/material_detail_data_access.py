from .base import BaseRepository

class MaterialDetailRepository(BaseRepository):
    def __init__(self):
        # We initialize with 'master_material' as the primary table
        super().__init__('master_material')
    
    def get_master_material_by_id(self, document_id):
        if not document_id:
            raise ValueError("document_id is required")
        return self.get(document_id=document_id)

    def get_current_version_row(self, document_id):
        master = self.get_master_material_by_id(document_id)
        if not master:
            raise Exception(f"No material found for ID: {document_id}")
            
        version = master['current_version']
        if not version:
            raise Exception(f"No current version found for ID: {document_id}")
        return version

    def get_version_history_rows(self, document_id):
        master = self.get_master_material_by_id(document_id)
        if not master:
            return []
        return list(master['version_history'] or [])
    