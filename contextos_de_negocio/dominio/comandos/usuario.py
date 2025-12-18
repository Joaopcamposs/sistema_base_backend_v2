from dataclasses import dataclass, field
from uuid import UUID

from pydantic import UUID4

from libs.ddd.barramento import Comando


@dataclass
class CadastrarUsuario(Comando):
    nome: str
    email: str
    cpf: str
    senha: str
    ativo: bool
    adm: bool
    empresa: UUID4
    permissoes: list[str] = field(default_factory=list)


@dataclass
class AtualizarUsuario(Comando):
    nome: str
    email: str
    cpf: str
    senha: str
    ativo: bool
    adm: bool
    permissoes: list[str] = field(default_factory=list)
    # campos de busca
    id: UUID | None = None
    email_antigo: str | None = None


@dataclass
class RemoverUsuario(Comando):
    id: UUID | None = None
    email: str | None = None
