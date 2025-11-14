from fastapi import Depends
from app.db_depends import get_async_db

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Review, Product
from sqlalchemy import select, func, update

async def update_avg_rating(product_id: int, db: AsyncSession):
    """
    Функция для обновления рейтинга при добавлении/удалении отзыва.
    """
    stmt = await db.scalars(select(Review).where(Review.product_id == product_id,
                                                 Review.is_active == True))
    db_reviews = stmt.all()
    reviews_grade = [review.grade for review in db_reviews]
    avg = sum(reviews_grade) / len(reviews_grade)
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(rating = avg)
    )