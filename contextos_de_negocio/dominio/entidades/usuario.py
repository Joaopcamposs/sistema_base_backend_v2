from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from libs.ddd.dominio.entidades import CamposBase, SegurancaDoUsuario
from libs.utils.tipos_basicos import Email, CPF


@dataclass(kw_only=True)
class Usuario(CamposBase, SegurancaDoUsuario):
    id: UUID | None
    empresa: UUID
    nome: str
    email: Email
    cpf: CPF
    ativo: bool
    adm: bool
    permissoes: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class UsuarioPublico(CamposBase, SegurancaDoUsuario):
    id: UUID
    empresa: UUID
    ativo: bool
    email_criptografado: bytes
    email_hash: str
