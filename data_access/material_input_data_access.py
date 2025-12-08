from .base import BaseRepository

class MaterialInputDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('material_input')
    
    def get_master_by_id(self, doc_id: str):
        return self.search(document_id=doc_id)

    def get_all_masters(self):
        # Used for ID generation logic
        return self.search()

    def create_master_record(self, doc_id, doc_uid, user_email, now):
        """Creates the shell master record"""
        return self.add_row(
            document_id=doc_id,
            current_version_uid=doc_uid,
            created_at=now,
            created_by=user_email
            # Note: current_version_number is removed here as requested
        )

    def create_version_record(self, master_row, doc_id, doc_uid, ver_num, status, user, now, data: dict):
        """Creates the version row and links it to master"""
        
        # 1. Create the version row
        # Filter data to ensure we don't pass unknown columns if schema changed
        # (Optional: strictly you might just pass **data)
        new_version = self.add_row(
            document_id=doc_id,
            document_uid=doc_uid,
            ver_num=ver_num,
            status=status,
            created_at=now,
            created_by=user,
            **data
        )

        # 2. Update Master links
        current_history = list(master_row['version_history'] or [])
        current_history.append(new_version)
        
        master_row['version_history'] = current_history
        master_row['current_version'] = new_version
        master_row['current_version_uid'] = doc_uid
        
        # If status is submitted, update master timestamps
        if "Submitted" in status:
            new_version['submitted_at'] = now
            new_version['submitted_by'] = user
            master_row['submitted_at'] = now
            master_row['submitted_by'] = user

        return new_version