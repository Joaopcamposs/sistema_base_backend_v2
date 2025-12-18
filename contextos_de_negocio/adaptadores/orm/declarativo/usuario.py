from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, String, Boolean, ARRAY, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.ddd.adaptadores.orm import Base, CamposBaseDB

if TYPE_CHECKING:
    from contextos_de_negocio.adaptadores.orm.declarativo.empresa import EmpresaDB


class UsuarioDB(Base, CamposBaseDB):
    __tablename__ = "usuario"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    empresa_id: Mapped[UUID] = mapped_column(ForeignKey("empresa.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    adm: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permissoes: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )

    # relacoes
    empresa: Mapped["EmpresaDB"] = relationship(
        "EmpresaDB",
        back_populates="usuarios",
        foreign_keys=[empresa_id],
    )

    def __repr__(self) -> str:
        return (
            f"UsuarioDB(email={self.email}, id={self.id}, empresa_id={self.empresa_id})"
        )

    def __hash__(self) -> int:
        return hash(self.id)


class UsuarioPublicoDB(Base, CamposBaseDB):
    __tablename__ = "usuario_publico"
    __table_args__ = (
        Index("idx_usuario_email_hash_empresa", "email_hash", "empresa_id"),
        {"schema": "public"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    empresa_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_criptografado: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    senha_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    def __repr__(self) -> str:
        return f"UsuarioPublicoDB(id={self.id}, empresa_id={self.empresa_id})"

    def __hash__(self) -> int:
        return hash(self.id)
