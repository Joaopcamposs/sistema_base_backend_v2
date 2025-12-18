from sqlalchemy import select

from contextos_de_negocio.adaptadores.orm.declarativo.usuario import (
    UsuarioDB,
    UsuarioPublicoDB,
)
from contextos_de_negocio.dominio.entidades.usuario import UsuarioPublico, Usuario
from libs.ddd.adaptadores.repositorio import RepositorioConsulta
from libs.ddd.visualizadores.filtro import Filtros

from libs.utils.constantes import NAO_DELETADO
from libs.utils.tipos_basicos import Email, CPF


class UsuarioRepoConsulta(RepositorioConsulta):
    async def consultar_usuario_publico_por_email(
        self, email: str
    ) -> UsuarioPublico | None:
        email_hash = UsuarioPublico.hash_email(email)
        async with self.session as session:
            usuario = (
                await session.execute(
                    select(UsuarioPublicoDB).where(
                        UsuarioPublicoDB.email_hash == email_hash,
                        UsuarioPublicoDB.deletado_em.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not usuario:
                return None

            usuario_entidade = UsuarioPublico(
                id=usuario.id,
                empresa=usuario.empresa_id,
                ativo=usuario.ativo,
                email_criptografado=usuario.email_criptografado,
                email_hash=usuario.email_hash,
                _senha=usuario.senha_hash,
            )
            return usuario_entidade

    async def consultar_um_por_email(self, email: str) -> Usuario | None:
        async with self.session as session:
            usuario = (
                await session.execute(
                    select(UsuarioDB).where(
                        UsuarioDB.email == email, UsuarioDB.deletado_em.is_(None)
                    )
                )
            ).scalar_one_or_none()
            if not usuario:
                return None

            usuario_entidade = Usuario(
                id=usuario.id,
                empresa=usuario.empresa_id,
                nome=usuario.nome,
                email=Email(usuario.email),
                cpf=CPF(usuario.cpf),
                adm=usuario.adm,
                ativo=usuario.ativo,
                _senha=usuario.senha_hash,
            )

        return usuario_entidade

    async def consultar_um_por_filtros(self, filtros: Filtros) -> Usuario | None:
        async with self.session as session:
            usuario = (
                await session.execute(
                    select(UsuarioDB).filter_by(**filtros, **NAO_DELETADO)
                )
            ).scalar_one_or_none()
            if not usuario:
                return None

            usuario_entidade = Usuario(
                id=usuario.id,
                empresa=usuario.empresa_id,
                nome=usuario.nome,
                email=Email(usuario.email),
                cpf=CPF(usuario.cpf),
                adm=usuario.adm,
                ativo=usuario.ativo,
                _senha=usuario.senha_hash,
            )

        return usuario_entidade

    async def consultar_por_filtros(self, filtros: Filtros) -> list[Usuario]:
        async with self.session as session:
            usuarios = (
                (
                    await session.execute(
                        select(UsuarioDB).filter_by(**filtros, **NAO_DELETADO)
                    )
                )
                .scalars()
                .all()
            )

            usuarios_entidade = [
                Usuario(
                    id=usuario.id,
                    empresa=usuario.empresa_id,
                    nome=usuario.nome,
                    email=Email(usuario.email),
                    cpf=CPF(usuario.cpf),
                    adm=usuario.adm,
                    ativo=usuario.ativo,
                    _senha=usuario.senha_hash,
                )
                for usuario in usuarios
            ]

        return usuarios_entidade
