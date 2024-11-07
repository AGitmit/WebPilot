class BrowserPoolCapacityReachedError(BaseException):
    def __init__(self, message: str):
        self.message = message


class NoAvailableBrowserError(BaseException):
    def __init__(self, message: str):
        self.message = message


class UnableToPerformActionError(BaseException):
    def __init__(self, message: str):
        self.message = message
