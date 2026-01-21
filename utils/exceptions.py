"""
Custom Exceptions
Application-specific exception types
"""


class BreadPorositityException(Exception):
    """Base exception for bread porosity application"""
    pass


class ConfigurationError(BreadPorositityException):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(BreadPorositityException):
    """Raised when input validation fails"""
    pass


class AnalysisError(BreadPorositityException):
    """Raised when image analysis fails"""
    pass


class RecipeError(BreadPorositityException):
    """Raised when recipe operation fails"""
    pass


class DatabaseError(BreadPorositityException):
    """Raised when database operation fails"""
    pass


class ExportError(BreadPorositityException):
    """Raised when export operation fails"""
    pass


class QCError(BreadPorositityException):
    """Raised when quality control operation fails"""
    pass


class MLError(BreadPorositityException):
    """Raised when ML operation fails"""
    pass
