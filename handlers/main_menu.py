from aiogram import Router
from aiogram import types
from aiogram.types import CallbackQuery
from keyboards.inline import get_main_menu, get_diagnostics_modules

router = Router()

# Обработчик возврата в главное меню
@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы вернулись в главное меню:", reply_markup=get_main_menu())
    await callback_query.answer()

# Обработчик выбора "Диагностика"
@router.callback_query(lambda c: c.data == "diagnostics")
async def process_diagnostics(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Выберите модуль для диагностики:", reply_markup=get_diagnostics_modules())
    await callback_query.answer()