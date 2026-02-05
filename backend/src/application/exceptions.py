class ConflictError(Exception):
    """Exception raised when a create operation conflicts with existing data.

    Attributes:
        conflicts -- list of conflicting model instances
    """

    def __init__(self, conflicts=None): 
        self.conflicts = conflicts or []
        super().__init__("Conflict detected")
