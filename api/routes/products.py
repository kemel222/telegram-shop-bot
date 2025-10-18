from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.product_service import ProductService
from database.models import User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class ProductVariantResponse(BaseModel):
    id: int
    name: str
    price: Optional[float]
    quantity: int
    is_available: bool
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    quantity: int
    is_available: bool
    has_variants: bool
    is_favorite: bool = False
    variants: List[ProductVariantResponse] = []
    
    class Config:
        from_attributes = True


@router.get("/public", response_model=List[ProductResponse])
async def get_public_products(session: AsyncSession = Depends(get_db)):
    """Получить все товары (публичный доступ)"""
    products = await ProductService.get_all_products(session)
    
    products_response = []
    for product in products:
        variants = await ProductService.get_product_variants(session, product.id)
        
        product_dict = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": product.quantity,
            "is_available": product.is_available,
            "has_variants": product.has_variants,
            "is_favorite": False,  # Для публичного доступа всегда False
            "variants": variants
        }
        products_response.append(product_dict)
    
    return products_response


@router.get("", response_model=List[ProductResponse])
async def get_all_products(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить все товары"""
    products = await ProductService.get_all_products(session)
    
    products_response = []
    for product in products:
        is_favorite = await ProductService.is_in_favorites(session, user.id, product.id)
        variants = await ProductService.get_product_variants(session, product.id)
        
        product_dict = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": product.quantity,
            "is_available": product.is_available,
            "has_variants": product.has_variants,
            "is_favorite": is_favorite,
            "variants": variants
        }
        products_response.append(product_dict)
    
    return products_response


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(session: AsyncSession = Depends(get_db)):
    """Получить все категории"""
    categories = await ProductService.get_all_categories(session)
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, session: AsyncSession = Depends(get_db)):
    """Получить категорию по ID"""
    category = await ProductService.get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/categories/{category_id}/products", response_model=List[ProductResponse])
async def get_category_products(
    category_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить товары категории"""
    products = await ProductService.get_products_by_category(session, category_id)
    
    # Проверяем, какие товары в избранном и загружаем варианты
    products_response = []
    for product in products:
        is_favorite = await ProductService.is_in_favorites(session, user.id, product.id)
        variants = await ProductService.get_product_variants(session, product.id)
        
        product_dict = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": product.quantity,
            "is_available": product.is_available,
            "has_variants": product.has_variants,
            "is_favorite": is_favorite,
            "variants": variants
        }
        products_response.append(product_dict)
    
    return products_response


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить товар по ID"""
    product = await ProductService.get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    is_favorite = await ProductService.is_in_favorites(session, user.id, product.id)
    variants = await ProductService.get_product_variants(session, product.id)
    
    return {
        "id": product.id,
        "category_id": product.category_id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": product.image_url,
        "quantity": product.quantity,
        "is_available": product.is_available,
        "has_variants": product.has_variants,
        "is_favorite": is_favorite,
        "variants": variants
    }


@router.get("/search/{query}")
async def search_products(
    query: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Поиск товаров по названию"""
    products = await ProductService.search_products(session, query)
    
    products_response = []
    for product in products:
        is_favorite = await ProductService.is_in_favorites(session, user.id, product.id)
        variants = await ProductService.get_product_variants(session, product.id)
        
        product_dict = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": product.quantity,
            "is_available": product.is_available,
            "has_variants": product.has_variants,
            "is_favorite": is_favorite,
            "variants": variants
        }
        products_response.append(product_dict)
    
    return products_response


@router.post("/{product_id}/favorite")
async def add_to_favorites(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Добавить товар в избранное"""
    success = await ProductService.add_to_favorites(session, user.id, product_id)
    if not success:
        raise HTTPException(status_code=400, detail="Already in favorites or product not found")
    return {"message": "Added to favorites"}


@router.delete("/{product_id}/favorite")
async def remove_from_favorites(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Удалить товар из избранного"""
    success = await ProductService.remove_from_favorites(session, user.id, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not in favorites")
    return {"message": "Removed from favorites"}


@router.get("/favorites/list")
async def get_favorites(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить избранные товары"""
    products = await ProductService.get_user_favorites(session, user.id)
    
    products_response = []
    for product in products:
        variants = await ProductService.get_product_variants(session, product.id)
        
        product_dict = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": product.quantity,
            "is_available": product.is_available,
            "has_variants": product.has_variants,
            "is_favorite": True,
            "variants": variants
        }
        products_response.append(product_dict)
    
    return products_response

