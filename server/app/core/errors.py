"""Domain exceptions. Mapped to HTTP errors by app/main.py exception handlers."""


class DomainError(Exception):
    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.code)
        self.message = message or self.code


class NotFound(DomainError):
    status_code = 404
    code = "not_found"


class Conflict(DomainError):
    status_code = 409
    code = "conflict"


class Unauthorized(DomainError):
    status_code = 401
    code = "unauthorized"


class Forbidden(DomainError):
    status_code = 403
    code = "forbidden"


class AIError(DomainError):
    status_code = 502
    code = "ai_error"


class ValidationFailed(DomainError):
    status_code = 422
    code = "validation_failed"
