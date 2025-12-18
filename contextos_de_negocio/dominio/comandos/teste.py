from dataclasses import dataclass

from libs.ddd.barramento import Comando


@dataclass
class ComandoTeste(Comando):
    mensagem: str
