from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import PetsCallback


async def get_return_detail_view_pet_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅ Вернуться к питомцу',
        callback_data=PetsCallback(
            pet_id=pet_id, company_id=company_id, group_id=group_id
        ).pack(),
    )
    builder.adjust(1)
    return builder.as_markup()
