from fastapi import APIRouter, Depends, Path
from database.collections import get_category_collection
from models.categoryModel import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    GetAllCategoriesResponseSchema,
)
from controllers.categoryController import (
    createCategoryController,
    getAllCategoriesController,
    getCategoryController,
    getCategoryBySlugController,
    updateCategoryController,
    deleteCategoryController,
)

category = APIRouter()


@category.post('/', response_model=CategoryResponseSchema)
async def create_category(payload: CategoryCreateSchema, categoryEntity=Depends(get_category_collection)):
    return await createCategoryController(payload, categoryEntity)


@category.get('/', response_model=GetAllCategoriesResponseSchema)
async def list_categories(categoryEntity=Depends(get_category_collection)):
    return await getAllCategoriesController(categoryEntity)


@category.get('/{category_id}', response_model=CategoryResponseSchema)
async def get_category(category_id: str = Path(...), categoryEntity=Depends(get_category_collection)):
    return await getCategoryController(category_id, categoryEntity)


@category.get('/slug/{slug}', response_model=CategoryResponseSchema)
async def get_category_by_slug(slug: str = Path(...), categoryEntity=Depends(get_category_collection)):
    return await getCategoryBySlugController(slug, categoryEntity)


@category.put('/{category_id}', response_model=CategoryResponseSchema)
async def update_category(category_id: str, payload: CategoryCreateSchema, categoryEntity=Depends(get_category_collection)):
    return await updateCategoryController(category_id, payload, categoryEntity)


@category.delete('/{category_id}')
async def delete_category(category_id: str, categoryEntity=Depends(get_category_collection)):
    return await deleteCategoryController(category_id, categoryEntity)
# định nghĩa đống api