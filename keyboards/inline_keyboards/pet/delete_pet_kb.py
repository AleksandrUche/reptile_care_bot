from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import ChoiceDeletePet


async def get_delete_pet_inline_kb(pet_id: int, pet_name: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ ДА",
        callback_data=ChoiceDeletePet(
            action="delete", pet_id=pet_id, pet_name=pet_name
        ).pack(),
    )
    builder.button(
        text="❌ НЕТ",
        callback_data=ChoiceDeletePet(
            action="cancel", pet_id=pet_id, pet_name=pet_name
        ).pack(),
    )
    builder.adjust(2)
    return builder.as_markup()
