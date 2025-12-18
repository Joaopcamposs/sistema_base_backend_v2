import os
from contextvars import ContextVar
from datetime import timedelta, datetime
from typing import Annotated

from jose import JWTError, jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, HTTPException, Security, logger
from passlib.exc import InvalidTokenError
from pydantic import ValidationError
from starlette import status

from contextos_de_negocio.dominio.entidades.usuario import (
    Usuario,
    UsuarioPublico,
)
from contextos_de_negocio.pontos_de_entrada.schemas.seguranca import TokenData
from infra.banco_de_dados import get_session
from libs.utils.constantes import SECRET_KEY, ALGORITHM, oauth2_scheme

current_user: ContextVar[Usuario] = ContextVar("current_user")


async def authenticate_user(username: str, password: str) -> UsuarioPublico | None:
    """
    Etapas da funcao:
    - busca o email do usuario, em hash, na tabela de usuarios publicos
    - confere se a senha informada bate com a senha do usuario
    """
    from contextos_de_negocio import UsuarioRepoConsulta

    async with get_session(somente_leitura=True, schema="public") as session:
        repo = UsuarioRepoConsulta(session=session)
        usuario = await repo.consultar_usuario_publico_por_email(email=username)

    if not usuario:
        return None
    if not usuario.verificar_senha(password):
        return None
    return usuario


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as erro:
        logger.logger.error(f"Erro ao decodificar o token: {erro}")
        return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Usuario:
    """
    Decodifica o token JWT e busca o usuario (privado) no banco de dados, no schema da empresa.
    :param token:
    :return:
    """
    from contextos_de_negocio import UsuarioRepoConsulta

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email = payload.get("email")
        empresa = payload.get("empresa_id")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    async with get_session(somente_leitura=True, schema=empresa) as session:
        repo = UsuarioRepoConsulta(session=session)
        user = await repo.consultar_um_por_email(email=token_data.username)

    if user is None:
        raise credentials_exception

    current_user.set(user)

    return user


async def get_current_active_user(
    current_user_ctx: Annotated[Usuario, Security(get_current_user)],
) -> Usuario:
    if current_user_ctx.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user_ctx


def gerar_chave_aes() -> bytes:
    key = os.urandom(32)
    AESGCM(key)
    return key
