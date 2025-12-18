from dataclasses import dataclass
from uuid import UUID

from libs.ddd.barramento import Evento


@dataclass
class EmpresaCriada(Evento):
    id: UUID


@dataclass
class EmpresaAtualizada(Evento):
    id: UUID


@dataclass
class EmpresaRemovida(Evento):
    id: UUID
