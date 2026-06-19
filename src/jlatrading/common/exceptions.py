class AppError(Exception):
    """Base application error."""


class DbError(AppError):
    """Repository layer error."""


class RepositoryError(AppError):
    """Repository layer error."""


class ServiceError(AppError):
    """Service layer error."""
