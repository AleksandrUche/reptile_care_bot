from aiogram.fsm.state import State, StatesGroup


class SearchTimeZoneByCityFSM(StatesGroup):
    city = State()