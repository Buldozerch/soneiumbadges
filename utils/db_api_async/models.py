from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text 


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'soneium'

    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    proxy: Mapped[str] = mapped_column(Text, nullable=True, unique=False)
    owlto_bridge: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    owlto_swap: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    quickswap_swap: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    sonex_swap: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    sonus_swap: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    sonus_lock: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)
    untintled_bank: Mapped[int] = mapped_column (nullable=False, unique=False, default=0)

    def __str__(self):
        return f'{self.public_key}'

    def __repr__(self):
        return f'{self.public_key}'
