from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from config.config import CHANNEL_ID
from keyboards.inline import get_main_menu
from utils.logger import logger, log_to_db

router = Router()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запустил бота с помощью команды /start")
    try:
        # Проверяем, подписан ли пользователь на канал
        member = await message.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await message.answer("Добро пожаловать в НутриЛайф! Вы подписаны на наш канал. Выберите действие ниже:",
                                 reply_markup=get_main_menu())
            logger.info(f"Пользователь {user_id} успешно прошел проверку подписки")
        else:
            await message.answer("Привет! Чтобы пользоваться ботом, подпишитесь на наш канал: [НутриЛайф](https://t.me/your_channel_link)",
                                 parse_mode="Markdown")
            logger.warning(f"Пользователь {user_id} не подписан на канал")
    except Exception as e:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка при проверке подписки для пользователя {user_id}: {str(e)}")
        await log_to_db("ERROR", f"Ошибка при проверке подписки: {str(e)}", user_id)