from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import (
    scheduleFeedingsCallback,
    EditPetCallback,
    DeletePetCallback,
    HistoryPetCallback,
)


async def get_interaction_pet_inline_kb(pet_id: int, company_id: int, group_id: int):
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='📝 График кормлений',
        callback_data=scheduleFeedingsCallback(action='menu', **data).pack(),
    )
    builder.button(
        text='🍼 Покормить',
        callback_data=EditPetCallback(field='add_feeding', **data).pack(),
    )
    builder.button(
        text='⚖️ Взвесить', callback_data=EditPetCallback(field='weight', **data).pack()
    )
    builder.button(
        text='📐 Измерить', callback_data=EditPetCallback(field='length', **data).pack()
    )
    builder.button(
        text='🐍 Добавить линьку',
        callback_data=EditPetCallback(field='molting', **data).pack(),
    )
    builder.button(
        text='✏ Редактировать',
        callback_data=EditPetCallback(field='all_editing_tools', **data).pack(),
    )
    builder.button(
        text='📜 История',
        callback_data=HistoryPetCallback(action='menu', **data).pack(),
    )
    builder.button(
        text='❌ Удалить питомца ',
        callback_data=DeletePetCallback(action='menu', **data).pack(),
    )
    builder.button(text='⬅ Назад', callback_data='back_to_all_pets')
    builder.adjust(2)  # По 2 кнопки в строке
    return builder.as_markup()
