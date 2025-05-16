from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from config.config import CHANNEL_ID
from keyboards.inline import get_main_menu

router = Router()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    try:
        # Проверяем, подписан ли пользователь на канал
        member = await message.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await message.answer("Добро пожаловать в НутриЛайф! Вы подписаны на наш канал. Выберите действие ниже:",
                                 reply_markup=get_main_menu())
        else:
            await message.answer("Привет! Чтобы пользоваться ботом, подпишитесь на наш канал: [НутриЛайф](https://t.me/your_channel_link)",
                                 parse_mode="Markdown")
    except Exception as e:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        print(f"Ошибка при проверке подписки: {e}")