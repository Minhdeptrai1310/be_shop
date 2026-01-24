from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

from auth.authBearer import JWTBearer
from database.entity.userEntity import User
from database.collections import init_db
from middlewares.errorException import custom_exception_handler
from database.entity.categoryEntity import Category
from database.entity.roleEntity import Role
from database.entity.productEntity import Product

from routes.user import user as userRouter
from routes.auth import auth as authRouter
from routes.category import category as categoryRouter
from routes.role import role as roleRouter
from routes.product import product as productRouter
from routes.email import email as emailRouter
from routes.upload import upload as uploadRouter
from routes.cart import cart as cartRouter
from routes.order import order as orderRouter
from util.ResponseSchema import successResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
   return custom_exception_handler(request, exc)


# startup event
@app.on_event("startup")
async def startup_event():
    db = init_db()
    await User.create_indexes(db)
    # create indexes for categories collection as well
    await Category.create_indexes(db)
    # create indexes for roles
    await Role.create_indexes(db)
    # create indexes for products
    await Product.create_indexes(db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # hoặc ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

get_token_header = JWTBearer()
deployedTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.get('/')
async def index():
    return successResponse("Welcome to FastAPI", {
        "deployedTime": deployedTime
    })

app.include_router(authRouter, tags=['auth'], prefix='/auth')
app.include_router(userRouter, tags=['user'], prefix='/users' , dependencies=[Depends(get_token_header)])
app.include_router(categoryRouter, tags=['category'], prefix='/categories')
app.include_router(roleRouter, tags=['role'], prefix='/roles')
app.include_router(productRouter, tags=['product'], prefix='/products')
app.include_router(emailRouter, tags=['email'], prefix='/email')
app.include_router(uploadRouter, tags=['upload'], prefix='/upload')
app.include_router(cartRouter, tags=['cart'], prefix='/cart')
app.include_router(orderRouter, tags=['order'], prefix='/order')
