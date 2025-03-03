from aiogram.fsm.state import State, StatesGroup


class PetAddFSM(StatesGroup):
    pet_name = State()


class PetIdFSM(StatesGroup):
    """Для добавления поля id питомца"""
    pet_id = State()


class PetEditBaseFSM(PetIdFSM):
    """Базовый для редактирования питомцев"""
    company_id = State()
    group_id = State()


class PetEditNameFSM(PetEditBaseFSM):
    """Имя питомца"""
    pet_name = State()


class PetEditMorphFSM(PetEditBaseFSM):
    """Морфа питомца"""
    pet_morph = State()


class PetEditViewFSM(PetEditBaseFSM):
    """Вид питомца"""
    pet_view = State()


class PetEditLengthFSM(PetEditBaseFSM):
    """Длина питомца"""
    pet_length = State()


class PetEditMoltingFSM(PetEditBaseFSM):
    """Линька питомца"""
    pet_ = State()


class PetEditBirthFSM(PetEditBaseFSM):
    """Дата рождения"""
    pet_birth = State()


class PetEditPurchaseFSM(PetEditBaseFSM):
    """Дата приобретения"""
    pet_purchase = State()
