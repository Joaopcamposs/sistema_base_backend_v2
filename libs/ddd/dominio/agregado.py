from dataclasses import dataclass, field

from libs.ddd.barramento import Evento
from libs.ddd.dominio.entidades import CamposBase
from libs.utils.tipos_basicos import TipoDeOperacao


@dataclass(kw_only=True)
class Agregado(CamposBase):
    eventos: list[Evento] = field(default_factory=list)
    _tipo_de_operacao: TipoDeOperacao | None = None
    _usa_soft_delete: bool = True

    def add_event(self, event: Evento) -> None:
        self.eventos.append(event)
