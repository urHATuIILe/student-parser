from datetime import datetime
from sqlalchemy import  String, BigInteger, Text, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "telegram_leads"
    __table_args__ = (
        UniqueConstraint("message_id", "chat_id"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[str] = mapped_column(String(15), nullable=False)
    tg_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sender_username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_posted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
