from dataclasses import dataclass, field
from uuid import UUID

from pydantic import UUID4

from libs.ddd.barramento import Evento
from libs.utils.constantes import (
    CPF_PRIMEIRO_USUARIO,
    SENHA_PRIMEIRO_USUARIO,
)


@dataclass
class UsuarioCriado(Evento):
    id: UUID


@dataclass
class UsuarioAtualizado(Evento):
    id: UUID


@dataclass
class UsuarioRemovido(Evento):
    id: UUID


@dataclass
class ChegouAHoraDeCriarUsuarioInicialDaEmpresa(Evento):
    empresa: UUID4
    nome: str
    email: str
    cpf: str
    senha: str
    ativo: bool
    adm: bool
    permissoes: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class ChegouAHoraDeCriarUsuarioADMDaEmpresa(Evento):
    empresa: UUID4
    email: str
    nome: str = "Usuario ADM JP Da Empresa"
    cpf: str = CPF_PRIMEIRO_USUARIO
    senha: str = SENHA_PRIMEIRO_USUARIO
    ativo: bool = True
    adm: bool = True
    permissoes: list[str] = field(default_factory=list)
