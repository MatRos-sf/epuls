class TrackerUserNotFoundError(Exception):
    """Raised when Tracker class cannot find User instance"""

    def __init__(self):
        super().__init__("Cannot find user instance!")
