from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_contact_choice, get_cancel_keyboard
from database.db import save_contact
from utils.logger import logger

router = Router()

# Определение состояний для контактов
class ContactStates(StatesGroup):
    NAME = State()
    CONTACT_INFO = State()

# Обработчик выбора "Записаться на консультацию"
@router.callback_query(F.data == "contact")
async def start_contact(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} начал процесс связи")
    await callback_query.message.edit_text("Оставьте Ваши данные и мы свяжемся с Вами?", reply_markup=get_contact_choice())
    await callback_query.answer()

# Обработчик выбора "Да, перезвоните"
@router.callback_query(F.data == "contact_yes")
async def process_contact_yes(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} запросил обратный звонок")
    await state.update_data(is_callback=True)
    await callback_query.message.edit_text("Введите ваше имя:", reply_markup=get_cancel_keyboard())
    await state.set_state(ContactStates.NAME)
    await callback_query.answer()

# Обработчик ввода имени
@router.callback_query(ContactStates.NAME, F.data == "cancel")
async def cancel_contact(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил ввод контакта")
    await state.clear()
    await callback_query.message.edit_text("Ввод контакта отменен.", reply_markup=get_main_menu())
    await callback_query.answer()

@router.message(ContactStates.NAME)
async def process_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text
    logger.info(f"Пользователь {user_id} ввел имя: {name}")
    await state.update_data(name=name)
    await message.answer("Введите контактный номер телефона или email:", reply_markup=get_cancel_keyboard())
    await state.set_state(ContactStates.CONTACT_INFO)

# Обработчик ввода контактной информации
@router.callback_query(ContactStates.CONTACT_INFO, F.data == "cancel")
async def cancel_contact_info(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} отменил ввод контактной информации")
    await state.clear()
    await callback_query.message.edit_text("Ввод контакта отменен.", reply_markup=get_main_menu())
    await callback_query.answer()

@router.message(ContactStates.CONTACT_INFO)
async def process_contact_info(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contact_info = message.text
    data = await state.get_data()
    name = data.get("name")
    is_callback = data.get("is_callback", False)
    await save_contact(user_id, name, contact_info)
    if is_callback:
        await message.answer(f"Спасибо за обращение, {name}! Мы свяжемся с Вами по {contact_info} 📞", reply_markup=get_main_menu())
        logger.info(f"Пользователь {user_id} оставил заявку на обратный звонок: {contact_info}")
    await state.clear()