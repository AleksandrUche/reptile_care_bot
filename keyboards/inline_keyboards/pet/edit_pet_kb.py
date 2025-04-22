from aiogram.utils.keyboard import InlineKeyboardBuilder

from enums.pets_enum import GenderRole
from factory.callback_factory.pet_factory import (
    EditPetCallback,
    GenderSelectionCallback,
    PetsCallback,
)


async def get_edit_pet_inline_kb(pet_id: int, company_id: int, group_id: int):
    """Клавиатура для отображения инлайн меню редактирования питомца"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='✏ Имя', callback_data=EditPetCallback(field='name', **data).pack()
    )
    builder.button(
        text='✏ Морфу', callback_data=EditPetCallback(field='morph', **data).pack()
    )
    builder.button(
        text='✏ Вид', callback_data=EditPetCallback(field='view', **data).pack()
    )
    builder.button(
        text='✏ Пол', callback_data=EditPetCallback(field='gender', **data).pack()
    )
    builder.button(
        text='✏ Дата рождения',
        callback_data=EditPetCallback(field='birth', **data).pack(),
    )
    builder.button(
        text='✏ Дата приобретения',
        callback_data=EditPetCallback(field='purchase', **data).pack(),
    )
    builder.button(
        text='⬅ Назад',
        callback_data=EditPetCallback(field='back_interaction_pet', **data).pack(),
    )
    builder.adjust(2)  # По 2 кнопки в строке
    return builder.as_markup()


async def get_gender_select_pet_inline_kb(pet_id: int, company_id: int, group_id: int):
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='♂ Мальчик',
        callback_data=GenderSelectionCallback(action=GenderRole.BOY, **data).pack(),
    )
    builder.button(
        text='♀ Девочка',
        callback_data=GenderSelectionCallback(action=GenderRole.GIRL, **data).pack(),
    )
    builder.button(
        text='🤷‍♂️ Не определен',
        callback_data=GenderSelectionCallback(
            action=GenderRole.NOT_DEFINED, **data
        ).pack(),
    )
    builder.button(text='Назад', callback_data=PetsCallback(**data).pack())
    builder.adjust(2)
    return builder.as_markup()
