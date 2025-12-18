from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from contextos_de_negocio.dominio.eventos.empresa import (
    EmpresaCriada,
    EmpresaAtualizada,
    EmpresaRemovida,
)

from contextos_de_negocio.dominio.eventos.usuario import (
    ChegouAHoraDeCriarUsuarioInicialDaEmpresa,
    ChegouAHoraDeCriarUsuarioADMDaEmpresa,
)
from libs.utils.constantes import PREFIXO_USUARIO_ADM
from libs.utils.tipos_basicos import Email, TipoDeOperacao, CPF, CNPJ
from libs.ddd.dominio.agregado import Agregado


@dataclass(kw_only=True)
class Empresa(Agregado):
    id: UUID
    razao_social: str
    nome_responsavel: str
    email: Email
    ativo: bool
    cpf: CPF
    nome_fantasia: str | None = None
    cnpj: CNPJ | None = None

    _eh_primeira_empresa: bool = False

    def __post_init__(self) -> None:
        self._usa_soft_delete = True

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def retornar_agregado_para_cadastro(
        cls,
        razao_social: str,
        nome_fantasia: str | None,
        nome_responsavel: str,
        email: Email,
        cpf: CPF,
        cnpj: CNPJ | None,
        ativo: bool,
        id: UUID | None = None,
        _eh_primeira_empresa: bool = False,
    ) -> "Empresa":
        email = Email(email)
        cpf = CPF(cpf)
        cnpj = CNPJ(cnpj)
        return Empresa(
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            nome_responsavel=nome_responsavel,
            email=email,
            cpf=cpf,
            cnpj=cnpj,
            ativo=ativo,
            id=id or uuid4(),
            _eh_primeira_empresa=_eh_primeira_empresa,
        )

    def cadastrar(self, id_usuario: UUID, senha: str) -> None:
        self._tipo_de_operacao = TipoDeOperacao.INSERCAO
        self.criado_por = id_usuario
        self.criado_em = datetime.now()

        self.add_event(EmpresaCriada(id=self.id))
        self.add_event(
            ChegouAHoraDeCriarUsuarioInicialDaEmpresa(
                nome=self.nome_responsavel,
                email=self.email,
                cpf=self.cpf,
                senha=senha,
                ativo=True,
                adm=True,
                empresa=self.id,
            )
        )
        if self._eh_primeira_empresa is False:
            email_usuario_adm_da_empresa = Email(
                f"{PREFIXO_USUARIO_ADM}@{str(self.id)}.com"
            )
            self.add_event(
                ChegouAHoraDeCriarUsuarioADMDaEmpresa(
                    empresa=self.id, email=email_usuario_adm_da_empresa
                )
            )

    def atualizar(
        self,
        razao_social: str,
        nome_fantasia: str | None,
        nome_responsavel: str,
        email: Email,
        cpf: CPF,
        cnpj: CNPJ | None,
        ativo: bool,
        id_usuario: UUID,
    ) -> None:
        self._tipo_de_operacao = TipoDeOperacao.ATUALIZACAO

        self.razao_social = razao_social
        self.nome_fantasia = nome_fantasia
        self.nome_responsavel = nome_responsavel
        self.email = Email(email)
        self.cpf = CPF(cpf)
        self.cnpj = CNPJ(cnpj)
        self.ativo = ativo

        self.modificado_por = id_usuario
        self.ultima_modificacao_em = datetime.now()

        self.add_event(EmpresaAtualizada(id=self.id))

    def remover(self, id_usuario: UUID) -> None:
        self._tipo_de_operacao = TipoDeOperacao.REMOCAO

        self.modificado_por = id_usuario
        self.ultima_modificacao_em = datetime.now()

        self.deletado_por = id_usuario
        self.deletado_em = datetime.now()

        self.add_event(EmpresaRemovida(id=self.id))
