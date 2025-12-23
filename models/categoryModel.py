
from typing import List
from pydantic import BaseModel, Field

class CategoryCreateSchema(BaseModel):
	name: str = Field(..., description="Category name")

	class Config:
		json_schema_extra = {
			"example": {
				"name": "Áo Thun"
			}
		}

class CategoryDataResponseBody(BaseModel):
	id: str = Field(...)
	name: str = Field(...)
	slug: str = Field(...)

class CategoryResponseSchema(BaseModel):
	success: bool
	message: str
	data: CategoryDataResponseBody

class GetAllCategoriesResponseSchema(BaseModel):
	success: bool
	message: str
	data: List[CategoryDataResponseBody]

