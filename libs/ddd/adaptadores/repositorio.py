from __future__ import annotations

from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class RepositorioAbstrato(ABC):
    def __init__(
        self,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            self.session = session


class RepositorioDominio(RepositorioAbstrato): ...


class RepositorioConsulta(RepositorioAbstrato): ...
