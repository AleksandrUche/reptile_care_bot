from aiogram import Router

from .other_handlers import router

other_router = Router()

other_router.include_router(router)
