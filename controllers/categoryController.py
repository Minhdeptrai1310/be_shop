from database.entity.categoryEntity import Category
from fastapi import HTTPException, status
from util.ResponseSchema import successResponse, errorResponse



async def createCategoryController(payload, categoryEntity):
    try:
        new_cat = await Category.create_category(
            name=payload.name,
            categoryEntity=categoryEntity,
        )
        return successResponse("Category created", new_cat.dict())
    except Exception as ex:
        print("exception under Category create controller:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def getAllCategoriesController(categoryEntity):
    try:
        cats = await Category.find_all_categories(categoryEntity)
        return successResponse("Categories fetched", cats)
    except Exception as ex:
        print("exception under getAllCategories:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def getCategoryController(category_id: str, categoryEntity):
    try:
        cat = await Category.find_one_category_by_id(category_id, categoryEntity)
        return successResponse("Category fetched", cat.dict())
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under getCategory:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def getCategoryBySlugController(slug: str, categoryEntity):
    try:
        cat = await Category.find_one_category_by_slug(slug, categoryEntity)
        return successResponse("Category fetched", cat.dict())
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under getCategoryBySlug:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def updateCategoryController(category_id: str, payload, categoryEntity):
    try:
        await Category.update_category(
            category_id=category_id,
            name=payload.name if hasattr(payload, 'name') else None,
            categoryEntity=categoryEntity,
        )
        return successResponse("Category updated", {"id": category_id})
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under updateCategory:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))


async def deleteCategoryController(category_id: str, categoryEntity):
    try:
        deleted = await Category.delete_category(category_id, categoryEntity)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errorResponse("Category not found"))
        return successResponse("Category deleted", {"id": category_id})
    except HTTPException:
        raise
    except Exception as ex:
        print("exception under deleteCategory:", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=errorResponse("Internal Server Error"))
