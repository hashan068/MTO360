"""
Sales Domain Exceptions

Custom exceptions for sales flow business logic.
"""


class SalesFlowException(Exception):
    """Base exception for sales flow errors"""
    pass


class InvalidStatusTransitionError(SalesFlowException):
    """Raised when attempting invalid status transition"""
    pass


class DocumentLockedException(SalesFlowException):
    """Raised when attempting to edit locked document"""
    pass


class DuplicateConversionError(SalesFlowException):
    """Raised when attempting duplicate conversion"""
    pass


class ValidationError(SalesFlowException):
    """Raised when business rule validation fails"""
    pass


class DocumentNotFoundError(SalesFlowException):
    """Raised when document is not found"""
    pass
