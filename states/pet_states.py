from aiogram.fsm.state import State, StatesGroup


class AddPetFSM(StatesGroup):
    pet_name = State()
