from datetime import datetime
from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class CamposBaseDB:
    criado_por: Mapped[UUID | None] = mapped_column(UUID, nullable=True, default=None)
    criado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    ultima_modificacao_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    modificado_por: Mapped[UUID | None] = mapped_column(UUID, nullable=True, default=None)
    deletado_em: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    deletado_por: Mapped[UUID | None] = mapped_column(UUID, nullable=True, default=None)
