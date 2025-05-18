from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import get_main_menu, get_diagnostics_modules
from utils.logger import logger

router = Router()

# Обработчик возврата в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} вернулся в главное меню")
    await callback_query.message.edit_text("Вы вернулись в главное меню:", reply_markup=get_main_menu())
    await callback_query.answer()

# Обработчик выбора "Диагностика"
@router.callback_query(F.data == "diagnostics")
async def process_diagnostics(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} выбрал раздел Диагностика")
    await callback_query.message.edit_text("Выберите тему для диагностики:", reply_markup=get_diagnostics_modules())
    await callback_query.answer()