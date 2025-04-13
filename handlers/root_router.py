from aiogram import Router
from .pet import pet_router
from .user import user_router
from .other import other_router

main_router = Router()

main_router.include_router(pet_router)
main_router.include_router(user_router)
main_router.include_router(other_router)
