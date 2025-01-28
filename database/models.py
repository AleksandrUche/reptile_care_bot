from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class UserOrm(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    # связь к группам
