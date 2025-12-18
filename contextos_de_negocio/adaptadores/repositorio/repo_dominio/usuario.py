from abc import abstractmethod
from uuid import UUID

from sqlalchemy import select, insert, update, delete

from contextos_de_negocio.adaptadores.orm.declarativo.usuario import (
    UsuarioDB,
    UsuarioPublicoDB,
)
from contextos_de_negocio.adaptadores.repositorio.repo_mixins.usuario import (
    UsuarioPublicoMixin,
)
from contextos_de_negocio.dominio.agregados.usuario import Usuario, UsuarioPublico
from contextos_de_negocio.dominio.excecoes import (
    UsuarioJaCadastrado,
    UsuarioNaoEncontrado,
)
from libs.ddd.adaptadores.repositorio import RepositorioDominio
from libs.ddd.visualizadores.filtro import Filtros
from libs.utils.constantes import NAO_DELETADO
from libs.utils.tipos_basicos import Email, TipoDeOperacao, CPF


class UsuarioRepoDominioAbstrato(RepositorioDominio):
    def __init__(self, *args, **kwargs):
        super(UsuarioRepoDominioAbstrato, self).__init__(*args, **kwargs)
        self.seen: set[Usuario] = set()

    async def adicionar(self, usuario: Usuario) -> None:
        self.seen.add(usuario)
        await self._adicionar(usuario)

    @abstractmethod
    async def _adicionar(self, usuario: Usuario) -> None:
        raise NotImplementedError

    async def remover(self, usuario: Usuario) -> None:
        await self._remover(usuario)

    @abstractmethod
    async def _remover(self, usuario: Usuario) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consultar_um_por_filtros(self, filtros: Filtros) -> Usuario:
        raise NotImplementedError()


class UsuarioRepoDominio(UsuarioRepoDominioAbstrato, UsuarioPublicoMixin):
    async def gerar_agregado_para_cadastro(
        self,
        empresa: UUID,
        nome: str,
        email: str,
        cpf: str,
        senha: str,
        ativo: bool,
        adm: bool,
        permissoes: list[str],
    ) -> Usuario:
        async with self.session as session:
            usuario_com_mesmo_email = (
                await session.execute(
                    select(UsuarioDB).where(
                        UsuarioDB.email == Email(email), UsuarioDB.deletado_em.is_(None)
                    )
                )
            ).scalar_one_or_none()
            if usuario_com_mesmo_email:
                raise UsuarioJaCadastrado

        return Usuario.retornar_agregado_para_cadastro(
            empresa=empresa,
            nome=nome,
            email=Email(email),
            cpf=CPF(cpf),
            senha=senha,
            ativo=ativo,
            adm=adm,
            permissoes=permissoes,
        )

    async def consultar_um_por_filtros(self, filtros: Filtros) -> Usuario:
        async with self.session as session:
            usuario = (
                await session.execute(
                    select(UsuarioDB).filter_by(**filtros, **NAO_DELETADO)
                )
            ).scalar_one_or_none()
            if not usuario:
                raise UsuarioNaoEncontrado

            agregado = Usuario(
                id=usuario.id,
                empresa=usuario.empresa_id,
                nome=usuario.nome,
                email=Email(usuario.email),
                cpf=CPF(usuario.cpf),
                adm=usuario.adm,
                ativo=usuario.ativo,
                _senha=usuario.senha_hash,
                permissoes=usuario.permissoes,
                criado_por=usuario.criado_por,
                criado_em=usuario.criado_em,
                ultima_modificacao_em=usuario.ultima_modificacao_em,
                modificado_por=usuario.modificado_por,
                deletado_em=usuario.deletado_em,
                deletado_por=usuario.deletado_por,
            )

        return agregado

    async def consultar_usuario_publico_por_id(self, id: UUID) -> UsuarioPublico:
        async with self.session as session:
            usuario = (
                await session.execute(
                    select(UsuarioPublicoDB).where(
                        UsuarioPublicoDB.id == id,
                        UsuarioPublicoDB.deletado_em.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not usuario:
                raise UsuarioNaoEncontrado

            usuario_entidade = UsuarioPublico(
                id=usuario.id,
                empresa=usuario.empresa_id,
                ativo=usuario.ativo,
                email_criptografado=usuario.email_criptografado,
                email_hash=usuario.email_hash,
                _senha=usuario.senha_hash,
                criado_por=usuario.criado_por,
                criado_em=usuario.criado_em,
                ultima_modificacao_em=usuario.ultima_modificacao_em,
                modificado_por=usuario.modificado_por,
                deletado_em=usuario.deletado_em,
                deletado_por=usuario.deletado_por,
            )
            return usuario_entidade

    async def _adicionar(
        self,
        usuario: Usuario,
    ) -> None:
        dados = {
            "id": usuario.id,
            "empresa_id": usuario.empresa,
            "nome": usuario.nome,
            "email": usuario.email,
            "cpf": usuario.cpf,
            "senha_hash": usuario._senha,
            "adm": usuario.adm,
            "ativo": usuario.ativo,
            "permissoes": usuario.permissoes,
            "criado_por": usuario.criado_por,
            "criado_em": usuario.criado_em,
            "modificado_por": usuario.modificado_por,
            "ultima_modificacao_em": usuario.ultima_modificacao_em,
            "deletado_por": usuario.deletado_por,
            "deletado_em": usuario.deletado_em,
        }

        match usuario._tipo_de_operacao:
            case TipoDeOperacao.INSERCAO:
                operacao = insert(UsuarioDB).values(dados)
            case TipoDeOperacao.ATUALIZACAO:
                operacao = (
                    update(UsuarioDB).where(UsuarioDB.id == usuario.id).values(dados)
                )
            case _:
                raise ValueError(
                    "Tipo de operação não suportado para o repositório de domínio."
                )

        await self.session.execute(operacao)

    async def _remover(self, usuario: Usuario) -> None:
        if usuario._usa_soft_delete:
            dados = {
                "modificado_por": usuario.modificado_por,
                "ultima_modificacao_em": usuario.ultima_modificacao_em,
                "deletado_por": usuario.deletado_por,
                "deletado_em": usuario.deletado_em,
            }

            operacao = update(UsuarioDB).where(UsuarioDB.id == usuario.id).values(dados)
        else:
            operacao = delete(UsuarioDB).where(UsuarioDB.id == usuario.id)

        await self.session.execute(operacao)
