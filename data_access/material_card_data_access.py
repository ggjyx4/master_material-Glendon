from base_repository import BaseRepository

class MaterialCard(BaseRepository):
    def __init__(self):
        super().__init__('material_card')
    
    def fetch_material_card_by_id(document_id):
        return self.search(document_id=document_id)
    