from aiogram.fsm.state import State, StatesGroup


class PetAddFSM(StatesGroup):
    pet_name = State()


class PetIdFSM(StatesGroup):
    """Для добавления поля id питомца"""
    pet_id = State()


class PetEditNameFSM(PetIdFSM):
    """Имя питомца"""
    pet_name = State()


class PetEditMorphFSM(PetIdFSM):
    """Морфа питомца"""
    pet_morph = State()


class PetEditViewFSM(PetIdFSM):
    """Вид питомца"""
    pet_view = State()


class PetEditGenderFSM(PetIdFSM):
    """Пол питомца"""
    pet_gender = State()


class PetEditLengthFSM(PetIdFSM):
    """Длина питомца"""
    pet_length = State()


class PetEditMoltingFSM(PetIdFSM):
    """Линька питомца"""
    pet_ = State()


class PetEditBirthFSM(PetIdFSM):
    """Дата рождения"""
    pet_birth = State()


class PetEditPurchaseFSM(PetIdFSM):
    """Дата приобретения"""
    pet_purchase = State()


class PetDeliteFSM(PetIdFSM):
    """Удаление питомца"""
    ...
