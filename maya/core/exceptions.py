"""Core exception classes for Maya system."""

class MayaBaseException(Exception):
    """Base exception class for all Maya system exceptions."""
    status_code = 500  # Default status code for internal errors
    
    def __init__(self, message="An unexpected error occurred", status_code=None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class ServiceError(MayaBaseException):
    """Raised when a service operation fails."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="Service operation failed", status_code=None):
        super().__init__(message, status_code)


class ConfigurationError(MayaBaseException):
    """Raised when there's a configuration error."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="Configuration error", status_code=None):
        super().__init__(message, status_code)


class AuthenticationError(MayaBaseException):
    """Raised when authentication fails."""
    status_code = 401  # Unauthorized
    
    def __init__(self, message="Authentication failed", status_code=None):
        super().__init__(message, status_code)


class AIModelError(MayaBaseException):
    """Raised when AI model operations fail."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="AI model operation failed", status_code=None):
        super().__init__(message, status_code)


class ContentProcessingError(MayaBaseException):
    """Raised when content processing fails."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="Content processing failed", status_code=None):
        super().__init__(message, status_code)


class SocialPlatformError(MayaBaseException):
    """Raised when social platform operations fail."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="Social platform operation failed", status_code=None):
        super().__init__(message, status_code)


class ValidationError(MayaBaseException):
    """Raised when input validation fails."""
    status_code = 400  # Bad Request
    
    def __init__(self, message="Validation failed", status_code=None):
        super().__init__(message, status_code)


class RateLimitError(MayaBaseException):
    """Raised when rate limits are exceeded."""
    status_code = 429  # Too Many Requests
    
    def __init__(self, message="Rate limit exceeded", status_code=None):
        super().__init__(message, status_code)


# Add new exception type for worker operations
class WorkerError(MayaBaseException):
    """Raised when worker operations fail."""
    status_code = 500  # Internal Server Error
    
    def __init__(self, message="Worker operation failed", status_code=None):
        super().__init__(message, status_code)


# For backwards compatibility
MayaException = MayaBaseException