from datetime import datetime

class SystemFields:
    def __init__(self):
        self.change_date: datetime = None
        self.change_user: str = None
        self.creation_date: datetime = None
        self.creation_user: str = None
        self.use_date: datetime = None
        self.use_user: str = None
        self.use_count: int = 0

