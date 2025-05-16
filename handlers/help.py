from aiogram import Router
from aiogram import types
from keyboards.inline import get_main_menu

router = Router()

# Обработчик выбора "Помощь"
@router.callback_query(lambda c: c.data == "help")
async def process_help(callback_query: types.CallbackQuery):
    help_text = (
        "📚 **Помощь по боту НутриЛайф**\n\n"
        "Я помогу вам с вопросами нутрициологии и здорового образа жизни. Вот что я умею:\n\n"
        "1. **Диагностика** - пройдите тест по питанию, сну или стрессу.\n"
        "2. **Сыграть в квиз** - проверьте свои знания в игровой форме.\n"
        "3. **Напоминалка** - установите напоминание о важных задачах.\n"
        "4. **Расчет БЖУ** - узнайте содержание белков, жиров и углеводов в продуктах.\n"
        "5. **Связаться с нами** - оставьте заявку на консультацию.\n\n"
        "Команды:\n"
        "- /start - начать работу с ботом.\n\n"
        "Если у вас есть вопросы, выберите 'Связаться с нами'."
    )
    await callback_query.message.edit_text(help_text, parse_mode="Markdown", reply_markup=get_main_menu())
    await callback_query.answer()
