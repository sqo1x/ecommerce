from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_db, get_async_db
from app.schemas import Product as ProductSchema, ProductCreate
from app.models import Category as CategoryModel, Product as ProductModel



# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/",response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = await db.scalars(select(ProductModel).where(ProductModel.is_active==True))
    result = stmt.all()
    return result

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новый товар.
    """
    category = await db.scalar(
        select(CategoryModel).where(CategoryModel.id == product.category_id,
                                    CategoryModel.is_active == True)
    )

    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()
    print(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    category_stmt = await db.scalar(select(CategoryModel).where(CategoryModel.id == category_id,
                                                CategoryModel.is_active==True))

    if category_stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
    product_stmt = select(ProductModel).where(ProductModel.is_active==True,
                                              ProductModel.category_id==category_id)
    product_result = await db.scalars(product_stmt)
    products = product_result.all()
    return products



@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product_stmt = await db.scalar(select(ProductModel).where(ProductModel.is_active==True,
                                      ProductModel.id == product_id))

    if product_stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_stmt


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет товар по его ID.
    """
    product_result = await db.scalar(select(ProductModel).where(ProductModel.is_active==True,
                                      ProductModel.id == product_id))
    if product_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    category_result = await db.scalar(select(CategoryModel).where(CategoryModel.is_active==True,
                                       CategoryModel.id == product.category_id))
    if category_result is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id==product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    return product_result

@router.delete("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductSchema)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляет товар по его ID.
    """
    product_result = await db.scalar(select(ProductModel).where(ProductModel.is_active==True,
                                      ProductModel.id == product_id))
    if product_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    await db.execute(update(ProductModel).where(ProductModel.id==product_id).values(is_active=False))
    await db.commit()

    return product_result