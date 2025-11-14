from sqlalchemy import ForeignKey

from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Text, DateTime
from datetime import datetime
from app.models import User

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    comment: Mapped[str | None] = mapped_column(Text)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    grade: Mapped[int] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship(
        back_populates="reviews",
    )
    product: Mapped["Product"] = relationship(
        back_populates="reviews",
    )

