from __future__ import annotations

from enum import Enum
from validate_docbr import CPF as ValidadorDeCPF


class TipoDeOperacao(Enum):
    INSERCAO = "insercao"
    ATUALIZACAO = "atualizacao"
    REMOCAO = "remocao"


class CPF(str):
    def __init__(self, cpf: str = ""):
        self.cpf = self.somente_digitos(cpf)
        self.validar()

    def validar(self) -> None:
        if not ValidadorDeCPF().validate(self.cpf):
            raise ValueError("CPF inválido")

    @staticmethod
    def somente_digitos(cpf: str) -> str:
        return "".join([char for char in cpf if char.isdigit()])

    @staticmethod
    def gerar() -> str:
        cpf_gerado = ValidadorDeCPF().generate()
        return str(cpf_gerado)

    def __str__(self) -> str:
        return self.cpf


class CNPJ(str):
    # apenas para formatar cnpj com digitos
    def __new__(cls, value: str | None) -> CNPJ | None:  # type: ignore[misc]
        if not value:
            return None
        if isinstance(value, str):
            value = cls.somente_digitos(value)
        return super().__new__(cls, value)

    @staticmethod
    def somente_digitos(cnpj: str) -> str:
        return "".join([char for char in cnpj if char.isdigit()])


class Email(str):
    # apenas para formatar email para lower case com o new
    def __new__(cls, value: str) -> Email | None:  # type: ignore[misc]
        if isinstance(value, str):
            return super().__new__(cls, value.lower())
        return None
