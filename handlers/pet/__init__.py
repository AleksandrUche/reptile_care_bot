from aiogram import Router

from .add_pet import router as add_pet_router
from .adding_events import router as adding_events_router
from .all_pets import router as all_pets_router
from .delete_pet import router as delete_pet_router
from .detail_pet import router as detail_pet_router
from .edit_pet import router as edit_pet_router
from .feeding import router as feeding_router
from .feeding_schedule import router as feeding_shedule_router

pet_router = Router()

pet_router.include_router(add_pet_router)
pet_router.include_router(adding_events_router)
pet_router.include_router(all_pets_router)
pet_router.include_router(delete_pet_router)
pet_router.include_router(detail_pet_router)
pet_router.include_router(edit_pet_router)
pet_router.include_router(feeding_router)
pet_router.include_router(feeding_shedule_router)
