from __future__ import annotations

from pydantic import BaseModel, UUID4


class CadastrarUsuarioSchema(BaseModel):
    nome: str
    email: str
    cpf: str
    senha: str
    adm: bool
    ativo: bool
    permissoes: list[str] | None = None


class AtualizarUsuarioSchema(BaseModel):
    nome: str
    email: str
    cpf: str
    senha: str
    adm: bool
    ativo: bool
    permissoes: list[str] | None = None


class LerUsuarioSchema(BaseModel):
    id: UUID4
    nome: str
    email: str
    cpf: str
    adm: bool
    ativo: bool
    permissoes: list[str] | None = None
