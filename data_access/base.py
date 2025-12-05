from anvil.tables import app_tables

class BaseRepository:
    def __init__(self, table_name):
        self.table = getattr(app_tables, table_name)

    def get_by_id(self, row_id):
        return self.table.get_by_id(row_id)

    def search(self, **kwargs):
        return self.table.search(**kwargs)

    def add_row(self, **kwargs):
        return self.table.add_row(**kwargs)
    
    def get(self, **kwargs):
        return self.table.get(**kwargs)
