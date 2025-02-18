class DownloadError(Exception):
    """Base exception for download-related errors"""
    def __init__(self, message: str, url: str = None):
        self.url = url
        super().__init__(message)

class MediaNotFoundError(DownloadError):
    """Raised when requested media is not found"""
    pass

class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int):
        self.retry_after = retry_after
        super().__init__(message)

class InvalidURLError(ValueError):
    """Raised when URL validation fails"""
    pass

class ProcessingError(Exception):
    """Raised when media processing fails"""
    pass