from aiogram.filters.callback_data import CallbackData


class CompanyCallbackFactory(CallbackData, prefix='company'):
    company_id: int
    user_id: int
