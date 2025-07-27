"""Core exception classes for Maya system."""

class MayaException(Exception):
    """Base exception class for Maya system."""
    pass


class ConfigurationError(MayaException):
    """Raised when there's a configuration error."""
    pass


class AuthenticationError(MayaException):
    """Raised when authentication fails."""
    pass


class AIModelError(MayaException):
    """Raised when AI model operations fail."""
    pass


class ContentProcessingError(MayaException):
    """Raised when content processing fails."""
    pass


class SocialPlatformError(MayaException):
    """Raised when social platform operations fail."""
    pass


class ValidationError(MayaException):
    """Raised when input validation fails."""
    pass


class RateLimitError(MayaException):
    """Raised when rate limits are exceeded."""
    pass