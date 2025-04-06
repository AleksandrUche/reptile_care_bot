from aiogram import Router
from .pet import pet_router

main_router = Router()

main_router.include_router(pet_router)
