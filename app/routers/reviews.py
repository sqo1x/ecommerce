from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.auth import get_current_user, get_current_buyer, check_admin
from app.models import Review as ReviewModel
from app.models import User as UserModel, Product as ProductModel
from app.utils import update_avg_rating

router = APIRouter(tags=["reviews"],
                   prefix="/reviews")

@router.get("/", response_model=list[ReviewSchema])
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Эндпоинт для получения всех отзывов.
    """
    stmt = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))

    return stmt.all()

@router.post("/", response_model=ReviewSchema)

async def create_review(
        review: ReviewCreate,
        user: UserModel = Depends(get_current_buyer),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Создание нового отзыва.
    Доступно только для пользователей с ролью "buyer".
    """
    product = await db.scalar(select(ProductModel).where(ProductModel.id ==  review.product_id,
                                                       ProductModel.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    new_review = ReviewModel(**review.model_dump(), user_id = user.id)
    db.add(new_review)
    await update_avg_rating(review.product_id, db)
    await db.commit()
    await db.refresh(new_review)

    return new_review

@router.delete("/{review_id}")
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db), admin: UserModel = Depends(check_admin)):
    """
    Удаляет отзыв по его ID.
    """
    db_review = await db.scalar(select(ReviewModel).where(ReviewModel.id == review_id,
                                                     ReviewModel.is_active == True))

    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    db_review.is_active = False
    await update_avg_rating(db_review.product_id, db)
    await db.commit()
    await db.refresh(db_review)

    return {"message": "Review deleted"}