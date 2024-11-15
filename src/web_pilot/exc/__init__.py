class BrowserPoolCapacityReachedError(Exception):
    def __init__(self, message: str):
        self.message = message


class NoAvailableBrowserError(Exception):
    def __init__(self, message: str):
        self.message = message


class UnableToPerformActionError(Exception):
    def __init__(self, message: str):
        self.message = message


class PoolAlreadyExistsError(Exception):
    def __init__(self, message: str):
        self.message = message


class PageSessionNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


class FailedToLaunchBrowser(Exception):
    def __init__(self, message: str):
        self.message = message


class PoolIsInactiveError(Exception):
    def __init__(self, message: str):
        self.message = message


class RateLimitsExceededError(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidSessionIDError(Exception):
    def __init__(self, message: str):
        self.message = message
