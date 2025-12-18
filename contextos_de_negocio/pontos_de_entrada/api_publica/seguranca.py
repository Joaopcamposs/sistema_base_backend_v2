from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from contextos_de_negocio.pontos_de_entrada.schemas.seguranca import Token
from contextos_de_negocio.pontos_de_entrada.schemas.usuario import LerUsuarioSchema
from contextos_de_negocio.servicos.executores.seguranca import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from libs.utils.constantes import ACCESS_TOKEN_EXPIRE_MINUTES

router_seguranca = APIRouter(prefix="/api", tags=["Login"])


@router_seguranca.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "email": form_data.username,
            "empresa_id": str(user.empresa),
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router_seguranca.get("/users/me/", response_model=LerUsuarioSchema)
async def read_users_me(
    current_user: Annotated[Usuario, Depends(get_current_active_user)],
) -> Usuario:
    return current_user
