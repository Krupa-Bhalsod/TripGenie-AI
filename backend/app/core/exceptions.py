class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500, user_message: str = "An error occurred", exception_string: str = "InternalError"):
        self.message = message
        self.status_code = status_code
        self.user_message = user_message
        self.exception_string = exception_string
        super().__init__(self.message)
