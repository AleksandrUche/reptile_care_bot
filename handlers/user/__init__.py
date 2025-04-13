from aiogram import Router

from .user_handler import router
from .company_handler import router as user_company_router

user_router = Router()

user_router.include_router(router)
user_router.include_router(user_company_router)