from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code


class RegleMetierInvalide(AppException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class NonAuthentifie(AppException):
    def __init__(self, detail: str = "Non authentifié"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class NonAutorise(AppException):
    def __init__(self, detail: str = "Accès non autorisé"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class RessourceNonTrouvee(AppException):
    def __init__(self, detail: str = "Ressource non trouvée"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppException)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )