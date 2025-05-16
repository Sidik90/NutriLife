from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu, get_contact_choice
from keyboards.reply import get_cancel_keyboard
from database.db import save_contact
from config.config import ADMIN_ID

router = Router()

# Определение состояний для обратной связи
class ContactStates(StatesGroup):
    NAME = State()
    CONTACT_INFO = State()

# Обработчик выбора "Связаться с нами"
@router.callback_query(lambda c: c.data == "contact")
async def start_contact(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Хотите, чтобы вам перезвонили?", reply_markup=get_contact_choice())
    await callback_query.answer()

# Обработчик выбора "Нет, просто контакт"
@router.callback_query(lambda c: c.data == "contact_no")
async def process_contact_no(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Свяжитесь с нами: [Контакт](https://t.me/your_contact_link)", parse_mode="Markdown", reply_markup=get_main_menu())
    await callback_query.answer()

# Обработчик выбора "Да, перезвоните"
@router.callback_query(lambda c: c.data == "contact_yes")
async def process_contact_yes(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ваше имя:", reply_markup=get_cancel_keyboard())
    await state.set_state(ContactStates.NAME)
    await callback_query.message.delete()
    await callback_query.answer()

# Обработчик ввода имени
@router.message(ContactStates.NAME, F.text == ["Отмена"])
async def cancel_contact(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Запрос отменен.", reply_markup=get_main_menu())

@router.message(ContactStates.NAME)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона или email:", reply_markup=get_cancel_keyboard())
    await state.set_state(ContactStates.CONTACT_INFO)

# Обработчик ввода контактной информации
@router.message(ContactStates.CONTACT_INFO, F.text == ["Отмена"])
async def cancel_contact_info(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Запрос отменен.", reply_markup=get_main_menu())

@router.message(ContactStates.CONTACT_INFO)
async def process_contact_info(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data["name"]
    contact_info = message.text
    user_id = message.from_user.id
    # Сохраняем данные в базу
    await save_contact(user_id, name, contact_info)
    # Отправляем уведомление администратору
    await message.bot.send_message(chat_id=ADMIN_ID, text=f"Новая заявка на звонок:\nИмя: {name}\nКонтакт: {contact_info}\nID: {user_id}")
    await message.answer("Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=get_main_menu())
    await state.clear()