from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_cancel_keyboard
from database.db import get_bju_from_local_db
from utils.logger import logger

router = Router()

# Определение состояний для расчета БЖУ
class BJUStates(StatesGroup):
    PRODUCT = State()

# Обработчик выбора "Расчет БЖУ"
@router.callback_query(F.data == "bju_calc")
async def start_bju_calc(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} начал расчет БЖУ")
    await callback_query.message.edit_text("Введите название продукта (или 'AI' для запроса к ИИ):", reply_markup=get_cancel_keyboard())
    await state.set_state(BJUStates.PRODUCT)
    await callback_query.answer()

# Обработчик ввода продукта
@router.callback_query(BJUStates.PRODUCT, F.data == "cancel")
async def cancel_bju(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил расчет БЖУ")
    await state.clear()
    await callback_query.message.edit_text("Расчет отменен.", reply_markup=get_main_menu())
    await callback_query.answer()

@router.message(BJUStates.PRODUCT, F.text == ["AI", "ai", "Ai"])
async def process_ai_request(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил функцию AI для БЖУ")
    await message.answer("Функция 'Спроси у AI' находится в разработке. Скоро будет доступна! 🚧", reply_markup=get_main_menu())
    await state.clear()

@router.message(BJUStates.PRODUCT)
async def process_product(message: Message, state: FSMContext):
    user_id = message.from_user.id
    product = message.text.lower()
    logger.info(f"Пользователь {user_id} запросил БЖУ для продукта: {product}")
    # Пробуем получить данные из локальной базы данных
    data = await get_bju_from_local_db(product)
    if data:
        result_text = f"Продукт: {product.capitalize()}\nБелки: {data['b']} г\nЖиры: {data['j']} г\nУглеводы: {data['u']} г\nКалории: {data['kcal']} ккал"
        logger.info(f"Пользователь {user_id} получил данные о продукте {product}")
    else:
        result_text = "Продукт не найден в базе данных. Попробуйте другой. 🔍"
        logger.warning(f"Продукт {product} не найден для пользователя {user_id}")
    await message.answer(result_text, reply_markup=get_main_menu())
    await state.clear()