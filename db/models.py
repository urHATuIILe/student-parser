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
    phone: Mapped[str | None] = mapped_column(String(17), nullable=True)
    
    
class VkLead(Base):

    __tablename__ = "vk_leads"
    __table_args__ = (
        UniqueConstraint("post_id", "group_id", "comment_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    comment_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    author_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    author_screen_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 'post' | 'comment'
    is_posted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
