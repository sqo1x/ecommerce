from urllib.request import ProxyDigestAuthHandler

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.db_depends import get_db
from app.schemas import Product as ProductSchema, ProductCreate
from app.models import Category as CategoryModel, Product as ProductModel



# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/",response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active==True)
    result = db.scalars(stmt).all()
    return result

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> ProductSchema:
    """
    Создаёт новый товар.
    """
    category = db.get(CategoryModel, product.category_id)
    if category is None or category.is_active == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    category_result = db.scalar(category_stmt)
    if category_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
    product_stmt = select(ProductModel).where(ProductModel.is_active==True,
                                              ProductModel.category_id==category_id)
    product_result = db.scalars(product_stmt).all()
    return product_result



@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    product_stmt = select(ProductModel).where(ProductModel.is_active==True,
                                      ProductModel.id == product_id)
    product_result = db.scalar(product_stmt)
    if product_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_result


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    Обновляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.is_active==True,
                                      ProductModel.id == product_id)
    product_result = db.scalar(stmt)
    if product_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    stmt = select(CategoryModel).where(CategoryModel.is_active==True,
                                       CategoryModel.id == product.category_id)

    category_result = db.scalar(stmt)
    if category_result is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found")

    db.execute(
        update(ProductModel)
        .where(ProductModel.id==product_id)
        .values(**product.model_dump())
    )
    db.commit()
    db.refresh(product_result)
    return product_result

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.is_active==True,)
    product_result = db.scalar(stmt)
    if product_result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.execute(update(ProductModel).where(ProductModel.id==product_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}