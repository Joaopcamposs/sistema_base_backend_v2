from dataclasses import dataclass
from fastapi import HTTPException


class HTTPExceptionBase(HTTPException):
    detail: str
    status_code: int
    description: str | None = None

    def __init__(self) -> None:
        raise NotImplementedError(
            "Essa classe não pode ser instanciada diretamente. Ela é usada como base para outras"
        )


@dataclass
class FeedbackUsuario(HTTPExceptionBase):
    """
    Exceção que infor erro de uso do usuário.
    Ela não será enviada para o sentry.

    USE a classe ErroInterno para erros de código.
    """

    detail: str
    status_code: int
    description: str | None = None

    def __post_init__(self) -> None:
        if self.status_code < 400 or self.status_code >= 500:
            raise ValueError(
                "Erro interno deve ter status code 4xx. "
                "Use a classe ErroInterno para erros de uso do usuário."
            )

    def __str__(self) -> str:
        return self.detail


@dataclass
class ErroInterno(HTTPExceptionBase):
    """Exceção que infor erro no sistema. Ela é enviada para o sentry."""

    detail: str
    status_code: int
    description: str | None = None

    def __post_init__(self) -> None:
        if self.status_code < 500:
            raise ValueError(
                "Erro interno deve ter status code 5xx. Use a classe "
                "FeedbackUsuario para erros de uso do usuário."
            )

    def __str__(self) -> str:
        return self.detail
