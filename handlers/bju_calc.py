from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_cancel_keyboard
from database.db import get_bju_from_local_db, recalculate_bju
from utils.logger import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


# Определение состояний для расчета БЖУ
class BJUStates(StatesGroup):
    PRODUCT = State()
    WEIGHT = State()
    SELECT_PRODUCT = State()


# Обработчик выбора "Расчет БЖУ"
@router.callback_query(F.data == "bju_calc")
async def start_bju_calc(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} начал расчет БЖУ")
    await callback_query.message.edit_text(
        "Введите название продукта (или 'AI' для запроса к ИИ):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(BJUStates.PRODUCT)
    await callback_query.answer()


# Обработчик отмены
@router.callback_query(F.data == "cancel")
async def cancel_bju(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил расчет БЖУ")
    await state.clear()
    await callback_query.message.edit_text(
        "Расчет отменен.", reply_markup=get_main_menu()
    )
    await callback_query.answer()


# Обработчик запроса AI
@router.message(BJUStates.PRODUCT, F.text.lower().in_(["ai", "ai", "ai"]))
async def process_ai_request(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил функцию AI для БЖУ")
    await message.answer(
        "Функция 'Спроси у AI' находится в разработке. Скоро будет доступна! 🚧",
        reply_markup=get_main_menu(),
    )
    await state.clear()


# Обработчик ввода продукта
@router.message(BJUStates.PRODUCT)
async def process_product(message: Message, state: FSMContext):
    user_id = message.from_user.id
    product = message.text.lower()
    logger.info(f"Пользователь {user_id} запросил БЖУ для продукта: {product}")
    # Пробуем получить данные из локальной базы данных
    data_list = await get_bju_from_local_db(product)
    if data_list:
        if len(data_list) == 1:
            # Если найден только один продукт, запрашиваем вес
            await state.update_data(product_data=data_list[0])
            await message.answer(
                f"Продукт: {data_list[0]['name'].capitalize()}\nВведите вес в граммах (по умолчанию 100 г):",
                reply_markup=get_cancel_keyboard(),
            )
            await state.set_state(BJUStates.WEIGHT)
        else:
            # Если найдено несколько продуктов, предлагаем выбрать
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            for idx, product_data in enumerate(data_list):
                keyboard.inline_keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=product_data["name"].capitalize(),
                            callback_data=f"select_product_{idx}",
                        )
                    ]
                )
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
            )
            await state.update_data(product_list=data_list)
            await message.answer(
                "Найдено несколько продуктов. Выберите один:", reply_markup=keyboard
            )
            await state.set_state(BJUStates.SELECT_PRODUCT)
    else:
        result_text = "Продукт не найден в базе данных. Попробуйте другой. 🔍"
        logger.warning(f"Продукт {product} не найден для пользователя {user_id}")
        await message.answer(result_text, reply_markup=get_main_menu())
        await state.clear()


# Обработчик выбора продукта из списка
@router.callback_query(BJUStates.SELECT_PRODUCT, F.data.startswith("select_product_"))
async def select_product(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    idx = int(callback_query.data.split("_")[-1])
    user_data = await state.get_data()
    product_data = user_data.get("product_list", [])[idx]
    logger.info(f"Пользователь {user_id} выбрал продукт: {product_data['name']}")
    await state.update_data(product_data=product_data)
    await callback_query.message.edit_text(
        f"Продукт: {product_data['name'].capitalize()}\nВведите вес в граммах (по умолчанию 100 г):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(BJUStates.WEIGHT)
    await callback_query.answer()


# Обработчик ввода веса
@router.message(BJUStates.WEIGHT)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    product_data = user_data.get("product_data", {})
    try:
        weight = float(message.text)
        if weight <= 0:
            await message.answer(
                "Вес должен быть больше 0. Попробуйте снова:",
                reply_markup=get_cancel_keyboard(),
            )
            return
        recalculated_data = recalculate_bju(product_data, weight)
        result_text = (
            f"Продукт: {recalculated_data['name'].capitalize()}\n"
            f"Вес: {recalculated_data['weight']} г\n"
            f"Белки: {recalculated_data['b']} г\n"
            f"Жиры: {recalculated_data['j']} г\n"
            f"Углеводы: {recalculated_data['u']} г\n"
            f"Калории: {recalculated_data['kcal']} ккал"
        )
        logger.info(
            f"Пользователь {user_id} получил данные о продукте {recalculated_data['name']} для веса {weight} г"
        )
    except ValueError:
        recalculated_data = product_data
        result_text = (
            f"Продукт: {recalculated_data['name'].capitalize()}\n"
            f"Вес: {recalculated_data['weight']} г (по умолчанию)\n"
            f"Белки: {recalculated_data['b']} г\n"
            f"Жиры: {recalculated_data['j']} г\n"
            f"Углеводы: {recalculated_data['u']} г\n"
            f"Калории: {recalculated_data['kcal']} ккал"
        )
        logger.info(
            f"Пользователь {user_id} не указал вес, используется стандартный вес для {recalculated_data['name']}"
        )
    await message.answer(result_text, reply_markup=get_main_menu())
    await state.clear()
