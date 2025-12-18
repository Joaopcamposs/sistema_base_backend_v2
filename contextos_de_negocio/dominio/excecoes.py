from dataclasses import dataclass

from fastapi import status

from libs.utils.excecoes import FeedbackUsuario


@dataclass
class EmpresaNaoEncontrada(FeedbackUsuario):
    detail: str = "Empresa não encontrada"
    status_code: int = status.HTTP_404_NOT_FOUND


@dataclass
class EmpresaJaCadastrada(FeedbackUsuario):
    detail: str = "Email de Empresa já existente"
    status_code: int = status.HTTP_409_CONFLICT


@dataclass
class UsuarioNaoEncontrado(FeedbackUsuario):
    detail: str = "Usuario não encontrado"
    status_code: int = status.HTTP_404_NOT_FOUND


@dataclass
class UsuarioJaCadastrado(FeedbackUsuario):
    detail: str = "Email de Usuario já existente"
    status_code: int = status.HTTP_409_CONFLICT
