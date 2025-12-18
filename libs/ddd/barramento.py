from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any

CAMPOS_SENSIVEIS = frozenset({"senha", "token"})


@dataclass
class BaseComandoOuEvento(ABC):
    """Classe base para Comandos e Eventos com censura de campos sensíveis."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if "__repr__" in cls.__dict__:
            cls.__repr__ = BaseComandoOuEvento.__repr__
        if "__str__" in cls.__dict__:
            cls.__str__ = BaseComandoOuEvento.__str__
        return super().__new__(cls)

    def __repr__(self) -> str:
        dados = asdict(self)
        for campo in CAMPOS_SENSIVEIS:
            if campo in dados:
                dados[campo] = "***"
        dados_str = ", ".join([f"{k}={v!r}" for k, v in dados.items()])
        return f"{self.__class__.__name__}({dados_str})"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Comando(BaseComandoOuEvento):
    """Classe base para todos os comandos do sistema."""

    pass


@dataclass(kw_only=True)
class Evento(BaseComandoOuEvento):
    """
    Classe base para todos os eventos do sistema.

    Attributes:
        executar_de_forma_assincrona: Se True, o evento será processado de forma assíncrona.
    """

    executar_de_forma_assincrona: bool = False


Mensagem = Comando | Evento
