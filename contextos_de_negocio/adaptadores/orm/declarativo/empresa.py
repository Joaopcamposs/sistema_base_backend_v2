from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.ddd.adaptadores.orm import Base, CamposBaseDB

if TYPE_CHECKING:
    from contextos_de_negocio.adaptadores.orm.declarativo.usuario import UsuarioDB


class EmpresaDB(Base, CamposBaseDB):
    __tablename__ = "empresa"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(
        String(255), nullable=False, default=""
    )
    nome_responsavel: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=False)
    cnpj: Mapped[str | None] = mapped_column(
        String(14), nullable=False, unique=False, default=""
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # relacoes
    usuarios: Mapped[list["UsuarioDB"]] = relationship(
        "UsuarioDB",
        back_populates="empresa",
        foreign_keys="[UsuarioDB.empresa_id]",
        primaryjoin="EmpresaDB.id==UsuarioDB.empresa_id",
    )

    def __repr__(self) -> str:
        return f"EmpresaDB(id={self.id}, razao_social={self.razao_social}, email={self.email})"

    def __hash__(self) -> int:
        return hash(self.id)
