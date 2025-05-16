from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu
from keyboards.reply import get_cancel_keyboard

router = Router()

# Определение состояний для расчета БЖУ
class BJUStates(StatesGroup):
    PRODUCT = State()

# База данных продуктов (пример)
BJU_DATABASE = {
    "яблоко": {"b": 0.4, "j": 0.4, "u": 9.8, "kcal": 47},
    "банан": {"b": 1.5, "j": 0.2, "u": 21.8, "kcal": 95},
    "курица": {"b": 23.1, "j": 1.9, "u": 0, "kcal": 110}
}

# Обработчик выбора "Расчет БЖУ"
@router.callback_query(lambda c: c.data == "bju_calc")
async def start_bju_calc(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название продукта (или 'AI' для запроса к ИИ):", reply_markup=get_cancel_keyboard())
    await state.set_state(BJUStates.PRODUCT)
    await callback_query.message.delete()
    await callback_query.answer()

# Обработчик ввода продукта
@router.message(BJUStates.PRODUCT, F.text == ["Отмена"])
async def cancel_bju(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Расчет отменен.", reply_markup=get_main_menu())

@router.message(BJUStates.PRODUCT, F.text == ["AI", "ai", "Ai"])
async def process_ai_request(message: Message, state: FSMContext):
    await message.answer("Функция 'Спроси у AI' находится в разработке. Скоро будет доступна!", reply_markup=get_main_menu())
    await state.clear()

@router.message(BJUStates.PRODUCT)
async def process_product(message: Message, state: FSMContext):
    product = message.text.lower()
    if product in BJU_DATABASE:
        data = BJU_DATABASE[product]
        result_text = f"Продукт: {product.capitalize()}\nБелки: {data['b']} г\nЖиры: {data['j']} г\nУглеводы: {data['u']} г\nКалории: {data['kcal']} ккал"
    else:
        result_text = "Продукт не найден в базе данных. Попробуйте другой."
    await message.answer(result_text, reply_markup=get_main_menu())
    await state.clear()